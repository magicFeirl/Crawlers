"""获取sm号工具模块"""

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
    """获取一个默认的session

    headers: 请求头
    timeout: 请求超时
    """

    if not headers:
        headers = HEADERS

    return aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=timeout))


def perr(message, err=None):
    """打印消息&异常处理的函数"""

    print('[SM2AV]', message)

    if err:
        print(f'Error type: {type(err)}')


async def bv2av(session, bvid):
    """简单的BV转AV程序"""

    api = f'https://api.bilibili.com/x/web-interface/archive/stat?bvid={bvid}'
    aid = ''

    try:
        async with session.get(api) as resp:
            r = await resp.json()
            if r['code'] == 0:
                aid = r['data']['aid']
            else:
                perr(f'无效的BV号: {bvid}')
    except Exception as error:
        perr(f'BV号转AV号出错: {error}', error)

    return aid

async def get_sm_from_desc(session, aid):
    """从B站视频简介中获取sm号列表

    session: 一个ClientSession对象
    aid: 视频av号"""

    if str(aid).upper().startswith('BV'):
        aid = await bv2av(session, aid)

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

    li = re.findall(r'sm\d+', text)
    print(f'共获取到 {len(li)} 条数据')

    return li


async def get_sm_from_nico(uid, begin=1, end=1):
    """从n站用户投稿获取sm号列表，使用前请确保能够连上n站
    这里使用aiohttp会抛出异常，原因可能是aiohttp和httpx貌似默认不会走全局代理?
    可以使用requests代替

    这里有个缺陷：
    必须等到sm号全部解析完后才能启动检索，在多页且网速较慢的情况下无法体现协程的优势

    uid: N站用户ID
    begin: 投稿列表起始页
    end: 投稿列表终止页"""

    print(f'从N站用户 {uid} 投稿列表获取sm号...')

    li = []

    def sub(sm):
        if sm.startswith('watch/'):
            return sm[len('watch/'):]

    def get_sm_list(html):
        xpath = '//div[@class="section VideoItem-videoDetail"]/h5/a/@href'
        selector = etree.HTML(html)
        return list(map(sub, selector.xpath(xpath)))

    try:
        for idx in range(begin, end+1):
            url = f'https://www.nicovideo.jp/user/{uid}/video?page={idx}'
            with requests.get(url) as resp:
                temp = get_sm_list(resp.text)

                if len(temp) == 0:
                    break

                li += temp
    except Exception as error:
        perr(f'请求网页异常: {error}', error)

    print(f'共获取到 {len(li)} 条数据')
    return li


async def get_sm_from_file(filename, encoding='utf-8'):
    """从本地文件获取sm号列表

    filename: 文件名
    encoding: 编码"""

    print(f'从文件 {filename} 读取sm号...')
    text = ''

    try:
        with open(filename, encoding=encoding) as fobj:
            text = fobj.read()
    except Exception as error:
        perr(f'打开文件 {filename} 失败: {error}', error)

    li = re.findall(r'sm\d+', text)
    print(f'共获取到 {len(li)} 条数据')

    return li


async def get_sm_from_text(text):
    """从字符串获取sm号列表，多个sm号用半角逗号(,)隔开"""

    li = []

    try:
        li = list(map(lambda s: s.strip(), text.split(',')))
    except Exception as error:
        perr(f'分离SM号失败: {error}', error)

    print(f'共获取到 {len(li)} 条数据')

    return li
