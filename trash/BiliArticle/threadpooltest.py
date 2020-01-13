import re
from time import sleep,time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import os

import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer


HOST = 'https://www.bilibili.com/read/'

def get(url, params={}):
    '''模拟get请求'''

    return requests.get(url, params=params)

def get_resp(url):
    return get(HOST+url)

def get_article(cv):

    with get(urljoin(HOST, cv)) as resp:
        text = resp.text

    url_list = [url.get('data-src') \
    for url in BeautifulSoup(text, 'html.parser', \
    parse_only=SoupStrainer('img', attrs={'data-size':True})) \
    .find_all()]

    def parse_img_name(url):
        index = url.rfind('/')+1
        return url[index:]

    def download(url):
        img_file = './Test/'+parse_img_name(url)
        print(img_file)
        with get('https:'+url) as resp:
            with open(img_file,'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)

    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(download,url_list)

def get_article_list(rl, begin=0, end=-1):
    '''返回专栏列表
    下载范围[begin,end)'''

    try:
        reg = re.compile('\w+ = \[(.*?)\]')

        text = get(urljoin('https://www.bilibili.com/'
        'read/readlist/',rl)).text

        result = BeautifulSoup(text,'html.parser',\
        parse_only=SoupStrainer('script')).find()

        article_list_id = list(map(lambda aid:'cv'+aid,\
        reg.search(result.text).group(1).split(',')))

        print('下载专栏列表,含专栏个数:',len(article_list_id))

        with ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(get_article,article_list_id[begin:end])

    except Exception as exce:
        print(str(exce))




'''with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for i in range(1,10):
            future = executor.submit(sleep,1)
            futures.append(future)

        for f in futures:
            print(f.result())'''


'''with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.map(sleep,[1]*10)
        for i in result:
            print(i)
        else:
            print('--')'''

get_article_list('rl16885')
#get_article('cv739455')
