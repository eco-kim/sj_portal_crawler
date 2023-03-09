import pandas as pd
import boto3
from sqlalchemy import create_engine
import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd
import json

target = 10
def getSoup(url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url=url, headers=hdr)
    if response.status_code!=200:  
        return response.status_code
    else:
        soup = Soup(response.content.decode('utf8','replace'), 'html.parser')
    return soup

##s3
accesskey = 
secretkey = 
bucket_thumbnail = 'portal-item-thumbnail'
bucket_info = 'portal-item-info'
s3 = boto3.client('s3',aws_access_key_id=accesskey, aws_secret_access_key=secretkey)

def s3Upload(rst, category_id, num):    
    fname = f'category_{str(category_id).zfill(5)}_{str(num).zfill(4)}.json'
    temp = {'category_id':category_id,
            'values':rst}
    temp = bytes(json.dumps(temp).encode('utf-8'))
    s3.put_object(
            Bucket=bucket_info,
            Key=fname,
            Body=temp)
    s3.close()

s3 = boto3.client('s3',aws_access_key_id=accesskey, aws_secret_access_key=secretkey)
rst = s3.list_objects(Bucket=bucket_info, Prefix='category_')
keylist = []
for r in rst['Contents']:
    key = r['Key']
    key = int(key.split('_')[-1].split('.')[0])
    if key//10 == target:
        keylist.append(key)
finished = (max(keylist)%10 + 1)*1000

sql = 'mysql+pymysql'
host = 
port = 3306
db = 
user = 
passwd = 
engine = create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

with engine.connect() as conn:
    df = pd.read_sql_query(f'select * from portal.cacheby_temp where part={target};', conn)

df = df.iloc[finished:]
df = df.set_index('id')
rst = []
nn = 0
num = target*200
for idx, row in df.iterrows():
    url = row['url']
    soup = getSoup(url)
    if type(soup) == int:
        print(url, soup, 'error')
        continue
    table = soup.find_all('div', {'class':'Table'})
    if not table:
        continue
    table_df = pd.read_html(str(table[0]))[0]
    table_df = table_df['상품 옵션 정보']
    table_df['url'] = url
    table_df['item_id'] = idx

    options = table_df.to_dict(orient='records')
    rst = rst + options
    nn += 1
    if nn%100==0:
        s3Upload(rst,row['category_id'],num)
        num += 1
        del(rst)
        rst = []
        print(f"==={nn}===")

s3Upload(rst,row['category_id'],num)