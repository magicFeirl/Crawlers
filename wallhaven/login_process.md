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
r = requests.post(post_url,data=filed,cookies=cookies)
```



