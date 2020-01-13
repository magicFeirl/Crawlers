import requests

url = 'https://api.bilibili.com/x/v2/reply/action'

cookie = '''
CURRENT_FNVAL=16; stardustvideo=1; LIVE_BUVID=AUTO2215551599227052; im_notify_type_183454954=0; fts=1555161510; sid=8oll4t4f; rpdid=|(u||uk|YluJ0J'ullY)|R~|m; im_local_unread_183454954=0; buvid3=52C85C8A-6AA0-42F7-89EB-F99935027FCB155808infoc; im_seqno_183454954=1095; _uuid=8D1EBB36-8B97-6515-B739-2C8B41BF38E777567infoc; CURRENT_QUALITY=112; UM_distinctid=16de85790b092-0b61b092e925af-b363e65-100200-16de85790b1247; finger=636f9d17; DedeUserID=183454954; DedeUserID__ckMd5=6b8fed359c76ac54; SESSDATA=e0141d55%2C1577799637%2Ceed309c1; bili_jct=d1f4e7763235b8df59b6d54322771143; laboratory=1-1; INTVER=1; stardustpgcv=0606; bp_t_offset_183454954=332677863123838619
'''

for string in cookie.split(';'):
    filed = string.strip()
    if 'bili_jct' in filed:
        print(filed.split('=')[1])
