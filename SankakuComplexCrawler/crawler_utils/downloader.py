'''实现了多生产者/消费者的基类'''

import asyncio

from aiohttp import ClientSession, ClientTimeout
from .client_config import ClientConfig


class Downloader():
    def __init__(self, ccf=None):
        self.ccf = ccf if ccf else ClientConfig()
        # 请求队列
        self.connect_queue = asyncio.Queue()
        # 下载队列
        self.download_queue = asyncio.Queue()

        print(self.ccf.proxy, self.ccf.port)

    def init_connect_queue(self, urls):
        '''传入请求链接初始化请求队列'''
        for url in list(urls):
            self.connect_queue.put_nowait(url)

    async def connect(self):
        '''队列请求回调'''
        while True:
            url = await self.connect_queue.get()

            try:
                async with self.session.get(url, headers=self.ccf.headers,
                proxy=self.ccf.proxy) as resp:
                    await self.connect_callback(resp)
            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                print(f'[ERROR] 请求 {url} 超时')
            except Exception as e:
                print(f'[ERROR] 请求回调发生异常 {str(e)} {type(e)}')
            finally:
                self.connect_queue.task_done()

    async def download(self):
        '''队列下载回调'''
        while True:
            url = await self.download_queue.get()

            try:
                async with self.session.get(url,
                headers=self.ccf.headers,
                proxy=self.ccf.proxy) as resp:
                    await self.download_callback(resp)
            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                print(f'[ERROR] 下载 {url} 超时')
            except Exception as e:
                print(f'[ERROR] 下载回调发生异常 {str(e)} {type(e)}')
            finally:
                self.download_queue.task_done()

    async def connect_callback(self, response):
        '''重写该函数以处理请求'''
        print('ConnectCallback:')
        print(response.status)

    async def download_callback(self, response):
        '''重写该函数以处理下载'''
        print('DownloadCallaback:')
        print(response.status)

    async def clear_connect_queue(self):
        '''特殊情况下使用，用于清空请求队列'''
        while not self.connect_queue.empty():
            await self.connect_queue.get()
            self.connect_queue.task_done()

    async def create_tasks(self):
        '''根据指定并发数启动协程'''
        tasks = []
        # print(self.ccf.max_connect_num, self.ccf.max_download_num)
        for i in range(self.ccf.max_connect_num):
            tasks.append(asyncio.create_task(self.connect()))
            await asyncio.sleep(0)

        for i in range(self.ccf.max_download_num):
            tasks.append(asyncio.create_task(self.download()))
            await asyncio.sleep(0)

        # print('开始请求数据...')
        await self.connect_queue.join()
        await self.download_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self):
        '''实例化 ClientSession 对象并等待协程队列处理完毕，调用该函数以启动下载器'''
        timeout = ClientTimeout(total=int(self.ccf.timeout))
        async with ClientSession(timeout=timeout) as session:
            self.session = session

            await self.create_tasks()


if __name__ == '__main__':
    pass
