# 默认请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36 Edg/81.0.416.53',
}


class Config(object):
    def __init__(self, headers=DEFAULT_HEADERS, connect_num=1,
    download_num=1, timeout=60, delay=1):
        '''客户端请求设置类'''
        self.headers = headers # 请求头
        self.connect_num = connect_num # 并发连接数
        self.download_num = download_num # 并发下载数

        self.timeout = timeout # 请求超时
        self.delay = delay # 请求延时
