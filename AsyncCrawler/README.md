### 迫真爬虫部，造轮子的里技

##### 介绍

`aio_crawler.py`实现了基本的多生产者消费者模型并发下载，使用`AsyncCrawler(session, url_list, coro_num, callback, consume_num, consume_callback)`类初始化一个`AsyncCrawler`对象

###### 参数列表

* `session`是进行连接的`ClientSession`对象，下载文件时也会用到

* `url_list`为要请求的URL列表

* `coro_num`最大并发**连接**数

* `callback`连接完毕后会返回获取到的文本，该函数为处理文本的回调，必须返回一个包含解析出的URL的列表对象，签名:`callback(text)`

* `consume_num`最大并发**下载**数

* `consume_callback`将`callback`获取到的URL加入下载队列，该函数用来处理下载URL，签名`consume_callback(url, session)`其中的session对象是传入构造方法的`session`对象


###### 方法

使用 `await crawler.run()`启动爬虫

基本上要实现三个函数：

1. 解析回调
2. 下载回调
3. 格式化初始链接URL

##### 示例

一个保存B站用户相簿图片URL的示例

```python
import asyncio
import json
import time

import aiohttp

import aio_crawler


async def parse_json(text):
    pictures = []

    items = json.loads(text)['data']['items']

    for item in items:
        if 'pictures' in item:
            for pic in item['pictures']:
                pictures.append(pic)

    return pictures


async def prt_url(url, session):
    print(url)
    pass # 在这里进行IO操作


def format_url(uid, begin, end):
    host = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list'

    return [host + f'?uid={uid}&page_num={idx}&page_size=20' for idx in range(begin, end+1)]


async def main():
    url_list = format_url('uid here', 1, 1)

    async with aiohttp.ClientSession() as session:
        crawler = aio_crawler.AsyncCrawler(session, url_list, 1, parse_json, 1, prt_url)
        await crawler.run() # 启动


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(f'耗时 {round(time.time() - start, 2)} s.')

```

#### 更新

##### 2020年2月27日

* 添加注释
* 新增获取到空列表清空请求队列功能
* 新增显示耗时功能
* 更新了示例文件