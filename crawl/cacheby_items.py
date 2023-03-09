from commons import mysqlEngine, seleniumWindow, goToBottom, loadDataType
import pandas as pd
from selenium.webdriver.common.by import By
import pickle
from bs4 import BeautifulSoup as Soup

def findSouptext(item, classname):
    temp = item.find_all('div',{'class':classname})
    if temp:
        return temp[0].text
    else:
        return None

def parseSoupItem(item, catid):
    href = item['href']
    title = findSouptext(item, 'title')
    brand = findSouptext(item, "brand-name")
    price = findSouptext(item, 'price')
    return [title, brand, price, href, catid]

engine = mysqlEngine()

root_id = 1122
category_id = [1122,1130,1176,1286]
cats = list(map(str, category_id))
tablename = 'cacheby_items'
with engine.connect() as conn:
    category = pd.read_sql_query(f'select * from portal.portal_item_category where id in ({", ".join(cats)});',conn)

category = category.set_index('id')
base_url = category.loc[root_id,'uri']

dtypes = loadDataType('portal',tablename)
dtypes.pop('img_url')
n = 0
for idx, row in category.iterrows():
    rst = []

    print(idx, row['title'])
    url = base_url+row['uri']
    driver = seleniumWindow(url)
    goToBottom(driver)
    print("page down finished")
    pagesrc = driver.page_source
    soup = Soup(pagesrc, 'html.parser')
    driver.quit()
    items = soup.find_all('a',{'class':'ProductCard'})

    for i, item in enumerate(items):
        rst.append(parseSoupItem(item,idx))
        n += 1            
        if n%1000==0:
            print(f"===={n}====")
            
    rst = pd.DataFrame(rst, columns=['title','brand','price','url','category_id'] )
    with open(f'./cacheby_{idx}','wb') as f:
        pickle.dump(rst, f)
    
    with engine.connect() as conn:
        rst.to_sql(name=tablename,
                schema='portal',
                dtype=dtypes,
                index=False,
                if_exists='append',
                con=conn)