### 迫真爬虫部，造轮子的里技

##### 介绍

`aio_crawler.py`实现了基本的多生产者消费者模型并发下载，使用`AsyncCrawler(session, url_list, request_callback, download_callback, is_clear_queue)`类初始化一个`AsyncCrawler`对象

###### 参数列表

* `session`进行连接的`ClientSession`对象，下载文件时也会用到
* `url_list`要请求的URL列表
* `request_callback`连接完毕后会返回获取到的文本，该函数为处理文本的回调，必须返回一个包含解析出的URL的列表对象，签名:`request_callback(text)`
* `download_callback`将`request_callback`获取到的URL加入下载队列，该函数用来处理下载URL，签名`download_callback(url, session)`其中的session对象是传入构造方法的`session`对象，由实例自动传入
* `is_clear_queue`请求回调返回空数据时是否清空生产者队列，默认为True

###### 方法

使用 `await crawler.run(request_coro, download_coro, display_time=True)`启动爬虫，

其中`request_coro`为**并发请求协程数**，`download_coro`为**并发下载协程数**，`display_time`默认在程序结束后显示运行耗时。

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
import aiofiles

import aio_crawler


async def parse_json(text):
    items = json.loads(text)['data']['items']

    return [pic['img_src'] for item in items if 'pictures' in item for pic in item['pictures']]


async def prt_url(url, session):
    print(url)


def format_url(uid, begin, end):
    host = 'https://api.vc.bilibili.com/link_draw/v1/doc/doc_list'

    return [host + f'?uid={uid}&page_num={idx}&page_size=20' \
    for idx in range(begin, end+1)]


async def main():
    url_list = format_url('2', 1, 1)

    async with aiohttp.ClientSession() as session:
        crawler = aio_crawler.AsyncCrawler(session, url_list, parse_json, prt_url)

        await crawler.run(1, 1)


if __name__ == '__main__':
    asyncio.run(main())
```

#### 更新

##### 2020年3月6日
* 更新介绍


##### 2020年2月27日

* 添加注释
* 新增获取到空列表清空请求队列功能
* 新增显示耗时功能
* 更新了示例文件