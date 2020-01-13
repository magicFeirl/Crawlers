from time import time

import requests
from pathlib import Path
from bs4 import BeautifulSoup
from bs4 import SoupStrainer

import os
import sys
import threading

#在此调整下载线程数
tlen = 10

class Downloader():
    def __init__(self):
        pass

    def get(self,url,params={}):
        headers = {

        }

        r = requests.get(url,params=params,headers=headers)
        r.encoding = 'utf-8'
        return r


    #从URL分离文件名
    def split_url_name(self,url):
        a = url.rfind('/')+1
        return url[a:]

    #下载文件并保存至本地
    def save_to_file(self,url_list):
        for url in url_list:
            file_name = self.split_url_name(url)
            desk = self.folder+file_name

            print('Downloading->',file_name)
            with open(desk,'wb') as f_obj:
                for chunk in self.get(url).iter_content(512):
                    f_obj.write(chunk)

    #线程函数
    def run(self,img_list):
        url_list = []
        for img in img_list:
            url = 'https:'+img.get('data-src')
            url_list.append(url)

        self.save_to_file(url_list)

    #创建文件夹
    def mkdir(self,folder):
        folder+='//'
        if not os.path.exists(folder):
            Path(folder).mkdir()
        else:
            if len(os.listdir(folder)):
                print('图片文件夹已存在，跳过操作')
                sys.exit()

        self.folder = folder

    #Run it!
    def get_articel_img(self,cid):
        start_time = time()
        count = 0

        try:
            if not 'cv' in cid:
                cid = 'cv'+cid

            self.cid = cid
            self.mkdir(cid)

            res = self.get('https://www.bilibili.com/read/'+cid)

            img_ele = BeautifulSoup(res.text,'html.parser',
            parse_only=SoupStrainer('img',attrs={'data-size':True})).find_all()

            count = len(img_ele)
            chunk = count//tlen #开启tlen条线程
            offset = 0

            if chunk <=0:
                chunk = len(img_ele)

            threads = []
            while True:
                img = img_ele[offset:offset+chunk]
                if len(img) == 0:
                    break

                thread = threading.Thread(target=self.run,args=(img,))
                threads.append(thread)
                thread.start()

                offset+=chunk

        except Exception as e:
            print('ERROR: ',e)
            pass
        else:
            for thread in threads:
                thread.join()

            print('下载用时：',int(time()-start_time),'s')
            print('共下载:',count,'张图片')


#get_articel_img('4127710')
Downloader().get_articel_img('cv4310044')
