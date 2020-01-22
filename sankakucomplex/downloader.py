import asyncio
import time
import os


import aiohttp
import aiofiles


class Downloader():
    '''chan.sankakucomplex 图片下载器
    参数：

    要下载的tag名
    图片保存文件夹名
    起始页
    结束页 范围[起始页, 结束页]

    下载队列大小，默认为存储   120 个图片URL
    接口最大同时连接数，默认为  6         条
    最大同时下载图片数，默认为 120        个
    连接-下载超时，默认为2分钟

    调用start方法启动下载器，需要用到asyncio

    暂且不知道会不会出现异常阻塞情况，如果程序超过3分钟没有响应就可以强制关闭了
    '''

    def __init__(self, tags, dir_name, start_page, end_page, \
    max_size=120, max_conn_num=6, max_download_num=120, timeout=2*60):

        pnum = end_page - start_page + 1

        self.tags = tags
        self.dir_name = dir_name
        self.start_page = start_page
        self.end_page = end_page+1
        self.max_conn_num = max_conn_num if pnum > \
        max_conn_num else pnum

        self.max_download_num = max_download_num if pnum * 20 > \
        max_download_num else pnum * 20

        self.timeout = timeout
        self.counter = 0

        self.conn_queue = asyncio.Queue()
        self.url_queue = asyncio.Queue(maxsize=max_size)

        self.init_queue()

    def init_queue(self):
        '''初始化连接队列'''

        for pidx in range(self.start_page, self.end_page):
            self.conn_queue.put_nowait(pidx)

    def make_dirs(self, dir_name):
        '''若文件夹不存在则创建文件夹，然后将当前目录地址设置为指定文件夹的地址'''

        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        os.chdir(dir_name)

        print(f'文件保存至：{os.getcwd()} 下')

    def __help(self):
        '''提示函数'''

        print(f'将启动 {self.max_conn_num} 条协程请求数据,', end='')
        print(f'{self.max_download_num} 条协程下载图片；')
        print(f'图片将保存至当前目录下的 {self.dir_name} 文件夹中；')
        print('提示：已经存在的重名图片不会重复下载。\n\n')

        input('按任意键开始下载...')

    async def conn(self, session):
        '''取出队列数据并连接相应接口，如果获取到空数据会清空后面的队列数据'''

        API = 'https://capi-v2.sankakucomplex.com/posts'+ \
        '?page={}&limit=20&tags={}'

        while True:
            pidx = await self.conn_queue.get()

            try:
                url = API.format(pidx, self.tags)

                print(f'Getting json {url}')
                async with session.get(url) as resp:
                    img_infos = await resp.json()

                    if len(img_infos) == 0:
                        while True:
                            print(f'获取到空数据，取消第 {pidx} 页下载')
                            self.conn_queue.task_done()
                            pidx = await self.conn_queue.get()

                    for img_url in img_infos:
                        if img_url['file_type'].startswith('image'):
                            await self.url_queue\
                                .put(img_url['sample_url'])

            except asyncio.CancelledError:
                raise
            except Exception as exce:
                print('Conn queue error:', exce)
            finally:
                if len(img_infos) is not 0:
                    self.conn_queue.task_done()

    async def download_img(self, session):
        '''从队列中下载图片，若本地目录下已有同名文件则取消操作'''

        while True:
            img_url = await self.url_queue.get()

            try:
                lidx = img_url.rfind('/') + 1
                ridx = img_url.rfind('?')
                file_name = img_url[lidx:ridx]

                print(f'Downloading: {file_name}')

                if not os.path.exists(file_name):
                    async with aiofiles.open(file_name, 'wb') as f:
                        async with session.get(img_url) as resp:
                            while True:
                                chunk = await resp.\
                                    content.read(64 * 1024)
                                if not chunk:
                                    break
                                await f.write(chunk)

                self.counter += 1

            except asyncio.CancelledError:
                raise
            except Exception as exce:
                print('Download img error:', exce)
            finally:
                self.url_queue.task_done()


    async def start(self):
        '''启动下载器'''

        tasks = []
        headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"+\
            " AppleWebKit/537.36 (KHTML, like Gecko)"+\
            " Chrome/79.0.3945.130 Safari/537.36"
        }

        self.__help()
        self.make_dirs(self.dir_name)

        timeout = aiohttp.ClientTimeout(self.timeout)
        async with aiohttp.ClientSession(headers=headers, \
            timeout=timeout) as session:
                tasks.extend([asyncio.create_task(self.conn(session))\
                for _ in range(self.max_conn_num)])

                tasks.extend([asyncio.create_task(self.download_img(session))\
                for _ in range(self.max_download_num)])

                start_time = time.time()

                await self.conn_queue.join()
                await self.url_queue.join()

                for task in tasks:
                    task.cancel()

                print(f'Done {time.time() - start_time} s')
                print(f'成功下载 {self.counter} 张图片')
