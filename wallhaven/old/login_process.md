# 模拟wallhaven登录：

**步骤：**

1. 请求 https://wallhaven.cc/login
2. 获取请求页面中的token，可通过解析DOM获取
3. 使用 requests.cookies.get_dict() 请求返回的cookies
4. 发送post请求至https://wallhaven.cc/auth/login，并附带上一步获取的cookies，用户名、密码、token

**简单示例：**

```python
import requests
from bs4 import BeautifulSoup

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/76.0.3809.132 Safari/537.36'
        }

get_url = 'https://wallhaven.cc/login'
post_url = 'https://wallhaven.cc/auth/login'

r = requests.get(get_url)
r.encoding = 'utf-8'

bs = BeautifulSoup(r.text,'html.parser')

_token = bs.find(attrs={'name':'_token'}).get('value')

filed = {'username':'un', #填写用户名
        'password':'ps', #填写密码
        '_token':_token}

cookies = r.cookies.get_dict()

#登录成功
r = requests.post(post_url,data=filed,headers=headers,cookies=cookies)
```

## 注意事项：

发送请求时要注意请求头，不同的请求头返回的数据格式不同，如果请求头不对会导致无法获取数据。

> 默认请求头：content-type: application/x-www-form-urlencoded
>
> Chrome显示的Post参数格式为：Form Data

requests会自动处理重定向；

发送请求时，如果有params字段则requests会自动对参数进行编码，这可能会导致错误的结果（与网站URL编码格式不同）；

