'''获取bilibili用户动态或话题图片链接，并存为文本'''

import json
import requests
import sys
from FileUtils import *

ua = {
    'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36'
        ' (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
}

host = 'https://api.vc.bilibili.com/'
dynamic_url = host+'dynamic_svr/v1/dynamic_svr/space_history'
topic_url = host+'topic_svr/v1/topic_svr/topic_history'
topic_url = host+'topic_svr/v1/topic_svr/topic_history'

class Download():
    def __init__(self,query,offset=0,file_name=''):


        self.query = query

        if file_name == '':
            self.file_name = str(query)+'.txt'
        else:
            self.file_name = file_name

        self.offset = offset
        self.data_file = self.file_name+'.json'
        self.init_data()

    def parse_json(self,url,param):
        '''解析JSON'''

        r = requests.get(url,params=param,headers=ua)
        r.encoding = 'utf-8'
        request_data = r.json()['data']

        if request_data['has_more'] != 1:
            self.prt_error('已无更多数据')

        print(r.url)

        url_list = []
        cards = request_data['cards']


        for card in cards:
            try:
                cid = card['desc']['dynamic_id']
                if cid in self.visited_url:
                    print('已下载的链接')
                    return None
                else:
                    self.visited_url.append(cid)

                pics = json.loads(card['card'])['item']
                for pic in pics['pictures']:
                    '''执行下载操作'''
                    url_list.append(pic['img_src'])
                    pass
            except:

                pass
        else:
            #保存下轮请求偏移ID
            self.offset = card['desc']['dynamic_id']
            self.save_to_file(url_list)

    def get_dynamic_json(self):
        '''获取用户动态JSON'''

        param = {
            'host_uid':self.query,
        }
        param['offset_dynamic_id'] = self.offset

        self.parse_json(dynamic_url,param)

    def get_topic_json(self):
        '''获取话题JSON'''

        param = {
            'topic_name':self.query
        }
        param['offset_dynamic_id'] = self.offset

        self.parse_json(topic_url,param)

    def run(self,times=1):
        '''内部迭代下载图片'''

        for i in range(0,times):
            if isinstance(self.query,int):
                self.get_dynamic_json()
            elif isinstance(self.query,str):
                self.get_topic_json()
            else:
                self.prt_error('无效的参数:'+str(self.query))
        else:
            json.dump(self.visited_url,get_file_objw(self.data_file))

    def save_to_file(self,url_list):
        try:
            with get_file_obja(self.file_name) as file_obj:
                for url in url_list:
                    file_obj.write(url)
                    file_obj.write('\n')
        except IOError as ie:
           self.prt_error(ie)

    def prt_error(self,msg):
        print(msg)
        sys.exit()

    def init_data(self):
        if not is_file(self.data_file):
            self.visited_url = []
        else:
            self.visited_url = json.load(get_file_objr(self.data_file))

        try:
            self.offset = self.visited_url[self.offset]
        except:
            self.offset = 0
            pass



Download('东方美图',-1).run(3)

