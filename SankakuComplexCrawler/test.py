# aiohttp 代理测试
import asyncio

import aiohttp


async def connect(resp):
    # async with session.get('https://www.google.com', proxy=proxy) as resp:
    print(await resp.text())


async def main():
    proxy = 'http://127.0.0.1:1081'
    async with aiohttp.ClientSession() as session:
        async with session.get('https://capi-v2.sankakucomplex.com/posts?page=8&limit=5', proxy=proxy) as resp:
            print(await resp.text())



asyncio.run(main())
