'''命令行式下载器启动文件'''

import time
import asyncio

from sankaku_downloader import SankakuDownloader
from crawler_utils import ClientConfig


async def main():

    # ccf = ClientConfig(port=1081)
    # pool%3a漫画id 下载漫画
    sd = SankakuDownloader('amamitsu_kousuke+touhou+rating:e', dest='amamitsu_kousuke', begin=1, end=3, limit=20)

    await sd.start()

if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    print(f'\n下载完成 {time.time()-start_time}s.')
