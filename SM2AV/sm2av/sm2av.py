"""检索类
提供Bilibili内站检索以及DogeDoge外站检索方法"""

import re
import asyncio
from time import time
from random import randint
import traceback

from lxml import etree


class SM2AV:

    def __init__(self, sm_list, session, output_file=None):
        '''SM 号检索类
        sm_list： sm号列表
        session： 一个 aiohttp.ClientSession 实例
        output_file: 可选的输出文件对象'''

        self.session = session
        self.url_queue = asyncio.Queue()

        # 输出文件句柄
        self.output_file = output_file

        # 内站检索结果列表
        self.result_list = []
        # 找到的av号集合
        self.found_av = set()
        # 找到的sm号集合（站内）
        self.found_sm = set()
        # 所有sm号
        self.all = set(sm_list)
        # 去重后的sm号列表，其中元素作为检索参数
        # 2020年6月8日 更改，集合去重后的数据无序，因此这里还是改成列表了
        self.sm_list = list(enumerate(sm_list))

        # 从Doge找到的sm号集合
        self.doge_found = set()
        # Doge检索结果
        self.doge_result_list = []

    async def __search(self, callback, *args, **kwargs):
        """异步URL队列"""
        counter = 0

        while True:
            try:
                sm_info = await self.url_queue.get()
                await callback(sm_info, *args, **kwargs)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                traceback.print_exc()
                print(f'请求数据异常: {error} type: {type(error)}')
            finally:
                self.url_queue.task_done()

    async def __empty_queue(self):
        """清空url队列"""

        while not self.url_queue.empty():
            await self.url_queue.get()
            self.url_queue.task_done()

    def __put_in_queue(self, sm_list):
        """将sm号列表中的元素添加至url队列"""

        for sm in sm_list:
            self.url_queue.put_nowait(sm)

    async def __create_tasks(self, coro_num, callback, *args, **kwargs):
        """并发创建协程
          coro_num: 并发数
          callback: 回调
          *args, **kwargs: 回调函数参数"""

        tasks = [asyncio.create_task(self.__search(callback, *args, **kwargs))
                 for _ in range(coro_num)]

        await self.url_queue.join()

        # 清空url队列
        await self.__empty_queue()

        # 取消任务
        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def search_from_bili(self, coro_num=1):
        """站内检索
        调用接口限制较小，但是请求多了照样会触发反爬，这里加个.5s的延时，看有没有效果"""

        print('正在进行站内检索...')
        self.__put_in_queue(self.sm_list)

        async def task(sm_info):
            rank, sm = sm_info

            api = 'https://api.bilibili.com/x/web-interface/search/type' + \
                  f'?keyword={sm}&search_type=video'

            await asyncio.sleep(.5)
            async with self.session.get(api) as resp:
                result = await resp.json()

                if result['code'] == 0:
                    if 'result' not in result['data']:
                        return

                    data = result['data']['result']
                    li = []

                    # 之前只是简单地判断是否有返回搜索结果，导致搜索不同sm号会多次返回同一视频结果
                    # 最后会使外站检索出问题，因为found_sm中有部分实际没有找到的sm号
                    for r in data:
                        if r['aid'] not in self.found_av:
                            self.found_av.add(r['aid'])
                            self.found_sm.add(sm)

                            aid = 'av' + str(r['aid'])
                            title = r['title']
                            li.append([rank, sm, aid, title])

                    if li:
                        self.result_list.append(li)

        await self.__create_tasks(coro_num, task)

        if len(self.result_list):
            print('站内检索结果:')
            for info in sorted(self.result_list):
                for item in info:
                    res = ' '.join(list(map(str, item)))
                    print(res)
                    # 输出到本地
                    if self.output_file:
                        print(res, file=self.output_file)
        else:
            print('站内检索无结果。')

        print()

    async def search_from_doge(self, delay=2):
        """外站检索
        请求过于频繁会导致503，所以就做成同步的了"""

        search_reg = re.compile(r'av\d+')
        sm_list = list(self.all-self.found_sm)
        self.__put_in_queue(sm_list)

        # print('Doge =>', sm_list)

        print('正在使用DogeDoge进行检索...')

        async def task(sm):
            # +site%3Awww.bilibili.com& 关于网站精确检索貌似会影响结果的准确性，所以去掉了
            # 这里只保留检索中文结果
            url = f'https://www.dogedoge.com/results?q={sm}&lang=cn'

            try:
                async with self.session.get(url) as resp:
                    html = await resp.text()

                    selector = etree.HTML(html)
                    # 获取所有包含搜索结果的a标签
                    tag_a = selector.xpath('//a[@class="result__url js-result-extras-url"]')
                    # titles = selector.xpath('//a[@class=result__a]')

                    if not tag_a:
                        # print(f'DogeDoge 检索: {sm} 无返回列表，可能是因为访问过于频繁或检索无结果。')
                        # 如果503，把链接再次入队
                        if selector.xpath('//body/center/h1/text()'):
                            self.url_queue.put_nowait(url)

                    # 遍历结果标签
                    for a in tag_a:
                        # 先解析结果简介信息，排除非B站的链接，避免无用请求
                        # print(a, title)
                        res_domain = a.xpath('string(./span[@class="result__url__domain"])')

                        if res_domain and res_domain.find(r'video/av') != -1:
                            url = 'https://www.dogedoge.com/' + a.get('href')

                            async with self.session.get(url, allow_redirects=False) as re_resp:
                                res = re_resp.headers.get('location')

                                # 排除带参数的URL
                                if res and res.find('?') == -1:
                                    res = re.search(search_reg, res)
                                    # res[0] av号
                                    if res and res[0] not in self.doge_found:
                                        self.doge_result_list.append((sm, res[0]))
                                        self.doge_found.add(res[0])

                                        self.found_sm.add(sm)
            except Exception as error:
                print(f'外站检索出错: {error}, type: {type(error)}')

            if len(sm_list) > 1:
                # 这里将delay增长到2s，减少被503的可能
                await asyncio.sleep(randint(2, delay))

        await self.__create_tasks(1, task)

    async def search(self, coro_num=1, delay=3):
        """启动搜索
        coro_num: 站内检索并发数
        delay: 站外检索最大延时"""

        start = time()

        print('\n\n请稍等...外站检索可能会花费更长时间...')

        await self.search_from_bili(coro_num)
        await self.search_from_doge(delay)
        self.__get_result()

        print(f'\n检索完毕。\n耗时: {round(time() - start, 2)} s\n')

    def __get_result(self):

        if len(self.doge_result_list):
            print('Doge 检索结果:')
            for info in self.doge_result_list:
                print(info[0], info[1])
                # 输出到本地
                if self.output_file:
                    print(info[0], info[1], file=self.output_file)
        else:
            print('Doge 检索无结果。')

        print(f'\n共 {len(self.all)} 个数据，检索到 {len(self.doge_found)+len(self.found_av)} 个相关视频。')

        not_found = list(self.all-self.found_sm)
        print(f'\n{len(not_found)} 个数据未找到。')

        if len(not_found):
            print(f'以下为未找到sm号：')
            if self.output_file:
                print('\n'*2, file=self.output_file)
                print(f'{len(not_found)} 个数据未找到。以下为未找到sm号：',
                file=self.output_file)

            for item in not_found:
                print(item, end=' ')
                if self.output_file:
                    print(item, file=self.output_file)
