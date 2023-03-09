import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
import pickle
import requests
from bs4 import BeautifulSoup as Soup

##beautiful soup
def getSoup(url):
    hdr = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'}
    response = requests.get(url=url, headers=hdr)
    if response.status_code!=200:  
        return response.status_code
    else:
        soup = Soup(response.content.decode('utf8','replace'), 'html.parser')
    return soup

##mysql 
sql = 'mysql+pymysql'
host = 
port = 3306
db = 
user = 
passwd = 
engine = create_engine(f'{sql}://{user}:{passwd}@{host}/{db}')

target = 10

def tciTable(url):
    soup = getSoup(url)
    try:
        df = pd.read_html(str(soup.find_all('table',{'id':'PricingTable'})[0]))[0]
    except:
        return None
    return df

with engine.connect() as conn:
    urls = pd.read_sql_query(f'select * from portal.tci_urls where part={target};', conn)

df = pd.DataFrame()
for idx, row in urls.iterrows():
    url = row['url']
    temp = tciTable(url)    
    if temp is not None:
        temp['url'] = url
        df = pd.concat([df, temp], ignore_index=True)
    if idx%100==0:
        print(f"===={idx}====")

df = df.rename(columns={'포장단위':'volume', '가격':'price'})
df = df[['url','volume','price']]
with open('./tci_dataframe','wb') as f:
    pickle.dump(df, f)

with engine.connect() as conn:
    df.to_sql(name='tci_volumes',
        schema='portal',
        index=False,
        dtype={'url':sqlalchemy.types.VARCHAR(200),
        'volume':sqlalchemy.types.VARCHAR(20),
        'price':sqlalchemy.types.VARCHAR(30)},
        con=conn)