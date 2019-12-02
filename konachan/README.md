# [KONACHAN.NET](http://konachan.net/)图片爬虫

爬取指定TAG的图片，base_url默认指定的是safe模式，要爬取Explicit模式请将base_url改为:

https://konachan.com/

还是惯例的那个，用Python写效率增加了很多。

用到了requests和BeautifulSoup，前者用来获取网页内容，后者负责解析获取到的网页内容。