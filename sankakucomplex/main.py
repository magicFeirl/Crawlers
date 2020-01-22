import asyncio

from download import Downloader

async def main():
    d = Downloader('tag_name', 'tag_name', 1, 1)
    await d.start()

if __name__ == '__main__':
    asyncio.run(main())
