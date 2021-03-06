# GelbooruDownloader

> 已经实现了 GUI，并且将解析网页改成了调用接口，所以下面这段可以忽视了。

用自写轮子写的图片爬虫。

通过将图片链接保存至本地以提升速度，至于保存图片可以通过 IDM 批量下载。

缺陷是会有部分图片404，为图片后缀与原网站 URL 不同导致。

这里可行的解决方法有:

1. 先对链接发送 head 请求，判断图片是否存在，不存在就改后缀
2. 请求每个图片对应的 post，直接获取原图 URI

两种方法都挺简单，但是这也意味着会对服务器造成更大的负担。

## 示例

![example](./example.jpg)

## 更新

### 2020年7月16日

把底边边距调小了点，同时设置窗口不可改变大小。

### 2020年6月23日

实现了 GUI。目前在输出文件名上还有问题，一些特殊符号在 Windows 下不能作为输出文件名这个问题没有解决。

### 2020年6月22日

逛了下 wiki 发现 Gelbooru 是提供 API 的（貌似很多这种图站都有提供 API），那么现在程序就要改一下了。

等考试考完再说吧。（懒）

### 2020年6月16日

隔了快一个月，原网站仍然会不时更换 CSS 样式。

不过发现页面内有class属性的img标签就是页面显示的全部图片，于是再次修改xpath。

对于 404 的问题还是没有结局，也懒得去解决了。

### 2020年5月17日 

原网站更换了 CSS 样式，导致之前的 xpath 失效，现已修复。

