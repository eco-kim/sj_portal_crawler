import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from commons.mysql import mysqlEngine
from commons.selenium import seleniumWindow
from commons.s3 import *
from commons.config import s3 as s3_config

engine = mysqlEngine()

partition = 10

query = f"""select * from
(select a.url, a.name, a.casno, b.shop from 
(select * from portal.alfa_items 
where part = {partition}) a
left join portal.portal_item_chemicals b
on a.url = b.url) c
where c.shop is null;"""

with engine.connect() as conn:
    df = pd.read_sql_query(query,conn)


def parse(url):
    driver = seleniumWindow(url, headless=True)
    wait = WebDriverWait(driver, 30)
    element = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class='x1w6']//div[@class='xx8']/table")))
    html = element.get_attribute('outerHTML')
    df = pd.read_html(html)[0]
    df.columns = pd.read_html(driver.find_element(By.CLASS_NAME,'xxj').get_attribute('outerHTML'))[0].columns
    driver.quit()
    return df

###기 업로드 된 부분 제외
shop_name = ''
s3 = s3Client()
rst = s3.list_objects(Bucket=s3_config['bucket_info'], Prefix=f'{shop_name}_{str(partition).zfill(2)}')
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

##크롤링 시작
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
        s3Upload(rst, partition, num)
        num += 1
        del(rst)
        rst = pd.DataFrame()

rst = rst.to_dict(orient='records')
s3Upload(rst, partition, num)