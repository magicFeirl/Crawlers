"""
DATE: 2020年4月16日13:16:57

requirements:

1. aiohttp
2. lxml
"""

import asyncio
import pickle
import time

import aiohttp
from lxml import etree

# 结论:
# aiohttp.CilentSesion 对象会自动记录请求返回的 cookies，无需手动添加

class Downloader(object):
    COOKIE_FILE = 'cookie.txt'

    def __init__(self, username, password, max_corou=5):
        """WALLHAVEN 下载器

        输入 WALLHAVEN 账号密码可下载 NSFW 图
        可自行设置最大并发数"""

        self.username = username
        self.password = password
        self.max_corou = max_corou

        self.uri_counter = 0
        self.url_queue = asyncio.Queue(maxsize=24*10)

    async def __login(self, session):
        """登录并保存 cookies 以便下次直接使用

        TODO：登录是否成功检查"""

        login_page = 'https://wallhaven.cc/login'
        login_url = 'https://wallhaven.cc/auth/login'

        token_xpath = '//input[@name="_token"]/@value'

        async with session.get(login_page) as resp:
            selector = etree.HTML(await resp.text())
            token = selector.xpath(token_xpath)[0]

            field = {
                'username': self.username,
                'password': self.password,
                '_token': token
            }

            cookies = {}

            async with session.post(login_url, data=field) as resp:
                resp.raise_for_status()
                cookies = resp.cookies

        with open(Downloader.COOKIE_FILE, 'wb') as f:
            pickle.dump(cookies, f)

        return cookies

    async def __get_cookies(self, session):
        """获取 COOKIES 并返回

        优先尝试从文件获取，如果文件不存在则尝试用指定的账户登录并返回 COOKIES"""

        cookies = {}

        try:
            with open(Downloader.COOKIE_FILE, 'rb') as f:
                cookies = pickle.load(f)
        except IOError:
            print('未找到 COOKIE 文件，尝试登录...')
            cookies = await self.__login(session)

        return cookies

    async def __create_tasks(self, session, url_list):
        """根据指定的并发数创建协程"""

        headers = {'User-Agent': 'wasp'}
        cookies = await self.__get_cookies(session)

        for url in url_list:
            self.url_queue.put_nowait(url)

        tasks = []

        for corou in range(self.max_corou):
            tasks.append(asyncio.create_task(self.__request_url(session, headers, cookies)))

        await self.url_queue.join()

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

    async def __request_url(self, session, headers, cookies):
        """协程消费者方法

        在此方法内处理uri
        """

        while True:
            url = await self.url_queue.get()

            try:
                async with session.get(url, headers=headers, cookies=cookies) as resp:
                    selector = etree.HTML(await resp.text())
                    uris = selector.xpath('//img[@class="lazyload"]/@data-src')

                    # 在这里处理URI
                    for uri in uris:
                        # uri 计数器自增1
                        self.uri_counter += 1
                        print(uri)

            except asyncio.CancelledError:
                raise
            except asyncio.TimeoutError:
                print(f'ERROR: Get {url} timeout')
            except Exception as error:
                print(f'ERROR: {error} TYPE: {type(error)}')
            finally:
                self.url_queue.task_done()

    async def download(self, tag, start=1, end=1, timeout=60):
        """下载指定 TAG 的内容

        可设置下载起始页以及下载结束页，目前没有对是否存在下载内容进行检查
        """

        timeout = aiohttp.ClientTimeout(total=timeout)

        url_list = [
        f'https://wallhaven.cc/search?q={tag}&purity=001&page={idx}'
        for idx in range(start,end+1)]

        start = time.time()

        async with aiohttp.ClientSession(timeout=timeout) as session:
            await self.__create_tasks(session, url_list)

        print('\n'*2)
        print(f'爬取 {tag} 标签结束。')
        print(f'耗时 {round(time.time()-start, 2)} s')
        print(f'共处理 {self.uri_counter} 条URI')
