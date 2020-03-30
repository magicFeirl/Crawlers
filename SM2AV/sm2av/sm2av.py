import re
import asyncio
from time import time
from random import randint


from lxml import etree


class SM2AV:

    def __init__(self, sm_list, session):
        self.session = session
        self.url_queue = asyncio.Queue()

        # 结果列表
        self.result_list = []
        # 找到的av号集合
        self.found_av = set()
        # 找到的sm号集合（站内）
        self.found_sm = set()
        # 所有sm号
        self.all = set(sm_list)
        # 去重后的sm号列表，其中元素作为检索参数
        self.sm_list = list(self.all)

        # 从Doge找到的sm号集合
        self.doge_found = set()
        # Doge检索结果
        self.doge_result_list = []

    async def __search(self, callback, *args, **kwargs):
        """异步URL队列"""

        while True:
            try:
                url = await self.url_queue.get()
                await callback(url, *args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                print(f'请求数据异常: {error} type: {type(error)}')
            finally:
                self.url_queue.task_done()

    async def __empty_queue(self):
        """清空url队列"""

        while not self.url_queue.empty():
            await self.url_queue.get()
            self.url_queue.task_done()

    def __put_in_queue(self, sm_list):
        for sm in sm_list:
            self.url_queue.put_nowait(sm)

    async def __create_tasks(self, coro_num, callback, *args, **kwargs):
        tasks = [asyncio.create_task(self.__search(callback, *args, **kwargs))
                 for _ in range(coro_num)]

        await self.url_queue.join()

        # 清空url队列
        await self.__empty_queue()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def search_from_bili(self, coro_num=1):
        """站内检索
        调用接口限制较小，但是请求多了照样会触发反爬，但是为了效率这里不做处理"""

        print('正在进行站内检索...')
        self.__put_in_queue(self.sm_list)

        async def inner(smn):
            api = 'https://api.bilibili.com/x/web-interface/search/type' + \
                  f'?keyword={smn}&search_type=video'

            # await asyncio.sleep(.5)
            async with self.session.get(api) as resp:
                result = await resp.json()

                if result['code'] == 0:
                    if 'result' not in result['data']:
                        return

                    data = result['data']['result']
                    li = []

                    if len(data):
                        self.found_sm.add(smn)

                    for r in data:
                        if r['aid'] not in self.found_av:
                            self.found_av.add(r['aid'])

                            aid = 'av' + str(r['aid'])
                            title = r['title']
                            li.append((smn, aid, title))

                    if len(li):
                        self.result_list.append(li)

        await self.__create_tasks(coro_num, inner)

    async def search_from_doge(self, delay=2):
        """外站检索
        请求过于频繁会导致503，所以就做成同步的了"""

        search_reg = re.compile(r'av\d+')
        sm_list = list(self.all-self.found_sm)
        self.__put_in_queue(sm_list)

        print('正在使用Doge进行检索...')

        async def inner(sm):
            url = f'https://www.dogedoge.com/results?q={sm}+site%3Awww.bilibili.com&lang=cn'

            try:
                async with self.session.get(url) as resp:
                    html = await resp.text()
                    xpath = '//a[@class="result__url js-result-extras-url"]/@href'
                    selector = etree.HTML(html)
                    href_list = selector.xpath(xpath)

                    if not len(href_list):
                        print(f'Doge 检索: {sm} 无返回列表，可能是由于访问过于频繁导致的。')

                    for href in href_list:
                        url = 'https://www.dogedoge.com/' + href
                        async with self.session.get(url, allow_redirects=False) as re_resp:
                            res = re_resp.headers.get('location')
                            # 排除带参数的URL
                            if res.find('?') == -1:
                                self.found_sm.add(sm)
                                res = re.search(search_reg, res)
                                if res and res[0] not in self.doge_found:
                                    self.doge_result_list.append((sm, res[0]))
                                    self.doge_found.add(res[0])
            except Exception as error:
                print(f'外站检索出错: {error}, type: {type(error)}')

            if len(sm_list) > 1:
                await asyncio.sleep(randint(1, delay))

        await self.__create_tasks(1, inner)

    async def search(self, coro_num=1, delay=2):
        start = time()

        print('请稍等...外站检索可能会花费更长时间...')
        await self.search_from_bili(coro_num)
        await self.search_from_doge(delay)
        print(f'检索完毕。耗时: {round(time() - start)} s')
        self.__get_result()

    def __get_result(self):

        if len(self.result_list):
            print('站内检索结果:')
            for info in self.result_list:
                print(info)
        else:
            print('站内检索无结果。')

        if len(self.doge_result_list):
            print('Doge检索结果:')
            for info in self.doge_result_list:
                print(info)
        else:
            print('Doge 检索无结果。')

        print(f'共 {len(self.all)} 个数据，检索到 {len(self.doge_found)+len(self.found_av)} 个相关视频。')

        not_found = self.all-self.found_sm

        if len(not_found):
            print(f'以下为未找到sm号集合：')
            print(not_found)
