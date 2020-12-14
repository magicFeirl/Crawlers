import re
from collections import defaultdict


def limit(filename, limit=1, reverse=False):
    """限制 sm2av 输出的重复数据个数，根据时间排序

    Args:
        filename: 要限制数据的 sm2av 的输出文件的文件名
        limit:    输出数据限制个数，默认为 1，也就是去重
        reverse:  是否按时间倒序排序数据，默认为 False
    """

    # 从 sm2av 的输出读取数据
    with open(filename, encoding='utf-8') as f:
        s = f.read()

    ns = s.split('\n')

    dc = defaultdict(list)

    # 去除 sm 号
    nns = [re.sub(' sm\d+ ', ' ', n).split(' ', 2) for n in ns]

    # 按排名作为 key 加入列表
    for c in nns:
        try:
            dc[c[0]].append([c[1], c[2]])
        except:
            print('Error')

    for k in dc.keys():
        # 根据 av 号长度排序，也就是根据时间排序
        dc[k].sort(key=lambda x:len(x[0]), reverse=reverse)
        # 在上一步的基础上按 av 号的值进行排序，值小的投稿时间早
        dc[k].sort(key=lambda x: x[0], reverse=reverse)
    ndc = defaultdict(list)

    # 取前 limit 个数据
    for k in dc.keys():
        ndc[k] = dc[k][:limit]

    # 输出，超过 980 字隔一行
    word_cnt = 0
    for k, v in ndc.items():
        for e in v:
            info = str(k) + ' ' + ' '.join(e)
            word_cnt += len(info) + 1

            if word_cnt >= 999:
                print()
                word_cnt = 0

            print(info)


limit('top100_out.txt', 3)
