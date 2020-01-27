'''
chan.sankakucomplex Images Downloader

API: https://capi-v2.sankakucomplex.com/posts?page={}&limit=20&tags={}

requier:

Python 3.7+
aiohttp
aiofiles
'''

import asyncio
import time
import os

import aiohttp
import aiofiles


def make_dirs(dir_name):
    '''若文件夹不存在则创建文件夹，然后将当前目录地址设置为指定文件夹的地址'''

    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    os.chdir(dir_name)

    print(f'文件保存至：{os.getcwd()} 下')


class Downloader():
    '''
    参数：
    必须项：

    tags:                  要下载的 tag 名
    dir_name:              图片保存文件夹名
    start_page:            起始页
    end_page:              结束页 范围[起始页, 结束页]

    自定义项：
    max_size:              下载队列大小，默认为存储 120 个图片URL
    max_conn_num:          接口最大同时连接数，默认为 10 条
    max_download_num:      最大同时下载图片数，默认为 120 个
    timeout:               连接-下载超时，默认为 3 分钟

    download_videos:       是否下载视频文件，默认为否
    file_quality:          下载的文件质量，默认为sample(0)，选择下载原图请输入1

    调用start方法启动下载器，需要用到asyncio

    暂且不知道会不会出现异常阻塞情况，如果程序超过 3 分钟没有响应就可以强制关闭了
    没有对函数进行参数类型检查，请确保输入的参数正确，否则可能会导致奇怪的行为（笑）
    '''

    FILE_QUALITY = ['sample_url', 'file_url']

    def __init__(self, tags, dir_name, start_page, end_page,
                 max_size=120, max_conn_num=10, max_download_num=120,
                 timeout=3*60, download_videos=False, file_quality=0):

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
        self.total_imgs = 0

        self.download_videos = download_videos
        self.file_quality = Downloader.FILE_QUALITY[file_quality]

        self.conn_queue = asyncio.Queue()
        self.url_queue = asyncio.Queue(maxsize=max_size)

        self.init_queue()

    def init_queue(self):
        '''初始化连接队列'''

        for pidx in range(self.start_page, self.end_page):
            self.conn_queue.put_nowait(pidx)

    def __help(self):
        '''提示函数'''

        print(f'将启动 {self.max_conn_num} 条协程请求数据,')
        print(f'{self.max_download_num} 条协程下载图片；')
        print(f'图片将保存至当前目录下的 {self.dir_name} 文件夹中；\n')
        print('提示：已经存在的重名图片不会重复下载。\n\n')

        input('按回车键开始下载...')

    async def conn(self, session):
        '''取出队列数据并连接相应接口，如果获取到空数据会清空后面的队列数据'''

        API = 'https://capi-v2.sankakucomplex.com/posts' + \
            '?page={}&limit=20&tags={}'

        while True:
            pidx = await self.conn_queue.get()

            try:
                url = API.format(pidx, self.tags)

                print(f'获取第 {pidx} 页数据...')
                async with session.get(url) as resp:
                    if resp.status is not 200:
                        raise Exception(f'Http状态码错误:{resp.status}')

                    img_infos = await resp.json()
                    print(f'成功获取第 {pidx} 页数据:')
                    if len(img_infos) == 0:
                        while True:
                            print(f'获取到空数据，取消第 {pidx} 页下载')

                            self.conn_queue.task_done()
                            pidx = await self.conn_queue.get()

                    for img_url in img_infos:
                        if self.download_videos:
                            await self.url_queue\
                                .put(img_url[self.file_quality])
                        elif img_url['file_type'].startswith('image'):
                            await self.url_queue\
                                .put(img_url[self.file_quality])

            except asyncio.TimeoutError:
                print(f'Error:第 {pidx} 页数据请求超时')
                self.conn_queue.task_done()
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
                self.total_imgs += 1

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

            except asyncio.TimeoutError:
                print(f'Error:下载图片 {file_name} 超时')
            except Exception as exce:
                print('Download img error:', exce)
            finally:
                self.url_queue.task_done()

    async def start(self):
        '''启动下载器'''

        tasks = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
            " AppleWebKit/537.36 (KHTML, like Gecko)" +
            " Chrome/79.0.3945.130 Safari/537.36"
        }

        self.__help()
        make_dirs(self.dir_name)

        timeout = aiohttp.ClientTimeout(self.timeout)
        async with aiohttp.ClientSession(headers=headers,
                                         timeout=timeout) as session:

            tasks.extend([asyncio.create_task(self.conn(session))
                          for _ in range(self.max_conn_num)])

            tasks.extend([asyncio.create_task(self.download_img(session))
                          for _ in range(self.max_download_num)])

            start_time = time.time()

            await self.conn_queue.join()
            await self.url_queue.join()

            for task in tasks:
                task.cancel()

            # 结束所有协程
            await asyncio.gather(*tasks, return_exceptions=True)

            print('*' * 60)
            print(f'Done {time.time() - start_time} s')
            print(f'共有 {self.total_imgs} 图片')
            print(f'成功下载 {self.counter} 张图片')
            print(f'失败 {self.total_imgs - self.counter} 张\n')

        input('按回车键退出...')
