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

filed = {'username':'un',
        'password':'ps',
        '_token':_token}

cookies = r.cookies.get_dict()

#登录成功
r = requests.post(post_url,data=filed,cookies=cookies)


