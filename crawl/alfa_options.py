import pandas as pd
import boto3
import json

from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sql = 'mysql+pymysql'
host = 
port = 3306
db = 
user = 
passwd = 

engine = create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

target = 10

query = f"""select * from
(select a.url, a.name, a.casno, b.shop from 
(select * from portal.alfa_items 
where part = {target}) a
left join portal.portal_item_chemicals b
on a.url = b.url) c
where c.shop is null;"""

with engine.connect() as conn:
    df = pd.read_sql_query(query,conn)

def seleniumWindow(url, headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    options.add_argument('--mute-audio')
    options.add_argument('--window-size=1400,2000')
    options.add_argument('--disable-notifications')
    options.add_argument('--enable-popup-blocking')
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get(url)
    return driver

def parse(url):
    driver = seleniumWindow(url, headless=True)
    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class='x1w6']//div[@class='xx8']/table")))
    html = element.get_attribute('outerHTML')
    df = pd.read_html(html)[0]
    df.columns = pd.read_html(driver.find_element(By.CLASS_NAME,'xxj').get_attribute('outerHTML'))[0].columns
    driver.quit()
    return df

accesskey = 
secretkey = 
bucket_info = 'portal-item-info'

def s3Client():
    return boto3.client('s3',aws_access_key_id=accesskey, aws_secret_access_key=secretkey)

def s3Upload(rst, part, num):
    s3 = s3Client()
    fname = f'alfa_{str(part).zfill(2)}_{str(num).zfill(4)}.json'
    temp = {'values':rst}
    temp = bytes(json.dumps(temp).encode('utf-8'))
    s3.put_object(
            Bucket=bucket_info,
            Key=fname,
            Body=temp)
    s3.close()

s3 = s3Client()
rst = s3.list_objects(Bucket=bucket_info, Prefix=f'alfa_{str(target).zfill(2)}')
keylist = []
for r in rst['Contents']:
    key = r['Key']
    keylist.append(key)

nums = []
for key in keylist:
    nums.append(int(key.split('.')[0].split('_')[-1]))

if len(nums)==0:
    num = 0
else:
    num = max(nums)+1

rst = pd.DataFrame()
j = 0
for idx, row in df.iterrows():
    url = row['url']
    try:
        temp = parse(url)
    except:
        continue
    temp['name'] = row['name']
    temp['url'] = url
    if row['casno'] != '':
        temp['casno'] = row['casno']
    else:
        temp['casno'] = None
    rst = pd.concat([rst,temp])
    j += 1
    if j%30==0:
        print(j)
        rst = rst.to_dict(orient='records')
        s3Upload(rst, target, num)
        num += 1
        del(rst)
        rst = pd.DataFrame()

rst = rst.to_dict(orient='records')
s3Upload(rst, target, num)