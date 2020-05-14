import time
import requests

with open('cookie_a.txt') as f:
    urls = [line.replace('\n', '') for line in f.readlines()]

notfound = 0
found = 0
total = 0

start = time.time()

for url in list(urls):
    print(f'\rtotal: {total}', end='')
    r = requests.head(url)
    if r.status_code == 404:
        notfound += 1
    elif r.status_code == 200:
        found += 1
    total += 1

'''
total: 1411
2606.30886054039
notfound: 604 found: 808 total: 1412
'''

print()
print(time.time()-start)
print(notfound, found, total)
