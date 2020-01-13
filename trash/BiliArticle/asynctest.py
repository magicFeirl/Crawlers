import requests
from concurrent.futures import ThreadPoolExecutor

urls_list = [
    'https://www.baidu.com',
    'http://www.gaosiedu.com',
    'https://www.jd.com',
    'https://www.taobao.com',
    'https://news.baidu.com',
]
pool = ThreadPoolExecutor(5)

def request(url):
    response = requests.get(url)
    return response

def read_data(future,*args,**kwargs):
    response = future.result()
    response.encoding = 'utf-8'
    print(response.status_code,response.url)

def main():
    for url in urls_list:
        done = pool.submit(request,url)
        done.add_done_callback(read_data)

    print('123')

if __name__ == '__main__':
    main()
    pool.shutdown(wait=True)
