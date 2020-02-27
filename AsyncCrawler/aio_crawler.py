'''
requirement:
Python 3.7+
aiohttp
aiofiles
'''

import asyncio
import time

class AsyncCrawler():

    def __init__(self, session, url_list, coro_num, callback, \
    consume_num, consume_callback):
        '''callback 为处理请求队列返回数据的回调函数，须返回一个list
        consum_callback 下载回调'''

        self.session = session
        self.url_list = url_list
        self.coro_num = coro_num
        self.callback = callback

        self.consume_num = consume_num
        self.consume_callback = consume_callback

        self.url_queue = asyncio.Queue() # 请求队列
        self.consume_url_queue = asyncio.Queue() # 下载队列
        self.cq = True

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
            url =  await self.url_queue.get()

            try:
                async with self.session.get(url) as resp:
                    result = await self.callback(await resp.text())
                    if len(result):
                        for i in result:
                            await self.consume_url_queue.put(i)
                    elif self.cq:
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

    async def consume(self):
        '''一个简单的消费者协程'''

        while True:
            url = await self.consume_url_queue.get()
            try:
                await self.consume_callback(url, self.session)
            except Exception as exce:
                print(f'Consume Url Error:', str(exce))
                print(f'Error Type: {type(exce)}')
            finally:
                self.consume_url_queue.task_done()

    async def run(self, show_msg=True, clear_queue=True):
        '''启动请求和下载协程，阻塞至队列任务结束
        show_msg -> boolean 是否显示耗时
        clear_queue -> boolean 当请求队列获取到空列表数据时是否清空请求队列'''

        tasks = []
        self.cq = clear_queue

        start_time = time.time()
        for i in range(self.consume_num):
            task = asyncio.create_task(self.consume())
            tasks.append(task)
            await asyncio.sleep(0.0001) # 确保数据在加入队列时有序

        for i in range(self.coro_num):
            task = asyncio.create_task(self.get())
            tasks.append(task)
            await asyncio.sleep(0.0001)

        await self.url_queue.join()
        await self.consume_url_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        if show_msg:
            print(f'完毕。耗时 {round(time.time() - start_time, 2)} s.')
