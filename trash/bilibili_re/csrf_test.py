import requests

url = 'https://api.bilibili.com/x/v2/reply/action'

cookie = '''
'''

for string in cookie.split(';'):
    filed = string.strip()
    if 'bili_jct' in filed:
        print(filed.split('=')[1])
