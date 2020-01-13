import requests
import sys

base_url ='https://api.vc.bilibili.com/link_draw/v1/doc/doc_list'

ua = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'
        '537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
}

class Downloader:

    def __init__(self,uid):
        self.uid = uid

    def check_download(self,sp,ep,ps):
        print('Begin:'+str(sp),'End:'+str(ep))
        choice = str(input('将下载'+str((ep-sp)*ps) \
        +'张图片?(Y/N)\n')).upper()

        if choice != 'Y':
            print('已取消操作')
            sys.exit()

    def get_json(self,pn,page_size):
        p = dict()
        p['page_size'] = page_size
        p['uid'] = self.uid
        p['page_num'] = pn

        r = requests.get(base_url,headers=ua,params=p)

        print('Downloading->\n{}'.format(r.url))

        return r.json()

    def run(self,sp=0,ep=1,page_size=30):
        self.check_download(sp,ep,page_size)

        #file = open(self.uid+'.txt','a')

        for i in range(sp,ep):
            items = self.get_json(i,page_size)['data']['items']
            if len(items) == 0:
                print('已无更多数据')
                return None

            for j in items:
                if len(j) == 0:
                    continue
                for k in j['pictures']:
                    img_src = k['img_src']
                    #file.write(img_src+'\n')


Downloader('327025636').run()





