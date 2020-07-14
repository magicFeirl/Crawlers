import asyncio

from aiohttp import ClientSession, ClientTimeout

from config import Config


class Crawler(object):
    def __init__(self, base_urls, cqsize=0, dqsize=200, config=None, session=None):
        '''爬虫基类，需要复写连接、下载回调
        base_urls 一个 URL 列表，用来初始化连接队列
        cqsize    连接队列大小限制，默认无限制
        dqsize    下载队列大小限制，默认为最多存放 200 条 URL
        config    客户端配置，没有传入则使用默认配置

        session   默认 session
        '''

        # 如果没有传入配置则使用默认配置
        self.config = config if config else Config()

        self.connect_queue = asyncio.Queue(maxsize=cqsize)
        self.download_queue = asyncio.Queue(maxsize=dqsize)

        self.base_urls = base_urls
        self.base_url_num = len(base_urls)

        self.session = session

        # 初始化连接队列
        for url in base_urls:
            self.connect_queue.put_nowait(url)

    async def onconnect(self, resp, *args):
        '''连接回调，必需一个 session.get 的实例，其余参数可以在 run 方法中传入'''
        pass

    async def ondownload(self, resp, *args):
        '''下载回调，必需一个 session.get 的实例，其余参数可以在 run 方法中传入'''
        pass

    async def clear_queue(self, queue):
        '''清空队列，在请求到无效数据时可能会用到'''
        while not queue.empty():
            await queue.get()
            queue.task_done()

    async def connect(self, session, args):
        '''连接队列生产者方法'''
        while True:
            try:
                url = await self.connect_queue.get()

                async with session.get(url, headers=self.config.headers) as resp:
                    if args:
                        await self.onconnect(resp, *args)
                    else:
                        await self.onconnect(resp)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print('ConnectError:', e)
            else:
                if self.base_url_num > 1: # 链接总数大于 1 时才延迟
                    await asyncio.sleep(self.config.delay)

            self.connect_queue.task_done()

    async def download(self, session, args):
        '''下载队列消费者方法'''
        while True:
            try:
                url = await self.download_queue.get()

                async with session.get(url, headers=self.config.headers) as resp:
                    if args:
                        await self.ondownload(resp, *args)
                    else:
                        await self.ondownload(resp)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print('DownloadError:', e)
            else:
                await asyncio.sleep(self.config.delay)

            self.download_queue.task_done()

    async def cancel_tasks(self, tasks, return_exceptions=False):
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=return_exceptions)

    async def create_tasks(self, session, connect_cb_args, download_cb_args):
        '''创建生产者消费者'''
        connect_tasks = []
        download_tasks = []

        # 简单的特判，防止并发数大于链接总数
        if len(self.base_urls) < self.config.connect_num:
            corou_num = len(self.base_urls)
        else:
            corou_num = self.config.connect_num

        for n in range(corou_num):
            connect_tasks.append(asyncio.create_task(self.connect(session, connect_cb_args)))
            await asyncio.sleep(0)

        for n in range(self.config.download_num):
            download_tasks.append(asyncio.create_task(self.download(session, download_cb_args)))
            await asyncio.sleep(0)

        await self.connect_queue.join()
        await self.cancel_tasks(connect_tasks)

        await self.download_queue.join()
        await self.cancel_tasks(download_tasks)


    async def run(self, connect_cb_args=None, download_cb_args=None):
        '''启动爬虫，可传入元组作为回调参数'''
        if self.session:
            await self.create_tasks(self.session, connect_cb_args, download_cb_args)
        else:
            timeout = ClientTimeout(total=self.config.timeout)
            async with ClientSession(timeout=timeout) as session:
                await self.create_tasks(session, connect_cb_args, download_cb_args)



