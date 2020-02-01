'''下载器启动包'''

import asyncio

from downloader import Downloader


async def main():
    '''在此处设置下载参数'''

    d = Downloader('cookie(touhou)', 'c ', 1, 2)

    await d.start()

if __name__ == '__main__':
    asyncio.run(main())

