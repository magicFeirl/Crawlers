import re
import asyncio


from addfav import AddFav


def read_av(filename):
    with open(filename, encoding='utf-8') as file:
        text = file.read()

    # av 号不能带 av
    return re.findall('av(.+)', text)

async def main():

    with open('cookies.txt') as f:
        cookies = f.read()

    A = AddFav('959696354', cookies)

    avlist = read_av('av.txt')
    # print(avlist)
    await A.run(avlist, 1)


if __name__ == '__main__':
    asyncio.run(main())

