'''
    自动收藏脚本，很垃圾，但是够用
'''

import asyncio
import re


import aiohttp


class AddFav():

    def __init__(self, fid, cookies):
        '''传入收藏夹id和cookie'''
        self.fid = fid
        self.cookies = cookies

        self.csrf = self.get_csrf()

    def init_queue(self, rids):
        q = asyncio.Queue()

        for rid in rids:
            q.put_nowait(rid)

        return q

    def get_csrf(self):
        csrf = re.findall('bili_jct=(.+?);', self.cookies)[0];
        print(csrf)

        return csrf

    async def fav(self, session):

        while True:
            rid = await self.rid_queue.get()
            url = 'https://api.bilibili.com/x/v3/fav/resource/deal'
            try:
                data = {
                    'rid': rid,
                    'type': '2',
                    'add_media_ids': self.fid,
                    'del_media_ids': '',
                    'jsonp': 'jsonp',
                    'csrf': self.csrf
                }

                headers = {
                    'referer': 'https://www.bilibili.com/',
                    'User-Agent': 'wasp',
                    'Cookie' : self.cookies
                }

                async with session.post(url, data=data, headers=headers) as resp:
                    print(await resp.text())

                await asyncio.sleep(.3)
            except Exception as error:
                print(error)
                print(type(error))
            finally:
                self.rid_queue.task_done()

    async def run(self, rids, coro_num):
        '''传入av号和并发收藏数进行自动收藏'''
        tasks = []

        self.rid_queue = self.init_queue(rids)

        async with aiohttp.ClientSession() as session:
            for n in range(coro_num):
                tasks.append(asyncio.create_task(self.fav(session)))
                await asyncio.sleep(0)

            await self.rid_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
