import asyncio


class AsyncCrawler():

    def __init__(self, session, url_list, coro_num, callback, consume_num, consume_callback):
        self.session = session
        self.url_list = url_list
        self.coro_num = coro_num
        self.callback = callback

        self.consume_num = consume_num
        self.consume_callback = consume_callback

        self.url_queue = asyncio.Queue()
        self.consume_url_queue = asyncio.Queue()

        self.init_queue()

    def init_queue(self):
        for url in self.url_list:
            self.url_queue.put_nowait(url)

    async def get(self):
        while True:
            url =  await self.url_queue.get()

            try:
                async with self.session.get(url) as resp:
                    for i in await self.callback(await resp.text()):
                        await self.consume_url_queue.put(i)
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
        while True:
            url = await self.consume_url_queue.get()
            try:
                await self.consume_callback(url, self.session)
            except Exception as exce:
                print(f'Consume Url Error')
            finally:
                self.consume_url_queue.task_done()

    async def run(self):
        tasks = []

        for i in range(self.consume_num):
            task = asyncio.create_task(self.consume())
            tasks.append(task)
            await asyncio.sleep(0.0001)

        for i in range(self.coro_num):
            task = asyncio.create_task(self.get())
            tasks.append(task)
            await asyncio.sleep(0.0001)

        await self.url_queue.join()
        await self.consume_url_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
