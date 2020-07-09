'''获取贴吧列表，只在本地使用'''

import os
import json

import requests
from lxml.html import fromstring


def get_tb_list(BDUSS, STOKEN, username, refresh=False):
    '''使用 refresh 指定是否重新拉取贴吧列表'''
    if not os.path.exists(username) or refresh:
        tb_list = get_tb_list_by_req(BDUSS, STOKEN)
        with open(username, 'w') as file:
            json.dump(tb_list, file)
    else:
        with open(username, 'r') as file:
            tb_list = json.load(file)

    return tb_list


def get_tb_list_by_req(BDUSS, STOKEN):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
            'cookie': 'BDUSS={}; STOKEN={};'.format(BDUSS, STOKEN)
        }

        idx = 1
        # 这里需要为期 1 个月的 STOKEN
        page = 'http://tieba.baidu.com/f/like/mylike?&pn={}'
        xpath = '//td/a[not(@class)]/text()'
        last_page_xpath = '//div[@class="pagination"]/a/@href'

        tb_list = []

        last_page = None

        while True:
            url = page.format(idx)
            idx += 1

            r = requests.get(url, headers=headers)

            html = fromstring(r.text)
            elems = html.xpath(xpath)

            if not last_page:
                last_page = html.xpath(last_page_xpath)

                if last_page:
                    last_page = last_page[-1]

            for e in elems:
                tb_list.append(e)

            # 如果有多页那么 last_page 不会为 None
            if not last_page or url.endswith(last_page):
                break

        return tb_list


def main():
    BDUSS = 'ZobzR0TU82YXRhcEktcTg5WlZyamtueXFTNFB0d01tSU9MUVU0QmNqRm5RUzVmRUFBQUFBJCQAAAAAAAAAAAEAAADU-R9ASWNnbm9vb29vb29vb28AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGe0Bl9ntAZfNH'
    STOKEN = '190e281eb565eb590ffcf34cdb3e268321a98ca6128353c7f6c7e7f893d23743'
    username = 'icgo'

    get_tb_list(BDUSS, STOKEN, username, refresh=True)

if __name__ == '__main__':
    main()
