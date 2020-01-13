import requests
from bs4 import BeautifulSoup
import time

#获取评论的API
base_url = 'https://api.bilibili.com/x/v2/reply'
#评论请求
action_url = 'https://api.bilibili.com/x/v2/reply/action'
#关注接口
modify_url = 'https://api.bilibili.com/x/relation/modify'
#请求头，需自行格式化添加

headers = {
    "Cookie":"CURRENT_FNVAL=16; stardustvideo=1; LIVE_BUVID=AUTO2215551599227052; im_notify_type_183454954=0; fts=1555161510; _uuid=DA7930C7-9626-93CD-4FFB-CE31CB74EB4B27537infoc; sid=8oll4t4f; rpdid=|(u||uk|YluJ0J'ullY)|R~|m; im_local_unread_183454954=0; buvid3=52C85C8A-6AA0-42F7-89EB-F99935027FCB155808infoc; im_seqno_183454954=1095; _uuid=8D1EBB36-8B97-6515-B739-2C8B41BF38E777567infoc; UM_distinctid=16de85790b092-0b61b092e925af-b363e65-100200-16de85790b1247; laboratory=1-1; DedeUserID=183454954; DedeUserID__ckMd5=6b8fed359c76ac54; SESSDATA=55d54b52%2C1580454175%2Cb515ae11; bili_jct=3baed42d2da1bad7d7b3633763d89db6; CURRENT_QUALITY=64; INTVER=1; bp_t_offset_183454954=340617745828994672; stardustpgcv=0606",

    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9,en;q=0.8",
    "Connection":"keep-alive",
    "Content-Length":"94",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "Host":"api.bilibili.com",
    "Origin":"https://www.bilibili.com",
    "Referer":"https://www.bilibili.com/bangumi/play/ep301016",
    "Sec-Fetch-Mode":"cors",
    "Sec-Fetch-Site":"same-site",
}

def exit(message):
    print(message)
    sys.exit()

class PostLike():

    def __init__(self,oid):
        #字典共同键值
        self.params = {
            'jsonp':'jsonp',
            'oid':oid,
            'type':1
        }

        #csrf关键key，需手动输入
        self.count = 1
        self.session = requests.Session()
        self.session.headers.update(headers)
        self.get_csrf()

    #从请求头中解析csrf参数
    def get_csrf(self):
        try:
            cookie = headers['Cookie'].split(';')

            for string in cookie:
                filed = string.strip()
                if 'bili_jct' in filed:
                    self.csrf = filed.split('=')[1]
                    print('csrf:',self.csrf)
                    return None
        except:
            pass
        else:
            if len(self.csrf) == 0:
                exit('错误的请求头参数：未含有csrf字段')

    def run(self,begin=0,pn=0,action=1,sort='0'):
        params = dict(self.params)
        params['sort'] = sort #设置排序方式。1 为热度排序 0 为时间排序

        for page in range(begin,pn+1):

            params['pn'] = page
            data = requests.get(base_url,params=params). \
            json()['data']['replies'] #解析评论ID

            for rpids in data:
                rpid = rpids['rpid']
                #print('rpid:',rpid)
                self.post_like(rpid,action)

    #点赞频率过快后目测需要等待60s
    def post_like(self,rpid,action):
        if self.count % 20 == 0:
            print('继续下一轮点赞，当前点赞人数:',self.count)

        params = dict(self.params)
        params['rpid'] = rpid
        params['action'] = action
        params['csrf'] = self.csrf

        while True:
            r = self.session.post(action_url,data=params).json()

            if r['code'] != 0:
                print('点赞频率过快',r['code'],r['message'])
                time.sleep(61)
            else:
                self.count+=1
                break

        del params


    def modify(self,fid,params):
        '''
            fid: 687808
            act: 1
            re_src: 14
            cross_domain: true
            csrf: d1f4e7763235b8df59b6d54322771143
        '''
        params['fid'] = fid
        params['act'] = 1
        params['re_src'] = 14
        params['cross_domain'] = True
        params['csrf'] = self.csrf

        json = self.session.post(modify_url,data=params).json()
        print(json)

#需要参数：视频av号 [点赞页数]

PostLike('79027200').run(pn=200)

