import os
import time
import asyncio

from lxml import html

from crawler_utils import Downloader
from crawler_utils import ClientConfig

# API 的 pid 下标是从 0 开始的

class GelBooruDownloader(Downloader):
    RATING_DICT = dict(a='', s='+rating:safe',
    q='+rating:questionalbe', e='+rating:explicit')

    HEADERS = {
        'User-Agent': 'wasp',
        'Cookie': 'fringeBenefits=yup',
        'referer': 'https://gelbooru.com'
    }

    def __init__(self, tags, destfile=None, begin=0, end=1,
    rating='e', max_connect_num=3, limit=40):
        ccf = ClientConfig(headers=self.HEADERS, max_connect_num=max_connect_num)

        super(GelBooruDownloader, self).__init__(ccf=ccf, req_download=False)

        self.tags = tags
        self.limit = limit

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
        API = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&'+ \
        'pid={}&tags={}{}&limit={}'

        return [API.format(pid, self.tags,
        self.RATING_DICT.get(rating, '+rating:explicit'), self.limit)
        for pid in range(begin, end)]

    async def connect_callback(self, response):
        status = response.status
        if status == 200:
            print(f'{response.url}')

            xpath = '//post/@sample_url' # 只下载 sample 质量的文件
            # 这里如果直接传 text lxml 会报 ValueError，貌似是因为 Unicode 的原因
            html = await response.read()
            urls = self.parse_html(html, xpath)
            # print(html)
            for url in urls:
                await self.download_queue.put(url)
            else:
                await self.clear_connect_queue()
        else:
            print(f'请求网页 HTTP 状态码错误:{status}')

    async def download_callback(self, url):
        print(url, file=self.output)

    def parse_html(self, text, xpath):
        selector = html.fromstring(text)
        return selector.xpath(xpath)

    def clear(self):
        if self.output:
            self.output.flush()
            self.output.close()


async def main():
    gbd = GelBooruDownloader('ke-ta+uncensored', destfile='keta_e_s',
    rating='e', max_connect_num=5, end=5)

    await gbd.start()
    gbd.clear()


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())

    print(f'Done {time.time()-start} s.')
    # gbd = GelBooruDownloader('ke-ta uncensored', end=10)
    # print(gbd.init_urls(1, 1, 'e'))
