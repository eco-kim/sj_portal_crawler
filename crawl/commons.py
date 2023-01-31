import boto3
from sqlalchemy import create_engine, types as sqltypes
import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd

##mysql
sql = 'mysql+pymysql'
host = 'research-master.cvtkhht2fxds.ap-northeast-2.rds.amazonaws.com'
port = 3306
db = 'ncbi'
user = 'smartjack'
passwd = 'workandplay1!'

def mysqlEngine():
    return create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

##s3
accesskey = 'AKIAJTHZ7J76SPC4AVNQ'
secretkey = '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'
bucket = 'smartjack-master-database'

def s3Client():
    return boto3.client('s3',aws_access_key_id=accesskey, aws_secret_access_key=secretkey)

##beautiful soup
def getSoup(url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url=url, headers=hdr)
    if response.status_code!=200:  
        return response.status_code
    else:
        soup = Soup(response.content.decode('utf8','replace'), 'html.parser')
    return soup

categoryColumns = ['id','title','parent_id','root_id','uri']
categoryDtypes = {'id': sqltypes.INTEGER(),
                'title': sqltypes.VARCHAR(50),
                'parent_id':sqltypes.INTEGER(),
                'root_id':sqltypes.INTEGER(),
                'uri': sqltypes.VARCHAR(100)}