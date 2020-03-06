'''
requirement:
Python 3.7+
aiohttp
aiofiles
'''

import asyncio
import time


class AsyncCrawler():

    def __init__(self, session, url_list, request_callback, \
    download_callback, is_clear_queue=True):
        '''request_callback 为处理请求队列返回数据的回调函数，须返回一个list
        download_callback 下载回调'''

        self.session = session
        self.url_list = url_list
        self.request_callback = request_callback
        self.download_callback = download_callback
        self.is_clear_queue = is_clear_queue

        self.url_queue = asyncio.Queue() # 请求队列
        self.download_url_queue = asyncio.Queue() # 下载队列

        self.init_queue()

    def init_queue(self):
        '''将初始请求URL放入请求队列'''

        for url in self.url_list:
            self.url_queue.put_nowait(url)

    async def clear_queue(self):
        '''清空请求队列'''

        while not self.url_queue.empty():
            await self.url_queue.get()
            self.url_queue.task_done()

    async def get(self):
        '''一个简单的生产者协程。

        该协程请求URL并获取数据然后将返回数据添加至下载队列，如果获取到的数据为空列表，
        则清空请求队列以结束后面的请求。
        可以通过设置run方法的clear_queue参数来取消默认行为。'''

        while True:
            url = await self.url_queue.get()

            try:
                async with self.session.get(url) as resp:
                    result = await self.request_callback(await resp.text())
                    if len(result) != 0:
                        for i in result:
                            await self.download_url_queue.put(i)
                    elif self.is_clear_queue:
                        # print('获取到空列表，清空队列')
                        await self.clear_queue()

            except asyncio.TimeoutError:
                print(f'Get {url} timeout')
            except asyncio.CancelledError:
                raise
            except Exception as exce:
                print(f'Get {url} Error:', str(exce))
                print(f'Error Type: {type(exce)}')
            finally:
                self.url_queue.task_done()

    async def download(self):
        '''一个简单的消费者协程'''

        while True:
            url = await self.download_url_queue.get()
            try:
                await self.download_callback(url, self.session)
            except asyncio.TimeoutError:
                print(f'Download {url} timeout')
            except asyncio.CancelledError:
                raise
            except Exception as exce:
                print(f'Download Url Error:', str(exce))
                print(f'Error Type: {type(exce)}')
            finally:
                self.download_url_queue.task_done()

    async def run(self, request_coro, download_coro, display_time=True):
        '''启动请求和下载协程，阻塞至队列任务结束
        show_msg -> boolean 是否显示耗时
        clear_queue -> boolean 当请求队列获取到空列表数据时是否清空请求队列'''

        tasks = []
        start_time = time.time()

        for _ in range(download_coro):
            task = asyncio.create_task(self.download())
            tasks.append(task)
            await asyncio.sleep(0.0001) # 确保数据在加入队列时有序

        for _ in range(request_coro):
            task = asyncio.create_task(self.get())
            tasks.append(task)
            await asyncio.sleep(0.0001)

        await self.url_queue.join()
        await self.download_url_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        if display_time:
            print(f'完毕。耗时 {round(time.time() - start_time, 3)} s.')
