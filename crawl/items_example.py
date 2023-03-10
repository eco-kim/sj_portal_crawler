import requests
from bs4 import BeautifulSoup as Soup
import pandas as pd
import time

from commons.mysql import mysqlEngine, loadDataType
from commons.bs import getSoup
from commons.selenium import seleniumWindow
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

engine = mysqlEngine()
dtypes = loadDataType('portal','alfa_items')

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
url = ''

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
        engine = mysqlEngine()
        with engine.connect() as conn:
            df.to_sql(name='alfa_items',
                     schema='portal',
                     if_exists='append',
                     dtype=dtypes,
                     index=False,
                     con=conn
                     )