'''下载器启动包'''

import asyncio

from downloader import Downloader


async def main():
    '''在此处设置下载参数'''
    # ainy77 rak_%28kuraga%29 toshi val_%28escc4347%29 satsuki_neko 已下载

    d = Downloader('order:pool+pool:254804', '254804', 1, 4, timeout=5*60)

    await d.start()

if __name__ == '__main__':
    asyncio.run(main())

