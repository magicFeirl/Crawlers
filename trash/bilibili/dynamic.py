import requests
import json
import sys
import time

base_url = 'https://api.vc.bilibili.com/topic_svr/v1/topic_svr/topic_history'

class Test:
	
	def __init__(self,tag,offset=0):
		self.tag = tag
		self.offset = offset

	def get_json(self):
			'''
				获取请求的json。
			'''
			
			#构造请求参数
			params = {'topic_name':self.tag,
					'offset_dynamic_id':self.offset
			}
			
			try:
				r = requests.get(base_url,params=params)
				print(r.url)
				json = r.json()
				data = json['data']
				
				print(data)
				
				#若本轮动态不存在，退出程序
				if int(data['has_more']) != 1:
					raise Exception()
				
				return data['cards']
			except:
				print('无法解析该条Json。',
				'tag:'+str(self.tag),
				'拉取动态ID:'+str(self.offset),
				'\n可能的原因：',
				'1.用户不存在',
				'2.该用户未发布任何动态',
				'3.输入的拉取动态ID参数错误',sep='\n')
				
				sys.exit()
				
			pass
			
	def run(self):

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


Test('东方美图',0).run()