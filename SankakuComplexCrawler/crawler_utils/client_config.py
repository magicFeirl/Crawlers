import os
import json

CONFIG_FILE = 'config.json'


def is_dict(obj):
    return isinstance(obj, dict)


def save_config(obj):
    config = obj
    if not is_dict(config):
        config = obj.__dict__

    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file)
        file.flush()


def update_config(config, **kwargs):
    if not is_dict(config):
        config.__dict__.update(kwargs)
    else:
        config.update(kwargs)


def get_config():
    if not os.path.exists(CONFIG_FILE):
        print('Config does not exist')
        config = ClientConfig()
        save_config(config)
        return config
    else:

        try:
            with open(CONFIG_FILE, 'r') as file:
                config = json.load(file)
        except IOError as e:
            print(f'[ERROR] 读取配置文件失败: {e}')
        except json.decoder.JSONDecodeError as e:
            print(f'[ERROR] JSON解码失败: {e}')
        except Exception as e:
            print(f'[ERROR] 获取配置异常: {e}')
        else:
            return ClientConfig(config.get('timeout', 2*60),
                    config.get('headers', 'wasp'),
                    config.get('port', ''),
                    config.get('max_connect_num', 5),
                    config.get('max_download_num', 100))

        config = ClientConfig()
        save_config(config)
        return config


class ClientConfig():
    def __init__(self, timeout=2*60, headers=None, port='',
    max_connect_num=5, max_download_num=100):
        self.proxy = None
        self.timeout = timeout

        self.headers = headers
        self.port = port

        if not self.headers:
            self.headers = {'User-Agent': 'wasp'}
        if port:
            self.proxy = f'http://127.0.0.1:{port}'

        self.max_connect_num = max_connect_num
        self.max_download_num = max_download_num
