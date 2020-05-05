import asyncio

from downloader import Downloader


async def save_to_text(uris, file_obj):

    for uri in uris:
        print(uri)
        print(uri, file=file_obj)

async def main():
    crawler = Downloader()

    # with open('tieba.txt', 'w') as file_obj:
    await crawler.download('6099119702',
    save_to_text, begin=1, end=1, corou_num=1, args=(1, 2))


if __name__ == '__main__':
    asyncio.run(main())
