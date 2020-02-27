import asyncio
import json
import time

import aiohttp

import aio_crawler


async def parse_json(text):
    pictures = []

    items = json.loads(text)['data']['items']

    for item in items:
        if 'pictures' in item:
            for pic in item['pictures']:
                pictures.append(pic)

    return pictures


async def prt_url(url, session):
    pass


def format_url(uid, begin, end):
    host = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list'

    return [host + f'?uid={uid}&page_num={idx}&page_size=20' for idx in range(begin, end+1)]


async def main():
    url_list = format_url('3798786', 1, 1)

    async with aiohttp.ClientSession() as session:
        crawler = aio_crawler.AsyncCrawler(session, url_list, 1, parse_json, 1, prt_url)
        await crawler.run()


if __name__ == '__main__':
    start = time.time()

    asyncio.run(main())

    print(f'耗时 {round(time.time() - start, 2)} s.')
