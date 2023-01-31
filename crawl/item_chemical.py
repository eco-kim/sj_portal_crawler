from commons import mysqlEngine, getSoup
import pandas as pd
from sqlalchemy import types as sqltypes
import requests

def selectChemicalCategory():
    keywords = ['시약'] ##키워드 추가 예정, 아예 시약회사들은 함수 따로 분리 예정
    key_excepts = ['시약장'] 
    query = "select * from portal.portal_item_category"
    engine = mysqlEngine()
    with engine.connect() as conn:
        category = pd.read_sql_query(query, conn)

    df = pd.DataFrame()
    for key in keywords:
        temp = category[category.title.str.contains(key)]
        df = pd.concat([df,temp])

    for key in key_excepts:
        df = df[~df.title.str.contains(key)]
        
    parents = df[df.id.isin(category.parent_id.unique())]
    df = pd.concat([df,category[category.parent_id.isin(parents)]])
    df = df[~df.id.isin(category.parent_id.unique())]
    root = category[category.id==category.root_id]
    root = root[['id','title','uri']].set_index('id')
    df = df.join(root, on='root_id', how='inner',rsuffix='_root')
    del(category)
    return df


def naviMro(category_info, image=False):
    category_id = category_info['id']
    url = category_info['uri_root']+category_info['uri']
    soup = getSoup(url)

    temp = soup.find_all('div',{'class':'paging'})[0].find_all('a',{'class':'icon icon-page-next2'})[0]
    pages = int(temp['href'].split('/')[3].split('-')[1])

    for page in range(1,pages+1):
        url2 = url + f'/page-{page}'
        soup = getSoup(url2)

        itemlist = soup.find_all('li',{'class':'item'})

        for item in itemlist:
            rst = {}
            temp = item.find_all('a',{'class':'item__title'})[0]
            rst['title'] = temp['title']
            rst['uri'] = temp['href']
            price = item.find_all('p', {'class':'item__price'})
            if len(price)==0:
                rst['valid'] = 0
            else:
                rst['valid'] = 1    
            
            img = item.find_all('img', {'class':'grid-img'})[0]
            uri = img['src']    
            img_name = uri.split('/')[-1]
            code = img_name.split('.')[0]
            rst['code'] = code
            
            if image:
                img_data = requests.get('https:'+uri).content

                ##s3 업로드 내일작성

categories = selectChemicalCategory()