'''bilibili专栏图片爬虫V1.0'''
#Python推荐库导入顺序：内部 扩展 自定义
from time import sleep,ctime
from threading import Thread
import sys
from pathlib import Path
import os
import urllib.parse as up
import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

#推荐常量使用大写标识
HOST = 'https://www.bilibili.com/read/'

#模拟get请求
def get(url,params={}):
    r = None
    try:
        r = requests.get(url,params=params)
    except Exception as e:
        print('Error:',str(e))
    return r

def run(folder,url_list):
    for i in url_list:
        file_name = folder+'//'+i[i.rfind('/')+1:]
        url = up.urljoin(HOST,i)

        print('Downloading ->',file_name)
        with open(file_name,'wb') as f:
            f.write(get(url).content)

def get_article_img(cv,tn=1):
    '''输入专栏cv，获取图片'''

    url = up.urljoin(HOST,cv)
    text = get(url).text

    '''获取BeautifulSoup对象，参数：网页文本，解析器...
        为了方便起见我们使用Python内置的html解析器
    '''
    imgs = BeautifulSoup(text,'html.parser',
    parse_only=SoupStrainer('img',attrs={'data-size':True})).find_all()

    url_list = [url.get('data-src') for url in imgs]
    tlen = len(url_list)

    if tlen//tn <=0:
        tn = tlen
    else:
        tn = tlen//tn

    offset = 0

    mkdir(cv)

    while True:
        urls = url_list[offset:offset+tn]

        if not len(urls):
            break

        Thread(target=run,args=(cv,urls)).start()
        offset += tn

def mkdir(folder):
    folder+='//'
    if not os.path.exists(folder):
        Path(folder).mkdir()
    else:
        if len(os.listdir(folder)):
            print('图片文件夹已存在，跳过操作')
            sys.exit()


get_article_img('cv4263864',10)
