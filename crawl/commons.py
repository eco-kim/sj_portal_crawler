import boto3
from sqlalchemy import create_engine, inspect
import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import time

from numpy import random

##mysql
sql = 'mysql+pymysql'
host = 
port = 3306
db = 
user = 
passwd = 

def mysqlEngine():
    return create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

def loadDataType(engine, schema, table):
    insp = inspect(engine)
    columns = insp.get_columns(table, schema)
    dtypes = {}
    for col in columns:
        dtypes[col['name']] = col['type']
    return dtypes

##s3
accesskey = 
secretkey = 
bucket_thumbnail = 'portal-item-thumbnail'
bucket_info = 'portal-item-info'

def s3Client():
    return boto3.client('s3',aws_access_key_id=accesskey, aws_secret_access_key=secretkey)

def s3Upload(rst, category_id, num):
    s3 = s3Client()
    fname = f'category_{str(category_id).zfill(5)}_{str(num).zfill(4)}.json'
    temp = {'category_id':category_id,
            'values':rst}
    temp = bytes(json.dumps(temp).encode('utf-8'))
    s3.put_object(
            Bucket=bucket_info,
            Key=fname,
            Body=temp)
    s3.close()

##beautiful soup
def getSoup(url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url=url, headers=hdr)
    if response.status_code!=200:  
        return response.status_code
    else:
        soup = Soup(response.content.decode('utf8','replace'), 'html.parser')
    return soup

##selenium
def setOptions():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--mute-audio')
    options.add_argument('--window-size=1200,800')
    options.add_argument('--disable-notifications')
    options.add_argument('--enable-popup-blocking')
    return options

options = setOptions()
def seleniumWindow(url):
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.get(url)
    return driver

def goToBottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        scroll_down = 0
        while scroll_down < 10:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            rr = random.rand()/10.
            time.sleep(0.3+rr)
            scroll_down += 1

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break

        last_height = new_height    
