from time import time
import re

import requests
from lxml import etree

host = 'https://www.bilibili.com/read/'

def get_imgs_url(session, cv):
    '''创建相应专栏标题文件夹并返回专栏图片链接列表'''

    if not cv.startswith('cv'):
        cv = 'cv' + cv

    url = host + cv

    with session.get(url) as resp:

        html = resp.text
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0]
        url_list = selector.xpath('//img[@data-size]/@data-src')

        if len(url_list) == 0:
            print('专栏 {cv} 未发现图片，终止操作'.format(cv=cv))
            exit()

        print(url_list)


def get_img_by_api(session, cv):
    url = f'https://api.bilibili.com/x/article/view?id={cv}'
    with session.get(url) as resp:
        text = resp.text
        # print(text)
        url_list = re.findall(r'img src=\\"(.+?)\\"', text)

        print(url_list)

if __name__ == '__main__':
    start = time()
    session = requests.Session()


    get_imgs_url(session, '4098563') # 0.2s

    # get_img_by_api(session, '4098563') # 0.18s 略快，缺点是无法去除分割线图片
    print(f'Done {time() - start} s')
