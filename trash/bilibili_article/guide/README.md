# Python爬虫入门之解析DOM爬取bilibili专栏图片

*针对静态加载的内容，我们可以采取解析DOM的方法来获取想要爬取的内容，而动态加载的内容则可能需要分析接口、JavaScript等。在此我们先进行较为基础的静态网页内容抓取，学完就能应付大部分同类型网页了（心虚）。*

## 可能会用到的东西

> 要用到的库：
>
> 1. requests
> 2. bs4
>
> 安装方法： pip install <库名>
>
> 目标专栏：[cv4175765](https://www.bilibili.com/read/cv4175765)

分析网页部分使用的是Chrome，你也可以使用你喜欢的浏览器，目前大部分浏览器都支持查看网页源码的功能。

~~部分基础知识本文可能不会涉及，但是个人觉得并不影响写代码。~~

## 库文档

[requests中文文档](http://cn.python-requests.org/zh_CN/latest/user/quickstart.html)

[bs4中文文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc.zh)

**本文不会介绍BS或requests的具体使用方法，因为官方文档已经介绍的很详细了**

## 第一步：分析网页DOM，找出图片URL

​     第一步作为爬虫的关键，很多情况下是要费一些功夫的，不过由于本教程相对基础，所以这部分其实非常轻松——只需要将鼠标放在专栏图片上，点击右键`检查`，该元素在文档中的结构就一目了然了，如图所示：

![此处应该有张图]()

​    可以看到要找的`img`标签是作为类名为`img-box`的figure标签的子元素存在的，而其`data-src`中正是我们需要的图片URL。

​    那么我们可以先获取到所有类名为`img-box`的`figure`标签，然后遍历它们找出标签为`img`的子元素，提取子元素中属性为`data-src`的值。

## 第二步：编写代码获取图片URL

根据第一步的分析，使用BeautifulSoup可以很轻松地获取到类名为i`mg-box`的`figure`标签并提取其`img`子元素的属性值，代码如下:

```python
'''bilibili专栏图片爬虫V1.0'''
#Python推荐库导入顺序：内部 扩展 自定义
import urllib.parse as up 
import requests
from bs4 import BeautifulSoup

#推荐常量使用大写标识
HOST = 'https://www.bilibili.com/read/'

def get(url,params):
    '''模拟get请求'''
    
    r = None
    try:
		r = requests.get(url,params=params)
    except Exception as e:
        print('Error:',str(e))
	return r

def get_article_img(cv):
    '''输入专栏cv，获取图片'''
    
    url = up.urljoin(HOST,cv)
    text = get(url).text
    
    '''获取BeautifulSoup对象，参数：网页文本，解析器...
    	为了方便起见我们使用Python内置的html解析器
    '''
    soup = BeautifulSoup(text,'html.parser')
    #找到所有标签名为figure且类名为img-box的标签
    figs = soup.find_all('figure',attrs={'class':'img-box'})
    #一大串列表推导式（地狱绘图）
    url_list = [url.get('data-src') for url in [fig.find('img') \
     for fig in figs] if url]
    
    print(url_list) #['//i0.hdslb.com...',...]
    
get_article_img('cv4175765)
    
    
```

```python
#上部分列表推导式的展开：
figure = soup.find_all('figure',attrs={'class':'img-box'})

url_list = []
for fig in figs: #遍历所有符合条件的figure标签
    '''获取figure内的第一个img标签（原网页figure内仅有一个img标签，所以使用find方法)
    	如果要获取所有子元素，请使用.find_all()方法
    '''
    img = fig.find('img') 
    if img and img.get('data-src'): #判断img元素是否含有data-src属性，若没有，会抛出空对象异常 
        url_list.append(img.get('data-src'))
```

打印图片链接列表，你可能会发现部分图片可能并不符合你的要求（如专栏中的分隔栏图片），我们可以通过不同元素的属性来筛选它们：