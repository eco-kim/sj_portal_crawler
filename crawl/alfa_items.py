import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd
import time

from sqlalchemy import create_engine, inspect

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

sql = 'mysql+pymysql'
host = 
port = 
db = 
user = 
passwd = 

engine = create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

def getSoup(url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url=url, headers=hdr)
    if response.status_code!=200:  
        return response.status_code
    else:
        soup = Soup(response.content.decode('utf8','replace'), 'html.parser')
    return soup

def loadDataType(schema, table):
    columns = insp.get_columns(table, schema)
    dtypes = {}
    for col in columns:
        dtypes[col['name']] = col['type']
    return dtypes

insp = inspect(engine)
dtypes = loadDataType('portal','alfa_items')

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

def pageSelect(driver, i):
    select = Select(driver.find_element(By.ID, 'pt1:soc2::content'))
    select.select_by_index(i)

def nPages(driver):
    l = driver.find_element(By.ID, "pt1:soc2::content").find_elements(By.CSS_SELECTOR, 'option')
    return len(l)

def findItems(soup):
    table = soup.find('div',{'id':'pt1:pgl11'})
    rst = []
    i = 0 
    while True:
        temp = []
        name = table.find('div',{'id':f'pt1:i1:{i}:pgl9'})
        if not name:
            break
        name = name.find('a')
        temp.append(name.text)
        temp.append('https://www.alfa.co.kr'+name['href'])
        cas = table.find('div',{'id':f'pt1:i1:{i}:pgl8'})
        if not cas:
            temp.append(None)
        else:
            temp.append(cas.find('div').text)
        rst.append(temp)
        i += 1
    return rst

errors = []
url = 'https://www.alfa.co.kr/AlfaAesarApp/faces/adf.task-flow?adf.tfId=ProductSearchTF&adf.tfDoc=/WEB-INF/ProductSearchTF.xml&pageName=AfAlphabeticalIndex&_afrLoop=502760592284270&_afrWindowMode=0&_afrWindowId=null'

for j in range(20,26):
    driver = seleniumWindow(url, headless=True)
    driver.implicitly_wait(20)
    wait = WebDriverWait(driver, 10)
    alpha = driver.find_element(By.ID, 'pt1:pgl23').find_elements(By.CSS_SELECTOR, 'span')
    az = alpha[j]
    print('--------')
    print(az.text)
    az.click()
    time.sleep(30)
    try:
        npage = nPages(driver)
    except:
        try:
            driver.quit()
            driver = seleniumWindow(url, headless=True)
            driver.implicitly_wait(20)
            az.click()
            time.sleep(30)
            npage = nPages(driver)
        except:
            continue
        
    print(f"total: {npage} pages")
    rst = []
    for p in range(npage):
        print(f"==={p}===")
        try:
            pageSelect(driver, p)
            time.sleep(20)
            pagesrc = driver.page_source
            soup = Soup(pagesrc, 'html.parser')
            rst = rst + findItems(soup)    
        except:
            try:
                driver.quit()
                driver = seleniumWindow(url, headless=True)
                driver.implicitly_wait(20)
                az.click()
                time.sleep(30)            

                pageSelect(driver, p)
                time.sleep(20)
                pagesrc = driver.page_source
                soup = Soup(pagesrc, 'html.parser')
                rst = rst + findItems(soup)
            except:
                errors.append([az,p])
    driver.quit()
    df = pd.DataFrame(rst, columns=['name','url','casno'])
    try:
        with engine.connect() as conn:
            df.to_sql(name='alfa_items',
                     schema='portal',
                     if_exists='append',
                     dtype=dtypes,
                     index=False,
                     con=conn
                     )
    except:
        engine = create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')
        with engine.connect() as conn:
            df.to_sql(name='alfa_items',
                     schema='portal',
                     if_exists='append',
                     dtype=dtypes,
                     index=False,
                     con=conn
                     )