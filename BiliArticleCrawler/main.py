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

count = 0
counter = 0

def makedirs_if_not_exist(path):
    '''若文件夹不存在则创建文件保存文件夹'''

    if not os.path.exists(path):
        os.makedirs(path)

async def get_imgs_url(session,cv):
    '''创建相应专栏标题文件夹并返回专栏图片链接列表'''

    global count

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

        count = len(url_list)
        input(f'将下载 {count} 张图片，按任意键执行操作...')
        print(f'开始下载 {cv}...\n\n')

        dir_name = re.sub(r'[\\\\/:*?\"<>|]', '_', title)\
        .replace(' ', '') + '_' + cv

        path = os.path.join(os.getcwd(), dir_name, '')
        makedirs_if_not_exist(path)

        print('文件保存至：',path)

        os.chdir(path)

    return url_list



async def download(session, url):
    '''将图片保存至本地'''
    global counter

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

        counter += 1

        print(f'已下载 {counter}/{count} 张图片\r', end='')

async def main(cv):
    '''入口函数
    传入专栏cv号以下载专栏图片'''

    global count

    start = time.time()

    async with aiohttp.ClientSession() as session:
        img_urls = await get_imgs_url(session, cv)

        await asyncio.gather(*[download(session, url) \
            for url in img_urls])

    print('下载完成，耗时 {} s.共下载 {} 个文件'. \
        format(int(time.time()-start),count))

    input('按任意键退出...')

'''同一专栏下载速度：
线程池版 17s
asyncio版 14s'''

def show_help():
    print('Bilibili专栏图片下载器'.center(60,'='))
    print('使用方法:')
    print('1.输入专栏号下载专栏图片（如cv114514）')
    print('2.下载完成的图片会保存至 ./专栏标题_cv号 中')

if __name__ == '__main__':
    show_help()

    try:
        cv = input('\n输入专栏cv号:')
        asyncio.run(main(cv))
    except Exception as exce:
        print(str(exce))

