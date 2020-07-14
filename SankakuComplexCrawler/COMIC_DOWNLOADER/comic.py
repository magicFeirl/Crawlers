'''
东拼西凑的漫画爬虫。
因为多协程保存的图片是无序的，所以查看图片时也是无序的。
该版本是单协程版，可以保证图片顺序，相应的如果不加端口下载速度会很慢。

2020年7月14日20:09:22
'''
import os
import asyncio

import aiohttp
from config import Config
from crawler import Crawler
from save_files import save_one


def mkdir(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

    if not folder.endswith('\\'):
        folder += '\\'

    return os.getcwd() + '\\' + folder


async def create_session(timeout):
    t = aiohttp.ClientTimeout(total=timeout)
    return aiohttp.ClientSession(timeout=t)


class ComicCrawler(Crawler):
    def __init__(self, comic_id, session, dest=None, port=None,
    base=0, begin=1, end=1, config=None):
        '''
        传入漫画id、session、目标文件夹（可选）本地代理端口（可选）、
        图片命名基数（可选）、起始页（可选）、结束页（可选）、配置（可选）下载漫画
        '''

        if begin > end:
            end = begin

        api = 'https://capi-v2.sankakucomplex.com/posts?tags=pool%3a{}&page={}&limit=20'
        urls = [api.format(comic_id, idx) for idx in range(begin, end+1)]
        super().__init__(base_urls=urls, config=config)

        if port:
            self.proxy = f'http://127.0.0.1:{port}'
        else:
            self.proxy = None

        if not dest:
            dest = str(comic_id)

        self.dest = mkdir(str(dest))

        self.session = session
        self.cnt = base + 1

        print('爬虫已启动')

    async def onconnect(self, resp):
        rjson = await resp.json()

        if not rjson:
            await self.clear_queue(self.connect_queue)
        else:
            for item in rjson:
                file_type = item['file_type']
                if file_type.startswith('image'):
                    uri = item['sample_url']
                    suffix = file_type[file_type.find('/')+1:]

                    async with self.session.get(uri, proxy=self.proxy) as resp:
                        print(f'Downloading {self.cnt}')
                        await save_one(self.dest, str(self.cnt) + '.' + suffix, resp)
                        self.cnt += 1

async def main():
    config = Config(connect_num=1, download_num=1)
    cid = '漫画id'
    port = None # 端口

    async with await create_session(120) as session:
        CC = ComicCrawler(cid, session, port=port,
        config=config, begin=2, base=20)

        await CC.run() # 给连接回调传参


if __name__ == '__main__':
    evt_loop = asyncio.get_event_loop()
    evt_loop.run_until_complete(main())
