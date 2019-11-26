import requests
import json
import time

class Crawler:
	#基本URL
	base_url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history'

	def __init__(self,host_uid,offset_dynamic_id=0):
		self.host_uid = host_uid
		self.offset_dynamic_id = offset_dynamic_id
		self.get_josn()

	#获取服务器返回的json
	def get_josn(self):
		'''
			返回一个json对象
			
			host_uid:要爬取的用户的UID
			offset_dynamic_id:要拉取下一轮动态的ID，默认为0
		'''

		params = {'host_uid':self.host_uid,
				'offset_dynamic_id':self.offset_dynamic_id
		}
		
		json = requests.get(Crawler.base_url,params=params).json()
		
		
		self.hasmore = int(json['data']['has_more'])
		
		self.cards = json['data']['cards']
		self.offset_dynamic_id = self.next_did = self.cards[-1]['desc']['dynamic_id_str']
		self.json = json

		pass
		
	def get_imgurl(self):
		for i in self.cards:
			items = i['card']
			try:
				img_card = json.loads(items)['item']['pictures']
				for url in img_card:
					print(url['img_src'])
			except:
				pass
				
		print('\n')
		self.get_josn()
		
	def has_more(self):
		return self.hasmore;
	
	
	def get_vipDueData(self):
		pass


i = 0
c = Crawler(33)
while c.has_more() and i<2:
	i+=1
	c.get_imgurl()
	time.sleep(1)
	
	pass