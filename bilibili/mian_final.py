import requests
import json
import os

class Downloader:
	#话题及动态基URL
	base_urls = ('https://api.vc.bilibili.com/',
					#话题
					'topic_svr/v1/topic_svr/topic_history?topic_name={}&offset_dynamic_id={}',
					#动态
					'dynamic_svr/v1/dynamic_svr/space_history?host_uid={}&offset_dynamic_id={}'
				)

	
	def __doc__(self):
		print('''
				下载Bilibili网的动态或话题图片	
				
				参数：
					target:
						要下载的动态UP UID 或 话题名
					save_path:
						文件保存路径
					[next_id]:
						从指定ID的动态开始下载图片；
						若要下载用户发送的动态，则指定的ID必须为用户发送的动态的ID
			''')
	
	def __init__(self,target,save_path,next_id=0):
		
		urls = Downloader.base_urls

		#通过判断函数参数是否为整数区分话题或动态的基URL
		if isinstance(target,int):
			self.base_url = urls[0] + urls[2]
		else:
			self.base_url = urls[0] + urls[1]

		self.next_id = next_id
		self.target = target
		self.save_path = save_path
		
		pass

	def format(self):
		return self.base_url.format(self.target,self.next_id)

	def get_json(self):
		try:
			r = requests.get(self.format())
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
		
	def run(self,limit=1):
		'''
			解析相应的JSON并下载图片。
			
			如果动态中不含图片则自动跳过该条动态。
			目前不考虑转发的动态中是否包含图片，直接跳过。
		'''
	
		for i in range(0,limit):
			card = self.get_json()
			for item in card:
				try:
					urls = json.loads(item['card'])['item']['pictures']
					try:
						with open(self.save_path,'a',encoding='utf-8') as file:
							for url in urls:
								'''
									coding here
								'''
								#解析出图片URL url['img_src']
								print(url['img_src'])
								file.writelines(url['img_src']+'\n')
					except:
						print('写入图片失败')
					finally:
						if file:
							file.flush()
							file.close()
				except:
					print('本条动态不含图片，已跳过')
				finally:
					pass
			#循环的最后一个对象保存的即为要拉取的下轮动态的ID
			else:
				self.next_id = item['desc']['dynamic_id_str']


if __name__ == '__main__':
	Downloader('魔法少女小圆','pmmm.txt').run(5)



