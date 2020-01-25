import asyncio

from downloader import Downloader

async def main():
    d = Downloader('touhou', \
    'touhou1', 3, 5, timeout=3*60)

    await d.start()

if __name__ == '__main__':
    asyncio.run(main())
