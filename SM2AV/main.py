import asyncio

from sm2av import sm2av, smtools

# get_sm_from_desc(session, aid)
# get_sm_from_nico(session, uid) 用的是requests，aiohttp和httpx貌似默认不会走全局代理？


async def main():
    aid = '90891488'
    uid = '61506906'

    async with await smtools.get_session() as session:
        sm_list = await smtools.get_sm_from_text('sm25574396')
        await sm2av.SM2AV(sm_list, session).search()

if __name__ == '__main__':
    asyncio.run(main())