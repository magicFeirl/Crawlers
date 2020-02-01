'''然并卵的多协程解析json轮子'''

import asyncio
from time import time

from aiohttp import ClientSession, ClientTimeout


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '+
                  'AppleWebKit/537.36 (KHTML, like Gecko)'+
                  ' Chrome/79.0.3945.130 Safari/537.36'
}


class Downloader():

    def __init__(self, url_list, max_conn_coro=5, max_download_coro=10):
        self.url_list = url_list
        self.max_conn = max_conn_coro
        self.max_download = max_download_coro

        pass

    async def run(self, parse_json_callback, download_callback, timeout=60, headers=HEADERS):
        timeout = ClientTimeout(total=timeout)
        async with ClientSession(timeout=timeout, headers=headers) as session:
            await Crawler(self.url_list, session, self.max_conn, self.max_download).\
                get_json(parse_json_callback, download_callback)


class Crawler():

    def __init__(self, url_list, session, max_conn_coro, max_download_coro):
        self.url_queue = asyncio.Queue()
        self.data_queue = asyncio.Queue()

        self.session = session
        self.max_conn = max_conn_coro
        self.max_download = max_download_coro

        for _ in url_list:
            self.url_queue.put_nowait(_)

        pass

    async def get_json(self, parse_json_callback, download_callback):
        '''获取json数据并传入回调函数'''

        async def inner(self):
            while True:
                url = await self.url_queue.get()

                try:
                    async with self.session.get(url) as resp:
                        if resp.status is not 200:
                            print(f'Http status error:{resp.status}, url:{url}')
                        else:
                            resp_json = await resp.json()
                            print(f'Got {url} \n')
                            result = await parse_json_callback(resp_json, self.url_queue)
                            for url in result:
                                self.data_queue.put_nowait(url)
                except asyncio.TimeoutError:
                    print(f'Get {url} timeout')
                except asyncio.CancelledError:
                    raise
                except Exception as exception:
                    print('Get json error:', exception)
                finally:
                    self.url_queue.task_done()

        tasks = []
        for _ in range(self.max_conn):
            tasks.append(asyncio.create_task(inner(self)))
            await asyncio.sleep(0)

        for _ in range(self.max_download):
            tasks.append(asyncio.create_task(download_callback(self.data_queue)))
            await asyncio.sleep(0)

        await self.url_queue.join()
        await self.data_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)


async def download(data_queue):
    while True:
        url = await data_queue.get()
        print(url)
        data_queue.task_done()


async def clear_queue(queue):
    '''清空队列，当获取到空json数据时使用'''

    while True:
        queue.task_done()
        await queue.get()


async def parse_json(resp_json, url_queue):
    '''解析JSON回调函数
    参数：获取的JSON URL队列
    返回值：解析完毕的数据列表
    '''

    items = resp_json['data']['items']

    if len(items) == 0:
        await clear_queue(url_queue)

    pics = []
    for item in items:
        if 'pictures' in item:
            for pic in item['pictures']:
                pics.append(pic['img_src'])

    return pics


async def main():
    api = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list'+\
          '?uid={}&page_num={}&page_size=20'

    url_list = [api.format('0', i) for i in range(1, 400)]

    await Downloader(url_list, max_conn_coro=40, max_download_coro=200).\
        run(parse_json, download)

    pass

if __name__ == '__main__':
    st = time()
    asyncio.run(main())
    print(f'Done {time() - st}')