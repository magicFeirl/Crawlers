'''爬取bilibili专栏图片'''

import re
import sys
import os
from time import time,sleep
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

HOST = 'https://www.bilibili.com/read/'

#调整图片下载最大线程数
DOWNLOAD_MAX_THREAD = 10

#调整同时连接最大线程数（下载专栏列表图片用）
CONN_MAX_THREAD = 3

def _help(msg):
    '''打印错误信息并退出程序'''

    print(msg)
    sys.exit()

def get(url, params={}):
    '''模拟get请求'''

    return requests.get(url, params=params)

def confirm():
    '''确认下载函数'''

    input('将开始下载，按任意键继续...')

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
        confirm()

        with ThreadPoolExecutor(max_workers=CONN_MAX_THREAD) as executor:
            executor.map(get_article,article_list_id[begin:end])

    except Exception as exce:
        _help('get_artcle_list Error:'+str(exce))

def download_img(cv,url_list,path):
    '''分线程下载图片'''

    print('Downloading cv:',cv)

    def parse_img_name(url):
        '''提取文件名'''

        index = url.rfind('/')+1
        return url[index:]

    def save_to_file(url):
        '''将url保存至本地'''

        img_file = path + parse_img_name(url)

        if os.path.exists(img_file):
            print('文件已存在')
            return

        if not url.startswith('http:'):
            url = 'http:'+url

        with get(url) as resp:
            with open(img_file,'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)

        sleep(1)

    with ThreadPoolExecutor(max_workers=DOWNLOAD_MAX_THREAD) as executor:
        executor.map(save_to_file,url_list)

def get_article(cv):
    '''解析对应专栏图url并下载'''

    path = os.getcwd() + '\\' +cv + '\\'

    if not os.path.exists(path):
        os.mkdir(path)
    elif len(os.listdir(path)):
        print(cv,'文件夹已存在且含有文件，终止操作')
        return

    sleep(.5)
    with get(urljoin(HOST, cv)) as resp:
        text = resp.text

    url_list = [url.get('data-src') \
    for url in BeautifulSoup(text, 'html.parser', \
    parse_only=SoupStrainer('img', attrs={'data-size':True})) \
    .find_all()]

    download_img(cv,url_list,path)


#启动函数
def download_article_img(param, begin=0, end=-1):
    '''根据用户输入下载相应类型专栏
    参数：cv号或rl（专栏列表）号 专栏列表起始位置=0 结束位置=-1'''

    if not isinstance(param,list):
        _help('请输入专栏cv或专栏列表rl(类型为list)')

    try:
        for item in param:
            if item.startswith('cv'):
                get_article(item)
            elif item.startswith('rl'):
                get_article_list(item,begin,end)
            else:
                _help('输入必须以cv或rl开头标明')
    except Exception as exce:
        _help('>Main.py Error:'+str(exce))
    pass

def main(param):

    start = time()

    folder = 'Downloader'
    if not os.path.exists(folder):
        os.mkdir(folder)

    os.chdir('./'+folder)

    #
    download_article_img(param)

    print('下载完成，耗时{}'.format(str(int(time() - start))))

if __name__ == '__main__':

    main(['rl...'])
