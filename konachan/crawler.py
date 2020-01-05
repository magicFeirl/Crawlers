'''Konachan图片下载'''

import re
from time import time,sleep
import sys
import os

import requests
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

HOST = 'https://konachan.com/post'
REG_FILENMAE = re.compile(r'/.+/(.+)/')

def get(url,params={}):
    '''模拟get请求'''

    return requests.get(url,params=params)

def parse_filename(url):
    '''从URL中提取文件名（暂且用不上）'''

    try:
        return REG_FILENMAE.search(url).group(1)+url[url.rfind('.'):]
    except Exception as e:
        t = str(int(time()))+'.jpg'
        print('parse filename error:',str(e))
        print('new filename:',t)
        return t

def save_to_file(url_list,file_obj):
    '''将链接保存至文件'''

    if file_obj:
        for url in url_list:
            print(url,file=file_obj)
    else:
        print('无效的文件对象!')
        sys.exit()


def get_img(tag,start=1,end=2,delay=1,file_name=''):
    '''获取图片链接并保存至文件
    参数：tag名，保存本地文件名=tag，[起始页=1，截止页=2)，抓取延时=1s
    '''

    count = 0

    if file_name == '':
        file_name = str(tag)

    if not (file_name.endswith('.txt')):
        file_name += '.txt'

    if os.path.isfile(file_name):
        print(file_name,'文件已存在，终止下载')
        sys.exit()

    print('创建保存文件:',file_name)

    params = {
        'tags':tag,
    }

    with open(file_name,'a') as f:
        for page in range(start,end):
            params['page'] = page
            r = get(HOST,params)

            if r.status_code != 200:
                print('HTTP status error:',r.status)
                print('URL:',r.url)
                continue

            print('Downloading:',r.url)

            large_imgs = BeautifulSoup(r.text,'html.parser',parse_only=
            SoupStrainer('a',attrs={'class':re.compile('directlink')}))

            if not len(large_imgs):
                print('已到达页尾:',page-1)
                sys.exit()

            #链接列表
            url_list = [img.get('href') for img in large_imgs \
             if img.get('href')]

            save_to_file(url_list,f)

            count += len(large_imgs)
            print('已保存:',count,'个链接')
            sleep(delay)


get_img('ke-ta',1,100)

