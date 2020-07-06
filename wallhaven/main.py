"""下载启动文件
"""

import asyncio

import aiohttp

from downloader import Downloader


async def main():
    # 填入你的 WALLHAVE 账号
    username = 'username'
    # 填入你的 WALLHAVEN 密码
    password = 'password'
    # 填入要下载的tag名
    tag = 'touhou'

    async with aiohttp.ClientSession() as session:
        await Downloader(username=username,
        password=password).download(tag, login=False)


if __name__ == '__main__':
    asyncio.run(main())
