'''

	#获取用户信息，仅获取一次
	if not self.is_get_profile:
		self.profile = data['cards'][0]['desc']['user_profile']
		self.is_get_profile = True
'''

import requests
import json
import sys
import time

class Helper:
	host = 'https://api.vc.bilibili.com/'
	
	def __init__(self,offset):
		self.offset = offset
		
	
	def topic_img(self,topic_name):
		base_url = Helper.host+'topic_svr/v1/topic_svr/topic_history'
		dict = {'topic_name':topic_name,
				'offset_dynamic_id':self.offset
		}
				
		return requests.get(base_url,params=dict)

	def dynamic_img(self,uid):
		base_url = Helper.host+'dynamic_svr/v1/dynamic_svr/space_history'
		dict = {'host_uid':self.uid,
				'offset_dynamic_id':self.offset
		}
		
		return requests.get(base_url,params=dict)
		
		
class Downloader:
	
	def __init__(self,r):
		self.url = list(r.url)
		self.res = r
	
	def prase_json(self):
		'''
			获取请求的json。
		'''
		
		try:
			r = requests.get(self.url)
			json = r.json()
			data = json['data'] 
			
			print(r.url)
			
			#若本轮动态不存在，退出程序
			if int(data['has_more']) != 1:
				raise Exception()
				
			return data['cards']
		except:
			print('无法解析该条Json。')
			
			sys.exit()
			
		pass
		
	

Downloader(Helper(0).topic_img('123')).get_json()
	