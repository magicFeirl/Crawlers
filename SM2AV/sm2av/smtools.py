import re

import requests
import aiohttp
from lxml import etree


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' +
    ' AppleWebKit/537.36 (KHTML, like Gecko)' +
    ' Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69'
}


async def get_session(headers=None, timeout=60):
    """获取一个默认的session"""

    if not headers:
        headers = HEADERS

    return aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=timeout))


def perr(message, err=None):
    """打印消息&异常处理的函数"""

    print('[SM2AV]', message)

    if err:
        print(f'Error type: {type(err)}')


async def get_sm_from_desc(session, aid):
    """从B站视频简介中获取sm号列表"""
    if str(aid).startswith('av'):
        aid = str(aid)[2:]

    print(f'从 av{aid} 获取sm号列表...')

    api = 'https://api.bilibili.com/x/web-interface/' + \
          f'archive/desc?aid={aid}'

    text = ''

    try:
        async with session.get(api, headers=HEADERS) as resp:
            r = await resp.json()

            if r['code'] == 0:
                text = r['data']
            else:
                perr('请求状态码错误')
    except Exception as error:
        perr(f'请求数据异常: {error}', error)

    return re.findall(r'sm\d+', text)


async def get_sm_from_nico(session, uid):
    """从n站用户投稿获取sm号列表，使用前请确保能够连上n站
    这里使用aiohttp会抛出异常，至于原因暂且不清楚，可以使用requests"""

    print(f'从N站用户 {uid} 投稿列表获取sm号...')

    li = []
    url = f'https://www.nicovideo.jp/user/{uid}/video'

    def sub(sm):
        if sm.startswith('watch/'):
            return sm[len('watch/'):]

    def get_sm_list(html):
        xpath = '//div[@class="section VideoItem-videoDetail"]/h5/a/@href'
        selector = etree.HTML(html)
        return list(map(sub, selector.xpath(xpath)))

    try:
        with requests.get(url) as resp:
            li = get_sm_list(resp.text)
    except Exception as error:
        perr(f'请求网页异常: {error}', error)

    return li


async def get_sm_from_file(filename, encoding='utf-8'):
    """从本地文件获取sm号列表"""

    text = ''

    try:
        with open(filename, encoding=encoding) as fobj:
            text = fobj.read()
    except Exception as error:
        perr(f'打开文件 {filename} 失败: {error}', error)

    return re.findall(r'sm\d+', text)


async def get_sm_from_text(text):
    """从字符串获取sm号列表，多个sm号用半角逗号(,)隔开"""
    li = []

    try:
        li = list(map(lambda s: s.strip(), text.split(',')))
    except Exception as error:
        perr(f'分离SM号失败: {error}', error)

    return li
