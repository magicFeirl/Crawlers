import os
import json
import time
from random import randint

import requests


class SignTieba(object):
    def __init__(self, BDUSS):
        self.BDUSS = BDUSS

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
            'cookie': 'BDUSS={};'.format(BDUSS)
        }

    def sign(self, filename=None, refresh=False):
        '''可传入吧列表文件和一个刷新吧列表标志，如果不传则每次都重新获取吧列表'''
        api = 'https://tieba.baidu.com/sign/add'
        tb_list = self.get_ba_list(filename, refresh)

        for tb in tb_list:
            r = requests.post(api, data=dict(ie='utf-8', kw=tb), headers=self.headers)
            print(tb, r.json())

            time.sleep(randint(2, 3))

    def get_ba_list(self, filename=None, refresh=False):
        '''获取吧列表（本地文件 or 请求接口）'''
        ba_list = []

        if not filename or refresh or not os.path.exists(filename):
            ba_list = self.get_ba_list_by_api()
        else:
            ba_list = self.get_ba_list_from_file(filename)

        return ba_list

    def get_ba_list_from_file(self, filename):
        '''从本地文件获取吧列表'''
        with open(filename, 'r') as file:
            ba_list = json.load(file)

        return ba_list

    def get_ba_list_by_api(self):
        '''请求接口获取吧列表'''
        api = 'https://tieba.baidu.com/mo/q/newmoindex'
        rjson = requests.get(api, headers=self.headers).json()

        if rjson['error'] != 'success':
            print('请求接口出错')
            return []

        ba_list = []

        for ba in rjson['data']['like_forum']:
            ba_list.append(ba['forum_name'])

        return ba_list

    def save_ba_list(self, ba_list, filename):
        '''传入吧列表和保存文件名保存吧列表'''
        with open(filename, 'w') as file:
            json.dump(ba_list, file)

        return ba_list


if __name__ == '__main__':
    BDUSS = 'here' # 填入你的BDUSS
    SignTieba(BDUSS).sign()
