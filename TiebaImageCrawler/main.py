import asyncio

from downloader import Downloader

# 自定义的下载回调函数
# uris 为解析的图片列表，是必填项
# file_obj 是自定义的参数参数，需要在crawler.download中传入
async def save_to_text(uris, file_obj):

    for uri in uris:
        print(uri)
        print(uri, file=file_obj)


async def main():
    crawler = Downloader()

    with open('tieba1.txt', 'w') as file_obj:
        await crawler.download('6099119702', # 帖子id
        save_to_text, # 下载回调
        begin=1, end=1, corou_num=1, # 下载起始页、结束页、并发请求数
        args=(file_obj,)) # 参数


if __name__ == '__main__':
    asyncio.run(main())
