import requests
from pathlib import Path
from bs4 import BeautifulSoup
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

    def split_url_name(self,url):
        a = url.rfind('/')+1
        return url[a:]

    def save_to_file(self,url_list):
        for url in url_list:
            file_name = self.split_url_name(url)
            desk = self.folder+file_name

            print('Downloading->',file_name)
            with open(desk,'wb') as f_obj:
                f_obj.write(self.get(url).content)

    def run(self,img_list):
        url_list = []
        for img in img_list:
            url = 'https:'+img.find('img').get('data-src')
            url_list.append(url)

        self.save_to_file(url_list)

    def mkdir(self,folder):
        folder+='//'
        if not os.path.exists(folder):
            Path(folder).mkdir()
        else:
            if len(os.listdir(folder)):
                print('图片文件夹已存在，跳过操作')
                sys.exit()

        self.folder = folder

    def get_articel_img(self,cid):
        try:
            if not 'cv' in cid:
                cid = 'cv'+cid

            self.cid = cid
            self.mkdir(cid)

            res = self.get('https://www.bilibili.com/read/'+cid)

            bs = BeautifulSoup(res.text,'html.parser')
            img_ele = bs.find_all(attrs={'class':'img-box'})
            chunk = len(img_ele)//tlen #开启tlen条线程
            offset = 0

            while True:
                img = img_ele[offset:offset+chunk]
                if len(img) == 0:
                    break

                threading.Thread(target=self.run,args=(img,)).start()
                offset+=chunk

        except Exception as e:
            print('ERROR: ',e)
            pass


#get_articel_img('4127710')
Downloader().get_articel_img('cv3949523')
