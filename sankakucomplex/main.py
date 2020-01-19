import asyncio
import time
import os

import aiohttp
import aiofiles

CHUNK_SIZE = 64 * 1024

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}

def put_pq_data(pq, data):
    '''初始化生产者队列'''

    pq.put_nowait(data)

def make_dirs(folder):
    '''若文件夹不存在则创建文件夹，然后将当前目录地址设置为指定文件夹的地址'''

    if not os.path.exists(folder):
        os.makedirs(folder)

    os.chdir(folder)
    print(f'文件保存至：{os.getcwd()} 下')

async def get_json(pq, cq, session ,tags):
    '''获取json数据并将图片链接添加至cq队列中'''

    API = 'https://capi-v2.sankakucomplex.com/posts?page={}&limit=20&tags={}'

    while True:
        page_num = await pq.get()
        url = API.format(page_num, tags)

        print(f'GET {url}')

        async with session.get(url) as resp:
            rjson = await resp.json()

            if len(rjson) == 0:
                while True:
                    pq.task_done()
                    await pq.get()

            for item in rjson:
                if item['file_type'].startswith('image'):
                    img_url = item['sample_url']
                    await cq.put(img_url)

            pq.task_done()

async def download_img(cq, session):
    '''从队列中下载图片，若本地目录下已有同名文件则取消操作'''

    while True:
        img_url = await cq.get()

        lidx = img_url.rfind('/') + 1
        ridx = img_url.rfind('?')

        file_name = img_url[lidx:ridx]


        if not os.path.exists(file_name):
            async with aiofiles.open(file_name, 'wb') as f:
                async with session.get(img_url) as resp:
                    while True:
                        chunk = await resp.content.read(CHUNK_SIZE)

                        if not chunk:
                            break

                        await f.write(chunk)

        print(file_name,'Done')
        cq.task_done()


async def main(tags, folder="", start_page=1, end_page=2,\
                max_conn=10, max_download=60):
    '''入口函数

    参数：
        tags:        目标tag名，必填项

        folder:      保存文件的目录名，默认为tag名。
        start_page:  下载起始页，默认值为1。一般情况下每页有20张图片。
        end_page:    下载结束页，默认值为2.

        max_conn:    同时请求json的最大协程数，如果下载页数小于默认值10，则最大协程数为下载页数
        max_download 同时下载文件的最大协程数，默认值为60

        下载范围：
        [start_page, end_page]
    '''

    pq = asyncio.Queue()
    cq = asyncio.Queue()

    tasks = []

    folder = tags if folder == "" else folder
    make_dirs(folder)

    total_page = end_page - start_page + 1
    max_conn = total_page if max_conn > total_page else max_conn

    max_download = total_page * 20 \
    if max_download > total_page *20 else max_download

    print(f'将启动 {max_conn} 条协程请求数据, {max_download}条协程下载文件')

    for _ in range(start_page, end_page+1):
        put_pq_data(pq, _)

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        for _ in range(max_conn):
            task = asyncio.create_task(get_json(pq, cq, session, tags))
            tasks.append(task)
            await asyncio.sleep(.001)

        for _ in range(max_download):
            task = asyncio.create_task(download_img(cq, session))
            tasks.append(task)

        print('初始化完毕')
        await pq.join()
        print('请求完毕')
        await cq.join()
        print('下载完毕')

    for task in tasks:
        task.cancel()


if __name__ == '__main__':
    tags = 'ke-ta+order%3Aquality+rating%3Ae'

    s = 1
    e = 3

    start = time.time()

    asyncio.run(main(tags, start_page=s, end_page=e))

    print(f'Done {time.time() - start} s')
