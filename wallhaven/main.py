from bs4 import BeautifulSoup
import requests
import time
import sys

#host https://wallhaven.cc/

#base_url
base_url = 'https://wallhaven.cc/search'

#src_url
src_url = 'https://w.wallhaven.cc/full/{}/wallhaven-{}'

#ua
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/76.0.3809.132 Safari/537.36'}

#下载NSFW图片必须设置cookie参数 remember_web ...
#sample:"remember_web123214":"fafwerewrewrEE"

cookies = {'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d':'eyJpdiI6IjBPcW1qUnhPczJrUjA4bWhZdFlWT2c9PSIsInZhbHVlIjoibXZsN2NldHJMYjlqTnZqN3FUVTV4am9yQUgrbGNnXC9mSUNEVGRCXC9mTWl6cmE3SkRDNmR5bFRMclp0OVNZV2tCRUxsbFVjNGhEMkpsUVh6NkRlY0p5NVArT2RCdDFpalB4c1JpR0tpSGpicjNRVU1Ea0RBZzJqQzczR3VQR2hva3JyQ3g3cHpZYU5qTEJYSGVOVm40S1AwdFBaZ3F0bDhXa1laUldpZWdcL3ZjNzZyVTNkY0ozSThcLzA1aTY5QWVNayIsIm1hYyI6IjQxMWZiNGNjOWQ3NzIyYWZhNTJlMjk5YmEyZTJkZWNlOWEwZDk3OTM1ZTVhMTA4ZGI2NDAzMDc5ZDY3MzllMmUifQ%3D%3D'}
		
'''
	sample url:
	
	https://wallhaven.cc/search?q=Touhou
	https://wallhaven.cc/search?q=Touhou&purity=001&page=1
	
	query params:
		q：
			要搜索的图片所属类别，理解为tag
			
		purity：
			筛选图片类型。
			目测是二进制数，可选值有 SFW Skechy NSFW 共8种组合方式。
			选择的参数相应二进制位变为1
			示例：001 SFW Skechy *NSFW
				  101 *SFW Skechy *NSFW
				  
				  *表示被选择的参数
'''


class Downloader:

	def __init__(self,target,path):
		'''
			target：要下载的图片目标TAG
			path：图片URL保存路径
		'''
		self.target = target
		self.path = path

	#部分class=lazyload元素中的图片的后缀可能和原图不同，会出现404的状况
	def format_url(self,obj):
		'''
			格式化从class=thumb-info的元素中提取的URL，转为相应的原图URL。
			
		'''
		data = obj.find('a').get('data-href')
		
		index = data.rfind('/')+1
		name = data[index:]
		if obj.find('span',attrs={'class':'png'}) != None:
			name = name+'.png'
		else:
			name = name+'.jpg'
		src = name[0:2]
		
		#返回原图URL（被格式化的URL）
		#sample:https://w.wallhaven.cc/full/2k/wallhaven-2kv1y9.jpg
		return src_url.format(src,name)

	
	def run(self,start=1,end=1,delay=1,**dict):
		'''
			内部迭代下载图片
			
			可选参数：
				start=1 下载开始页
				end=1   下载结束页
				
				delay=1 请求延时
				
				**dict 筛选参数
		'''
		dict['q'] = self.target
		for i in range(start,end+1):
			dict['page'] = i
			self.parser(dict)
			time.sleep(delay)

	
	def parser(self,params):
		'''
			解析原图URL并下载
		'''
		res = requests.get(base_url,headers=header,params=params,cookies=cookies)
		res.encoding = 'utf-8'
		print('Downloading>',res.url)

		bs = BeautifulSoup(res.text,'html.parser')

		#preview = bs.find_all('img',class_='lazyload')
		#修改获取URL方式，原方式无法判别文件名会导致404
		div_list = bs.find_all('div',attrs={'class':'thumb-info'})
		if not len(div_list):
			print('Cookie 已失效')
			sys.exit()
			
		try:
			file = open(self.path,'a')
			for i in div_list:
				'''
					coding here
				'''
				src = self.format_url(i)
				file.write(src+'\n')
				pass
		except:
			print('异常')
		pass


Downloader('Touhou','th_nsfw.txt').run(end=10,purity='001')
