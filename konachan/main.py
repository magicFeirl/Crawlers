'''
	日期：2019年12月2日
	编码时间：18:49
	结束时间：19:05
	
	host=http://konachan.net/post
	
	Editor：Notepad++
'''

import requests
from bs4 import BeautifulSoup


base_url = 'http://konachan.net/post'

headers = {
	'User-Agent':'"Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
	'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"'
}


class Downloader:
	
	#请求参数设置
	def __init__(self,**params):
		self.p = params
		pass
		
	#内部迭代下载URL
	def run(self,start=1,end=1):
		self.p['page'] = start
		for i in range(start,end+1):
			r = requests.get(base_url,self.p,headers=headers)
			r.encoding  = 'utf-8'
			self.text = r.text
			
			print('Downloading->'+r.url)
			
			#下载图片
			self.write_file()
			pass
			
	#解析出含目标URL的DOM
	def get_imgurl(self,text):
		bs = BeautifulSoup(text,'html.parser')
		content_list = bs.find(id='post-list-posts')
		result = []
		
		for i in content_list.find_all('a',attrs={'class':'largeimg'}):
			result.append(i.get('href'))
			
		return result
		
	#将URL写入文件
	def write_file(self):
		result = self.get_imgurl(self.text)
		for i in result:
			print(i)
			

Downloader(tags='touhou').run()