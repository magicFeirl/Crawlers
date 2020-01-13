import sys
import os
#After Python 3.4
from pathlib import Path
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

HOST = 'https://www.bilibili.com/read/'
#http://i0.hdslb.com/bfs/article/8b8f4ec433efd751ba734560f63d9019cb7e2608.jpg

#调整图片下载最大线程数
DOWNLOAD_MAX_THREAD = 10

#调整同时连接最大线程数（下载专栏列表图片用）
CONN_MAX_THREAD = 3

class Downloader():

    def __init__(self, folder):
        self._chdir(folder)

    def _chdir(self, folder):
        path_obj = Path(folder)

        try:
            folder = os.getcwd() + '/' + folder
            path_obj.mkdir(parents=True)
            os.chdir(folder)
        except Exception as exce:
            if len(os.listdir(folder)):
                _help('文件目录({})已存在，取消操作.\n'
                'Downloader _chdir Error:'.format(folder, str(exce)))
        else:
            self.path = os.getcwd() + '/'

    def parse_img_name(self,url):
        index = url.rfind('/')+1
        return url[index:]

    def save_img(self,url):
        with get(url) as resp:
            file_path = self.path + self.parse_img_name(url)
            if not os.path.isfile(file_path):
                with open(file_path,'wb') as fobj:
                    fobj.write(resp.content)


def get_article_imgs(self, article_id, begin=0, end=-1):
'''根据用户输入下载相应类型专栏'''

if not isinstance(article_id,list):
    _help('请输入专栏cv或专栏列表rl(类型为list)')
try:
    for item in article_id:
        if item.startswith('cv'):
            get_article(item)
        elif item.startswith('rl'):
            get_article_list(item,begin,end)
        else:
            _help('输入必须以cv或rl开头以标明专栏类型')
except Exception as exce:
    print('>Main.py Error:', str(exce))
pass

def _help(msg):
    print(msg)
    sys.exit()

def get(url, params={}):
    '''模拟get请求'''

    return requests.get(url, params=params)

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


        print(article_list_id)

    except Exception as exce:
        print('get_artcle_list Error:',str(exce))

def download_artcle_img(text,cv):
    '''提取专栏图片url并分线程下载'''

    url_list = [url.get('data-src') \
    for url in BeautifulSoup(text, 'html.parser',\
    parse_only=SoupStrainer('img', attrs={'data-size':True}))\
    .find_all()]

    with ThreadPoolExecutor(max_workers=DOWNLOAD_MAX_THREAD) as executor:
        executor.map(D.save_img,url_list)

def get_article(cv,folder=""):
    '''下载对应专栏图
    可选的文件保存文件夹名（未进行检查）'''

    with get(urljoin(HOST, cv)) as resp:
        text = resp.text

    if folder == "":
        folder = cv

    download_artcle_img(text,Downloader(folder))

#get_article_imgs(['cv114514'])

def main():
    #get_article('cv689489')
    '''Downloader(r'1233').save_img('http://i0.hdslb.com/bfs/article/69a59d33a3aad93b17ab2ff448676e48ea87dcbb.png')'''
    get_article_list('rl16885')

if __name__ == '__main__':
    main()
