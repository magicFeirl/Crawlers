import re
import asyncio

from lxml.html import fromstring

from crawler import Crawler
from config import Config


HOST = 'https://www.bilibili.com/read/{}'


class BiliArticleImgCrawler(Crawler):
    def __init__(self, cvs, config=None):
        '''传入 cv 号列表批量保存专栏文章图片链接'''
        urls = []
        # 当然也可以用 map
        for cv in cvs:
            if not cv.startswith('cv'):
                cv = 'cv' + cv
            urls.append(HOST.format(cv))

        super(BiliArticleImgCrawler, self).__init__(urls, config=config)

    async def onconnect(self, resp):
        title, img_urls = self.parse_url(await resp.text())
        article_url = str(resp.url)
        cv = article_url[article_url.rfind(r'/')+1:] # 提取 cv 号

        self.save_to_textfile(title, img_urls, cv)

    def save_to_textfile(self, title, urls, cv):
        '''将图片链接保存至文本文件'''
        output = re.sub(r'[\\\\/:*?\"<>|]', '_', title).replace(' ', '') + '_' + cv + '.txt'

        with open(output, 'w', encoding='utf-8') as file:
            for url in urls:
                uri = 'https:' + url
                print(uri)
                print(uri, file=file)
                file.flush()

    def parse_url(self, html):
        selector = fromstring(html)

        title = selector.xpath('//title/text()')[0]
        url_list = selector.xpath('//img/@data-src')

        return (title, url_list)


async def main():
    cv = ['6521528', '114514']
    crawler = BiliArticleImgCrawler(cv)
    await crawler.run()


if __name__ == '__main__':
    asyncio.run(main())
