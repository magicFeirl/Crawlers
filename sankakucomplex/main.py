'''下载器启动包'''

import asyncio

from downloader import Downloader


async def main():
    '''在此处设置下载参数'''
    # ainy77 rak_%28kuraga%29 toshi val_%28escc4347%29 satsuki_neko 已下载

    # 设置本地的全局代理
    proxy = "http://127.0.0.1:1081"
    # 下载标签名
    tag_name = ''
    # 保存文件夹名
    dir_name = ''

    # 漫画下载：pool%3A漫画id

    d = Downloader(tag_name, dir_name
    , 1, 20, proxy=proxy, timeout=5*60)

    await d.start()

if __name__ == '__main__':
    asyncio.run(main())

