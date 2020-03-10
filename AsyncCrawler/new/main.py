import asyncio

import aiohttp

from aio_crawler import AsyncCrawler

# 请求回调函数必须为协程，且至少含有一个接受请求返回文本的参数
# 返回值：处理后的数据，清空队列的旗标
async def get(text, *args, **kwargs):
    print(args, kwargs)
    return text, False

# 处理回调函数必须为协程，且至少含有一个接受请求回调处理后数据的参数
async def prt(result):
    print(result)

async def main():
    ulist = ['https://www.baidu.com' for _ in range(1)]

    async with aiohttp.ClientSession() as session:
        crawler = AsyncCrawler(ulist, session, 1, 1)
        crawler.set_req_callback(target=get, args=('12', ), kwargs={'filename': '1.txt'})
        crawler.set_pro_callback(target=prt)

        await crawler.run()


if __name__ == '__main__':
    asyncio.run(main())
