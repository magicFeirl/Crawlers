# 使用 SCF 实现贴吧云签

> 继图片爬虫之外的爬虫入门作品

## 分析接口

经分析后得出贴吧签到只需要 BDUSS 这条 cookie，请求接口需要如下参数：

```python
{
	ie: 'uft-8' # 目测是吧名编码，在签到 Unicode 吧名时必须
	kw: '吧名' # 贴吧名
}
```

签到请求接口：https://tieba.baidu.com/sign/add

发送 post 请求之后会返回一条 json 表示状态。

那么现在的思路就很简单了，首先我们需要获取要签到的贴吧列表，然后遍历这个列表发送 post 请求进行签到即可。

## 获取贴吧列表

找到了一个获取贴吧列表的[接口](https://tieba.baidu.com/mo/q/newmoindex)，使用该接口可以很轻松的获取到吧信息，只须一个 BDUSS cookie。

## 获取贴吧列表（旧版）

这里发请求很容易，但是获取贴吧列表有些坑：

首先如果直接请求[我关注的吧](http://tieba.baidu.com/i/i/forum)是无法拿到数据的，就算把所有 cookie 带上也是一样的结果。抓包预览一下返回内容会发现该页面返回的其实是一个”外壳“，真正的贴吧列表在[管理我喜欢的吧](http://tieba.baidu.com/f/like/mylike)这里。再带上 BDUSS 发请求会发现还是无法获取贴吧列表，原因是获取贴吧列表还需要一个在 tieba.baidu.com 域名下名为 STOKEN 的 cookie，这条 cookie 的过期时间为 1 个月。注意不要和 passport.baidu 下的 STOKEN 搞混了，这条 cookie 的过期时间为 8 年，但如果想用这条 cookie 代替 tieba.baidu.com 域名下名为 STOKEN 是无法获取数据的。

有了以上分析（踩坑）就很容易构造请求头了：

```python
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
    'cookie': 'BDUSS={}; STOKEN={};'.format(BDUSS, STOKEN)
}
```

请求之后会返回一个包含吧名的表格，通过 xpath 很容易把吧名解析出来：

```python
xpath = '//td/a[not(@class)]/text()' # 吧名
last_page_xpath = '//div[@class="pagination"]/a/@href' # 尾页
```

之后就是重复请求页面直到到达尾页，获取贴吧列表的完整代码如下：

```python
def get_tb_list_by_req(BDUSS, STOKEN):
    	# 这里需要为期 1 个月的 STOKEN
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
            'cookie': 'BDUSS={}; STOKEN={};'.format(BDUSS, STOKEN)
        }

        idx = 1
      
        page = 'http://tieba.baidu.com/f/like/mylike?&pn={}'
        xpath = '//td/a[not(@class)]/text()'
        last_page_xpath = '//div[@class="pagination"]/a/@href'

        tb_list = []

        last_page = None

        while True:
            url = page.format(idx)
            idx += 1

            r = requests.get(url, headers=headers)

            html = fromstring(r.text)
            elems = html.xpath(xpath)

            if not last_page:
                last_page = html.xpath(last_page_xpath)

                if last_page:
                    last_page = last_page[-1]

            for e in elems:
                tb_list.append(e)

            # 如果有多页那么 last_page 不会为 None
            if not last_page or url.endswith(last_page):
                break

        return tb_list # 返回吧名列表
```

然后我们把吧名以 json 的格式存在本地，等到要用的时候直接从本地拿即可：

```python
def get_tb_list(BDUSS, STOKEN, username, refresh=False):
    '''使用 refresh 指定是否重新拉取贴吧列表'''
    
    # 先判断本地是否存在吧名列表，如果没有的话就拉取吧名
    if not os.path.exists(username) or refresh: 
        tb_list = get_tb_list_by_req(BDUSS, STOKEN)
        with open(username, 'w') as file:
            json.dump(tb_list, file)
    else:
        with open(username, 'r') as file:
            tb_list = json.load(file)

    return tb_list
```

自此获取贴吧列表的代码就结束了。

## 遍历贴吧列表签到

> 2020年7月18日 更新接口版源码

有了贴吧列表之后签到就只剩发送请求了，这部分很简单，因此直接上代码：

```python
import os
import json
import time
from random import randint

import requests


class SignTieba(object):
    def __init__(self, BDUSS):
        self.BDUSS = BDUSS

        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.58',
            'cookie': 'BDUSS={};'.format(BDUSS)
        }

    def sign(self, filename=None, refresh=False):
        api = 'https://tieba.baidu.com/sign/add'
        tb_list = self.get_ba_list(filename, refresh)

        for tb in tb_list:
            r = requests.post(api, data=dict(ie='utf-8', kw=tb), headers=self.headers)
            print(tb, r.json())

            time.sleep(randint(2, 3))

    def get_ba_list(self, filename=None, refresh=False):
        ba_list = []

        if not filename or refresh or not os.path.exists(filename):
            ba_list = self.get_ba_list_by_api()
        else:
            ba_list = self.get_ba_list_from_file(filename)

        return ba_list

    def get_ba_list_from_file(self, filename):
        with open(filename, 'r') as file:
            ba_list = json.load(file)

        return ba_list

    def get_ba_list_by_api(self):
        api = 'https://tieba.baidu.com/mo/q/newmoindex'
        rjson = requests.get(api, headers=self.headers).json()

        if rjson['error'] != 'success':
            print('请求接口出错')
            return []

        ba_list = []

        for ba in rjson['data']['like_forum']:
            ba_list.append(ba['forum_name'])

        return ba_list

    def save_ba_list(self, ba_list, filename):
        with open(filename, 'w') as file:
            json.dump(ba_list, file)

        return ba_list


if __name__ == '__main__':
    BDUSS = 'here' # 填入你的BDUSS
    SignTieba(BDUSS).sign()

```

自此本地版贴吧签到就完成了。

## 云签到

操作基本和本地签到一致，不过这里的 BDUSS 我推荐保存到环境变量里。

## 源码

[Github](https://github.com/magicFeirl/Crawlers/tree/master/SignTieba)

<span style="color:#fffff0;">看完了还是一头雾水？这不是你的问题，是作者太懒了。</span>