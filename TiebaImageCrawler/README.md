## 贴吧图片爬虫

其实并没有什么爬取贴吧图片的需求，但是搞算法又搞不懂（DP 随缘），为了消磨时间还是写了个图片爬虫。

记得最开始写爬虫还是在 JAVA 里用正则表达式提取 URI，JAVA 的代码量就不谈了，那时也不知道 JSOUP 之类的轮子，线程池用的也不是很熟练，HTTP 相关的知识更是一窍不通，现在想来还是走了不少弯路——人生苦短，我用Python。

当时就写过贴吧的图片爬虫，现在用 Python 重写一遍，也算是不忘初心吧（）。

## 例子

```python
import asyncio

from downloader import Downloader

# 自定义的下载回调函数
# uris 为解析的图片列表，是必填项
# file_obj 是自定义的参数参数，需要在 crawler.download 中传入
async def save_to_text(uris, file_obj):

    for uri in uris:
        print(uri)
        print(uri, file=file_obj)


async def main():
    crawler = Downloader()

    with open('tieba1.txt', 'w') as file_obj:
        await crawler.download('6099119702', # 帖子id
        save_to_text, # 下载回调
        begin=1, end=1, corou_num=1, # 下载起始页、结束页、并发请求数
        args=(file_obj,)) # 参数


if __name__ == '__main__':
    asyncio.run(main())

```

## 更新

### 2020年6月20日14:00:49

给代码加了点注释。

### 2020年5月5日23:08:35

本以为很简单，于是上手一气呵成打完代码，结果调试的时候 Bug 满天飞。