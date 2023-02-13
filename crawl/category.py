from commons import mysqlEngine, getSoup
from targets import targets
import pandas as pd
from sqlalchemy import types as sqltypes

categoryColumns = ['id','title','parent_id','root_id','uri','counts']
categoryDtypes = {'id': sqltypes.INTEGER(),
                'title': sqltypes.VARCHAR(50),
                'parent_id':sqltypes.INTEGER(),
                'root_id':sqltypes.INTEGER(),
                'uri': sqltypes.VARCHAR(100),
                'counts': sqltypes.INTEGER()}

class categoryCrawler:
    def __init__(self, target):
        self.name = target
        self.base_url = targets[target]['url']
        self.root = targets[target]['id']
        self.soup = getSoup(self.base_url)
        self.data = [[self.root, self.name, self.root, self.root, self.base_url, 0]]
        self.idx = [self.root + 10, self.root + 100, self.root + 1000]
        self.parent = [self.root, None, None, 0]

    def parse(self, a, depth, url=False):
        idx = self.idx[depth]
        parent = self.parent[depth]
        name = a.text.strip()
        uri = a['href']
        if url:
            uri = '/'+uri.split('/')[-1]

        self.parent[depth+1]= idx
        self.idx[depth] += 1
        return [idx,name,parent,self.root,uri,None]    

def naviMro():
    crawler = categoryCrawler('(주)나비엠알오')
    reflist = crawler.soup.find_all('div',{'id':'list-category-wrap'})[0].find_all('a')

    for l in reflist:
        if 'href' in l.attrs.keys():
            href = l['href']
            if href.split('/')[1] == 's':
                if len(href.split('/')[2])==4:
                    crawler.data.append(crawler.parse(a=l, depth=0))
                else:
                    crawler.data.append(crawler.parse(a=l, depth=1))

    df = pd.DataFrame(crawler.data, columns=categoryColumns)
    df = df.sort_values(by='id')
    return df

def labsMro():
    crawler = categoryCrawler("(주)랩스엠알오")
    reflist = crawler.soup.find_all('div',{'class':'category'})[0].find_all('a')

    depths = {'category_depth1_a':0,
            'category_depth2_a':1,
            'category_depth3_a':2}
    for l in reflist:
        if 'class' in l.attrs.keys():
            depth = depths[l['class'][0]]
            crawler.data.append(crawler.parse(a=l, depth=depth, url=True))

    df = pd.DataFrame(crawler.data, columns=categoryColumns)
    df = df.sort_values(by='id')
    return df

def cacheBy():
    crawler = categoryCrawler("캐시바이")
    reflist = crawler.soup.find_all('a',{'class':'CategorySubItem'})
    depth=0
    for l in reflist:
        href = l['href']
        name = l.find_all('div',{'class':'name'})[0].text.strip()
        counts = int(l.find_all('div',{'class':'counts'})[0].text)
        crawler.data.append([crawler.idx[depth],name,crawler.parent[0],crawler.root,href,counts])
        crawler.idx[depth] += 1

    df = pd.DataFrame(crawler.data, columns=categoryColumns)
    df = df.sort_values(by='id')
    return df

def uploadTable(df):
    df = df.set_index('id')
    engine = mysqlEngine()
    with engine.connect() as conn:
        df.to_sql(name='portal_item_category_temp',
                schema='portal',
                if_exists='append',
                con=conn,
                dtype=categoryDtypes,
                index=True,
                index_label='id')

if __name__=='__main__':
    uploadTable(naviMro())
    uploadTable(labsMro())
    uploadTable(cacheBy())

#업데이트시 레거시 테이블 어떻게 처리할지 생각해야함.
#1안 : s3에 업로드(append) 2안 : 검색 인덱스 업데이트 완료 시 삭제