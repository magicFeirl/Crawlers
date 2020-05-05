import asyncio

import aiohttp

from parse import Parser

class Downloader():

    def __init__(self):
        self.parser = Parser()
        self.base_url = 'https://tieba.baidu.com/p/{tid}?pn={pn}'
        self.headers = {'User-Agent': 'wasp'}

        self.uri_queue = asyncio.Queue()

    async def get_img_uris(self, tie_url, session):
        xpath = '//img[@class="BDE_Image"][not(@ad-dom-img)]/@src'

        async with session.get(tie_url, headers=self.headers) as resp:
            img_uris = self.parser.parse_html(await resp.text(), xpath)

        return img_uris

    async def create_tasks(self, session, callback, corou_num, args):
        tasks = []
        for n in range(corou_num):
            task = asyncio.create_task(self.consumer(session, callback, args))
            tasks.append(task)
            await asyncio.sleep(0) # 保证入队 URL 有序

        return tasks

    async def consumer(self, session, callback, args):
        while True:
            url = await self.uri_queue.get()
            try:
                img_uris = await self.get_img_uris(url, session)
                if args is not None:
                    await callback(img_uris, *args)
                else:
                    await callback(img_uris)
            except Exception as error:
                print(error)
            finally:
                self.uri_queue.task_done()

    async def download(self, tid, callback, begin=1, end=1, corou_num=1, args=None):
        for idx in range(begin, end+1):
            url = self.base_url.format(tid=str(tid), pn=str(idx))
            self.uri_queue.put_nowait(url)

        async with aiohttp.ClientSession() as session:
            tasks = await self.create_tasks(session, callback,
            corou_num, args)

            await self.uri_queue.join()

            for task in tasks:
                task.cancel()

            await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == '__main__':
    pass
