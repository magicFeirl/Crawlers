'''require:
python3.7+
aiohttp
aiofiles
lxml
'''

import asyncio
import time
import os
import re

from lxml import etree
import aiohttp
import aiofiles

chunk_size = 32 * 1024
host = 'https://www.bilibili.com/read/'

def makedirs_if_not_exist(path):
    '''若文件夹不存在则创建文件保存文件夹'''

    if not os.path.exists(path):
        os.makedirs(path)

async def get_imgs_url(session,cv):
    '''创建相应专栏标题文件夹并返回专栏图片链接列表'''

    if not cv.startswith('cv'):
        cv = 'cv' + cv

    url = host + cv

    async with session.get(url) as resp:
        if not resp.status == 200:
            print('http 状态码错误:',resp.status)
            exit()

        html = await resp.text()
        selector = etree.HTML(html)
        title = selector.xpath('//title/text()')[0]
        url_list = selector.xpath('//img[@data-size]/@data-src')

        if len(url_list) == 0:
            print('专栏 {cv} 未发现图片，终止操作'.format(cv=cv))
            exit()

        input('将下载 {} 张图片，按任意键执行操作...'.format(len(url_list)))
        print('开始下载 {}...\r'.format(cv))

        dir_name = re.sub(r'[\\\\/:*?\"<>|]', '_', title)\
        .replace(' ', '') + '_' + cv

        path = os.path.join(os.getcwd(), dir_name, '')
        makedirs_if_not_exist(path)

        os.chdir(path)

    return url_list

async def download(session, url):
    '''将图片保存至本地'''

    file_name = url[url.rfind('/')+1:]

    if not os.path.exists(file_name):
        async with session.get('http:' + url) as resp:
            if not resp.status == 200:
                return

            async with aiofiles.open(file_name, 'wb') as f:
                while True:
                    chunk = await resp.content.read(chunk_size)

                    if not chunk:
                        break

                    await f.write(chunk)

async def main(cv):
    '''入口函数
    传入专栏cv号以下载专栏图片'''

    start = time.time()

    async with aiohttp.ClientSession() as session:
        img_urls = await get_imgs_url(session, cv)
        count = len(img_urls)

        await asyncio.gather(*[download(session, url) \
            for url in img_urls])

    print('下载完成，耗时 {} s.共下载 {} 个文件'. \
        format(int(time.time()-start)),count)

'''同一专栏下载速度：
线程池版 17s
asyncio版 14s'''

if __name__ == '__main__':

    asyncio.run(main('2432523'))
