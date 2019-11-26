'''
	作者：MagicFeirl
	时间：2019年11月26日18:09:47
	功能：下载bilibili用户动态图片
	编辑器：notepad++
'''

import requests
import json
import sys
import time

#基URL，请求参数：UID、起始动态ID（默认为0，即从最新的一条动态开始）
base_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history'

class Downloader:

	def __init__(self,uid):
		'''
			初始化下载器。
		
			uid:要抓取的动态的发送者。
		'''
		
		self.uid = uid
		self.is_get_profile = False
		self.offset = 0
		
	def get_json(self):
		'''
			获取请求的json。
		'''
		
		#构造请求参数
		params = {'host_uid':self.uid,
				'offset_dynamic_id':self.offset
		}
		
		try:
			json = requests.get(base_url,params=params).json()
			data = json['data'] 
			
			#若本轮动态不存在，退出程序
			if int(data['has_more']) != 1:
				raise Exception()
			
			#获取用户信息，仅获取一次
			if not self.is_get_profile:
				self.profile = data['cards'][0]['desc']['user_profile']
				self.is_get_profile = True
				
			return data['cards']
		except:
			print('无法解析该条Json。',
			'UID:'+str(self.uid),
			'拉取动态ID:'+str(self.offset),
			'\n可能的原因：',
			'1.用户不存在',
			'2.该用户未发布任何动态',
			'3.输入的拉取动态ID参数错误',sep='\n')
			
			sys.exit()
			
		pass
		
	def run(self):
		'''
			解析相应的JSON并下载图片。
			
			如果动态中不含图片则自动跳过该条动态。
			目前不考虑转发的动态中是否包含图片，直接跳过。
		'''
	
		card = self.get_json()
		
		for item in card:
			try:
				urls = json.loads(item['card'])['item']['pictures']
				for url in urls:
					'''
						coding here
					'''
					print(url['img_src'])
			except:
				print('本条动态不含图片，已跳过')
		#循环的最后一个对象保存的即为要拉取的下轮动态的ID
		else:
			self.offset = item['desc']['dynamic_id_str']
	
	def get_user_info(self):
		#若未请求过json，则先请求一遍
		if not self.is_get_profile:
			self.get_json()
		
		profile = self.profile
		info = profile['info']
		vip = profile['vip']
		
		print('UID:{}\n用户名:{}'.format(info['uid'],info['uname']))
		print('当前等级: {} 级'.format(profile['level_info']['current_level']))
		
		#判断当前用户是否为VIP
		if vip['vipStatus']:
			#Python中格式化时间戳的长度必须小于等于11位
			due_data = int(vip['vipDueDate'])//1000
			print('会员到期时间:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(due_data))))
		else:
			print('该用户不是(大/小)会员')
	
	#内部迭代抓取图片
	def get_img(self,limit=1,offset=0):
		'''
			下载图片。
			
			参数：
				[limit]:
					拉取limit轮动态，其中每轮有20条动态。
				
				[offset]:
					指定从ID为offset的动态开始拉取[limit]轮动态；
					该动态必须为初始化时指定的UID用户发送。
		'''
		
		self.limit = limit
		self.offset = offset
		for i in range(0,self.limit):
			self.run()
			print('*'*20)
			


if __name__ == '__main__':
	Downloader(9).get_user_info()
		
