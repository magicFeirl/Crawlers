import os
import time
import asyncio

from lxml import etree

from crawler_utils import Downloader
from crawler_utils import ClientConfig

# //span[@class="thumb"]/a/img/@src

# 页数增长规律:
# 第一页从 0 开始，后一页为前一页页数+42
# 页数过大无法获取结果，目测页数在 400(16800) 页以内均可获得结果
# 当页数非 42 的倍数时页数会被除以 42 向下取整（目测）
# 当解析链接列表为空或超过用户页数限制时停止队列
# Gelbooru 的图片链接可以通过 IDM 下载，因此考虑把链接保存为文本
# 每页最多显示 42 张图
# 传入 Cookie: fringeBenefits=yup 可以下载所有图片（甚至不需要PHPSESSID...)
# 图片后缀不同会导致 404，可以用 head 请求参看图片类型，这里只下载 sample 质量的图片，后缀目测一致，且大小较小
# self.file_url = 'https://img2.gelbooru.com/images'

# 几十行代码摸了一上午...

# 发现页面有类的图片标签就是图片元素
# 以前的 xpath 写的太复杂了...
XPATH = '//img[@class]/@src'


class GelBooruDownloader(Downloader):
    RATING_DICT = dict(a='', s='+rating:safe',
    q='+rating:questionalbe', e='+rating:explicit')

    HEADERS = {
        'User-Agent': 'wasp', 'Cookie': 'fringeBenefits=yup',
        'referer': 'https://gelbooru.com'
    }

    def __init__(self, tags, destfile=None, begin=1, end=1, rating='e', max_connect_num=3):
        ccf = ClientConfig(headers=self.HEADERS, max_connect_num=max_connect_num)

        super(GelBooruDownloader, self).__init__(ccf=ccf, req_download=False)

        self.tags = tags

        self.init_output(destfile)
        self.init_connect_queue(self.init_urls(begin, end, rating))
        # print(self.connect_queue)

    def init_output(self, destfile):
        if not destfile:
            f = self.tags
            if os.path.exists(f):
                f += '_' + str(int(time.time()))
            self.output = open(f+'.txt', 'w')
        else:
            if os.path.exists(destfile):
                destfile += '_' + str(int(time.time()))
            if not destfile.endswith('.txt'):
                destfile += '.txt'
            self.output = open(destfile, 'w')

    def init_urls(self, begin, end, rating):
        begin= (begin - 1) * 42
        end = end * 42

        return ['https://gelbooru.com/index.php?page=post&s=list&'
        'tags={}{}&pid={}'.format(self.tags,
        self.RATING_DICT.get(rating, '+rating:explicit'), pid)
        for pid in range(begin, end, 42)]

    async def connect_callback(self, response):
        status = response.status
        if status == 200:
            thumb_imgs = self.parse_html(await response.text(), XPATH)
            # print(thumb_imgs)
            if thumb_imgs:
                for img in thumb_imgs:

                    await self.download_queue.put(img)
            else:
                await self.clear_connect_queue()
        else:
            print(f'请求网页 HTTP 状态码错误:{status}')

    async def download_callback(self, url):
        # print(url)
        print(url.replace('thumbnail', 'sample'), file=self.output)

    def clear(self):
        if self.output:
            self.output.flush()
            self.output.close()

    def parse_html(self, text, xpath):
        selector = etree.HTML(text)
        return selector.xpath(xpath)


async def main():
    gbd = GelBooruDownloader('tksand', destfile='tksand',
    rating='e', max_connect_num=1)

    await gbd.start()
    gbd.clear()


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())

    print(f'Done {time.time()-start} s.')
    # gbd = GelBooruDownloader('ke-ta uncensored', end=10)
    # print(gbd.init_urls(1, 1, 'e'))
