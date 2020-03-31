"""SM2AV启动模块
requirements:
aiohttp
requests
lxml

Python 3.7+"""

import asyncio

from sm2av import menu


async def main():
    await menu.run()

if __name__ == '__main__':
    asyncio.run(main())
