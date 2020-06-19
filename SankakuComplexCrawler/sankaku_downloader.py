'''继承自 crawler_utils.Downloader 的下载器'''

import os
import asyncio

from crawler_utils import Downloader
import crawler_utils.save_files as cs


API = 'https://capi-v2.sankakucomplex.com/posts?page={}&limit={}&tags={}'


class SankakuDownloader(Downloader):
    def __init__(self, tag, frame_obj=None, dest=None, ccf=None, begin=1, end=1, limit=20):
        super(SankakuDownloader, self).__init__(ccf=ccf)

        urls = [
            API.format(pn, limit, tag)
            for pn in range(begin, end+1)
        ]

        self.dest = dest
        self.page_count = begin
        self.begin = begin
        self.end = end

        self.frame_obj = frame_obj

        if not self.dest:
            self.dest = os.getcwd() + '\\' + tag

        if not self.dest.endswith('\\'):
            self.dest += '\\'

        if not os.path.exists(self.dest):
            os.makedirs(self.dest)

        if frame_obj:
            frame_obj.SetStatusText('开始请求', 0)

        # print(self.dest)

        self.init_connect_queue(urls)
        # print(self.connect_queue)

    def get_filename(self, url):
        lidx = url.rfind('/') + 1
        ridx = url.rfind('?')

        return url[lidx:ridx]

    async def connect_callback(self, response):
        status = response.status
        if status == 200:
            try:
                rjson = await response.json()
                # 原网站更改了返回的JSON格式，现在参数超过最大offset值后会返回
                # {"success":false,"code":"offset_forbidden"}，并且状态码为 400
                # 原先会返回空列表，这里的逻辑还是留着以防万一
                if self.frame_obj:
                    self.frame_obj.SetStatusText(
                    f'{self.page_count}/{self.end} 页数据已请求', 1)

                if not rjson:
                    await self.clear_connect_queue()
                else:
                    for item in rjson:
                        if item['file_type'].startswith('image'):
                            uri = item['sample_url']
                            # 如果存在同名文件则不入队，先前会入队后再判断是否存在同名文件，造成多余请求
                            filename = self.get_filename(uri)
                            full_path = os.path.join(self.dest, filename)

                            if not os.path.exists(full_path):
                                await self.download_queue.put(uri)
                            else:
                                print(f'\n目标目录下已存在同名文件: {filename}', end='')
            except asyncio.TimeoutError:
                print('请求数据超时')
            except Exception as e:
                print(f'[ERROR] ConnectError: {e}')
        else:
            if status == 400:
                try:
                    r = await response.json()
                    if not r['success']:
                        await self.clear_connect_queue()
                except Exception as e:
                    print(f'[ERROR] JSON 转码失败: {e}')
            else:
                print(f'[ERROR] 连接 HTTP 状态码错误: {status}')

        self.page_count += 1

    async def download_callback(self, response):
        status = response.status
        if status == 200:
            url = str(response.url)
            filename = self.get_filename(url)

            if self.frame_obj:
                # print(url)
                img_list = self.frame_obj.img_list
                idx = img_list.InsertItem(img_list.GetItemCount(), filename)
                img_list.SetItem(idx, 1, '下载中')
            await cs.save_one(self.dest, filename, response)
            if self.frame_obj:
                img_list = self.frame_obj.img_list
                img_list.DeleteItem(idx)
        else:
            print(f'[ERROR] 下载图片状态码错误: {status}')
