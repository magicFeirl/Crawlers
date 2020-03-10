'''
requirement:
python 3.7+
aiphttp

[aiofiles]
'''

import asyncio

class AsyncCrawler():
    '''一个简单的并发爬虫类'''
    def __init__(self, url_list, session, req_coro, pro_coro):
        '''
            参数：
            请求URL列表
            aiohttp的ClientSession实例，可以自定义如超时等信息
            并发请求协程数
            并发处理协程数
        '''
        self.req_coro = req_coro
        self.pro_coro = pro_coro
        self.session = session

        self.req_queue = asyncio.Queue()
        self.pro_queue = asyncio.Queue()

        self.__init_queue(url_list)

    def __init_queue(self, url_queue):
        '''初始化请求队列'''
        for url in url_queue:
            self.req_queue.put_nowait(url)

    async def __clear_req_queue(self):
        '''清空请求队列'''
        q = self.req_queue

        while not q.empty():
            await q.get()
            q.task_done()

    async def __get(self):
        '''向服务器发起请求，并通过设置的请求回调将获取到的结果(文本)放入处理队列'''
        req_q = self.req_queue
        pro_q = self.pro_queue

        while True:
            url = await req_q.get()

            try:
                async with self.session.get(url) as resp:
                    result, clear = await self.req(await resp.text(), \
                    *self.req_args, **self.req_kwargs)

                    if clear and self.clear_when_empty:
                        await self.__clear_req_queue()
                    else:
                        await pro_q.put(result)
            except asyncio.TimeoutError:
                print('ReqError: 请求数据超时')
            except asyncio.CancelledError:
                raise
            except Exception as exce:
                print('ReqError:', str(exce))
                print('ReqError type:', type(exce))
            finally:
                req_q.task_done()

    async def __process(self):
        '''通过设置的回调处理请求返回的结果'''
        pro_q = self.pro_queue

        while True:
            result = await pro_q.get()
            try:
                await self.pro(result, *self.pro_args, **self.pro_kwargs)
            except Exception as exce:
                print('ProcessError:', str(exce))
                print('ProcessError type:', type(exce))
            finally:
                pro_q.task_done()

    async def __cancel_tasks(self, tasks):
        '''取消协程'''
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def run(self):
        '''启动爬虫'''
        req_tasks = [asyncio.create_task(self.__get()) \
        for _ in range(self.req_coro)]

        pro_tasks = [asyncio.create_task(self.__process()) \
        for _ in range(self.pro_coro)]

        await self.req_queue.join()
        await self.__cancel_tasks(req_tasks)

        await self.pro_queue.join()
        await self.__cancel_tasks(pro_tasks)

    def set_req_callback(self, target, args=(), kwargs={}, *, clear_when_empty=True):
        '''设置请求回调，通过该回调处理请求获取的数据并返回给处理队列
        请求回调函数必须为协程，且至少含有一个接受请求返回文本的参数
        返回值：处理后的数据，清空队列的旗标'''

        self.req = target
        self.req_args = args
        self.req_kwargs = kwargs
        self.clear_when_empty = clear_when_empty

    def set_pro_callback(self, target, args=(), kwargs={}):
        '''设置处理回调'''
        self.pro = target
        self.pro_args = args
        self.pro_kwargs = kwargs
