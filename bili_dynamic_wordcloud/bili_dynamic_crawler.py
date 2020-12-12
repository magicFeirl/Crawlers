"""
爬取 B 站用户动态（不含专栏）文本并保存至本地
"""
import time
import json
from random import randint

import requests


def get_dynamic_text(data):
    """
    传入动态数据项（rjson['data']），返回动态内容列表，如果没有内容则返回空列表

    Notes:
        type: 2  带图片的动态
        type: 4  不带图片的动态
        type: 64 专栏动态

    Args:
        data: 动态数据项，一般由 fetch_one_dynamic 的第一个返回值提供

    Returns:
        解析出来的动态文本列表
    """

    cards = data['cards']
    content_list = []

    for card in cards:
        try:
            ctype = card['desc']['type']
        except:
            continue
        if ctype in [2, 4]: # 只统计日常动态
            content_json = json.loads(card['card'])['item']
            if ctype == 2:
                content = content_json['description']
                # print(content)
            else:
                content = content_json['content']
                 # print(content)

            content_list.append(content)

    return content_list


def fetch_one_dynamic(uid, offset=0):
    """
    拉取一页动态
    Args:
        uid: 用户 id
        offset: 起始偏移

    Returns:
        一个包含动态数据的列表和下个动态偏移值，如果出错则返回一个含空列表和 0 的元组 (list, int)
    """

    # 接口默认每次返回 11 条 card
    api = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?'+\
    'host_uid={}&offset_dynamic_id={}'.format(uid, offset)

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/'+\
        '537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
    }

    rjson = requests.get(api, headers=headers).json()

    if rjson['code'] != 0:
        print('CODE ERROR:', rjson['code'])
        print('MESSAGE', rjson['msg'], rjson['message'])
        return ([], 0)
    else:
        return (rjson['data'], rjson['data']['next_offset']) # next_offset 为 0 时表示没有动态了


def fetch_all_dynamic(uid, dest=None, offset=0, limit=0, delay=3, cover=False):
    """
    获取指定用户的所有动态文本（不包含专栏）并保存至本地，可以设置动态起始偏移和获取最大页数
    Args:
        uid:  用户id
        dest: 保存到本地的文件名，默认用 uid 替代
        offset: 起始偏移（暂且这样称呼），默认不偏移
        limit: 最大请求页数，默认无限制
        delay: 随机请求间隔延迟（为了防止被反爬建议不要设置太小），延迟范围 [1, delay]
        cover: 是否覆盖已有的同名文件，默认为否，也就是如果文件已存在则在文件末尾追加内容

    Returns:
        动态文本列表
    """

    all_dynamic_list = []

    dest = dest if dest else str(uid)
    if not dest.endswith('.txt'):
        dest += '.txt'

    mode = 'w' if cover else 'a'
    limit = limit if limit > 0 else -1 # else True -> 1，之前这样写循环只会跑一遍

    with open(dest, mode, encoding='utf-8') as f_str:
        while limit:
            limit -= 1

            data, offset = fetch_one_dynamic(uid, offset)
            print('请求:', offset)

            if offset == 0: # or not data 是错误的，因为可能有一整页专栏动态导致没有数据
                print('** offset 为 0 退出程序')
                break

            for text in get_dynamic_text(data):
                content = text.strip().upper()
                f_str.write(content+'\n')
                all_dynamic_list.append(content)

            f_str.flush()

            time.sleep(randint(1, delay))

    return all_dynamic_list
