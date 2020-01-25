import asyncio

from downloader import Downloader

async def main():
    d = Downloader('touhou', 't1', 1, 2)

    await d.start()

if __name__ == '__main__':
    asyncio.run(main())
