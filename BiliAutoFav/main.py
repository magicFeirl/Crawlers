import re
import asyncio


from addfav import AddFav

# 从文本中读取 av 号
def read_av(filename):
    with open(filename, encoding='utf-8') as file:
        text = file.read()

    # av 号不能带 av
    return re.findall('av(\d+)', text)


async def main():

    # 读取本地 cookie
    with open('cookies.txt') as f:
        cookies = f.read()

    # 参数：收藏夹id、cookies
    A = AddFav('962977254', cookies)

    avlist = read_av('fsm.txt')
    # print(avlist)
    await A.run(avlist, 1) # 执行收藏
    # print(avlist)

if __name__ == '__main__':
    asyncio.run(main())

