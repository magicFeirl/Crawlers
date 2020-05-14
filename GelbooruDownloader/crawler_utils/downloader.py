import asyncio

from aiohttp import ClientSession, ClientTimeout
from .client_config import ClientConfig


class Downloader():
    def __init__(self, ccf=None, req_download=True):
        self.ccf = ccf if ccf else ClientConfig()

        # 设置是否请求下载队列中的 URL
        # 如果为 False 下载回调会接受一个 URL
        self.req_download = req_download
        self.connect_queue = asyncio.Queue()
        self.download_queue = asyncio.Queue()

    def init_connect_queue(self, urls):
        for url in list(urls):
            self.connect_queue.put_nowait(url)

    async def connect(self):
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
            finally:
                self.connect_queue.task_done()

    async def download(self):
        while True:
            url = await self.download_queue.get()

            try:
                if self.req_download:
                    async with self.session.get(url, headers=self.ccf.headers,
                    proxy=self.ccf.proxy) as resp:
                        await self.download_callback(resp)
                else:
                    await self.download_callback(url)
            except asyncio.CancelledError:
                break
            except asyncio.TimeoutError:
                print(f'[ERROR] 下载 {url} 超时')
            finally:
                self.download_queue.task_done()

    async def connect_callback(self, response):
        print('ConnectCallback:')
        print(response.status)

    async def download_callback(self, response):
        print('DownloadCallaback:')
        print(response.status)

    async def clear_connect_queue(self):
        while not self.connect_queue.empty():
            await self.connect_queue.get()
            self.connect_queue.task_done()

    async def create_tasks(self):
        tasks = []
        # print(self.ccf.max_connect_num, self.ccf.max_download_num)
        for i in range(self.ccf.max_connect_num):
            tasks.append(asyncio.create_task(self.connect()))
            await asyncio.sleep(0)

        for i in range(self.ccf.max_download_num):
            tasks.append(asyncio.create_task(self.download()))
            await asyncio.sleep(0)

        print('开始请求数据...')
        await self.connect_queue.join()
        await self.download_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def start(self):
        timeout = ClientTimeout(total=self.ccf.timeout)
        async with ClientSession(timeout=timeout) as session:
            self.session = session

            await self.create_tasks()
