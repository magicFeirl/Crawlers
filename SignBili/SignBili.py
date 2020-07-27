"""
    一个类似云签的脚本，实现了 B 站直播间签到、每日登录、每日观看视频、每日分享视频功能

    推荐放到 SCF 上定时执行
"""

import requests


# CTRN43062 的 cookie
# 填入你的 SESSDATA 和 bili_jct
SESSDATA = '4a39e976%2C1610683388%2Cae5b1*71'
bili_jct = '8dccc4234e1ccb01465e30da694eb181'


class SignBili(object):
    def __init__(self, SESSDATA, bili_jct):
        """传入你的 SESSDATA 和 bili_jct 两个 cookie，
        注意在 cookie 的 180 天过期时间之前更新 cookie"""

        self.SESSDATA = SESSDATA
        self.bili_jct = bili_jct
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'origin': 'https://www.bilibili.com',
            'referer': 'https://www.bilibili.com',
            'cookie': 'SESSDATA={}; bili_jct={};'.format(SESSDATA, bili_jct)
        }

    def prt_err_msg(self, res, expectation):
        if res['code'] != expectation:
            print('ERROR:', res['message'])
        else:
            print('SUCCESS')

    def sign_live(self):
        """直播间签到"""

        api = 'https://api.live.bilibili.com/xlive/web-ucenter/v1/sign/DoSign'

        res = requests.get(api, headers=self.headers).json()
        self.prt_err_msg(res, 0)

    def share_video(self, aid):
        """分享视频"""

        api = 'https://api.bilibili.com/x/web-interface/share/add'

        res = requests.post(api, data=dict(aid=aid, csrf=self.bili_jct),
        headers=self.headers).json()
        self.prt_err_msg(res, 0)

    def daily_task(self):
        """登录 & 观看视频"""

        h5 = 'https://api.bilibili.com/x/click-interface/click/web/h5'

        data = {
            'aid': '56804944',
            'cid': '99225805',
            'bvid': 'BV1dx411o78f',
            'mid': '343118157'
        }

        res = requests.post(h5, data=data, headers=self.headers).json()
        self.prt_err_msg(res, 0)

        # 观看视频的参数限制貌似较小
        heartbeat = 'https://api.bilibili.com/x/click-interface/web/heartbeat'
        data = {
            'aid': '1919810',
            'csrf': self.bili_jct
        }

        res = requests.post(heartbeat, data=data, headers=self.headers).json()
        self.prt_err_msg(res, 0)

    def run(self):
        """运行所有日常任务"""

        print('直播间签到:')
        self.sign_live()
        print('分享视频:')
        self.share_video('114514') # 同一个视频每天可以分享一次，多于一次会报重复分享
        print('登录 & 观看视频:')
        self.daily_task()


if __name__ == '__main__':
    SignBili(SESSDATA, bili_jct).run()
