'''
    本地版贴吧自动签到

    贴吧签到只需要一个 BDUSS
    获取贴吧列表需要 BDUSS 和 tieba.baidu 下的 STOKEN

    由于 STOKEN 有一个月的过期时间且 SCF 对 lxml 支持不好，因此考虑 SCF 端只保留贴吧列表文件和 BDUSS，而更新贴吧列表则由本地程序实现
'''

import time
import json
from random import randint

import requests

BDUSS = 'here'

def get_tb_list_from_file(username):
    with open(username, 'r') as file:
        tb_list = json.load(file)

    return tb_list

class SignTieba(object):
    def __init__(self):
        pass

    def sign(self, tb_list, BDUSS):
        api = 'https://tieba.baidu.com/sign/add'

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
            'cookie': 'BDUSS={};'.format(BDUSS)
        }

        for tb in tb_list:
            r = requests.post(api, data=dict(ie='utf-8', kw=tb), headers=headers)
            print(tb, r.json())

            time.sleep(randint(2, 3))


if __name__ == '__main__':
    ST = SignTieba()
    tb_list = get_tb_list_from_file('ww2100')

    ST.sign(tb_list, BDUSS)







