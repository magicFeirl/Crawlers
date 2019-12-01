from bs4 import BeautifulSoup
import requests
import time

#host https://wallhaven.cc/

#base_url
base_url = 'https://wallhaven.cc/search'

#src_url
src_url = 'https://w.wallhaven.cc/full/{}/wallhaven-{}'

#ua
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/76.0.3809.132 Safari/537.36'}

#下载NSFW图片必须cookie参数 remember_web ...
#sample:"remember_web123214":"fafwerewrewrEE"

cookies = {"":""}
		
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

	def __init__(self,target):
		'''
			target：要下载的图片目标TAG
		'''
		self.target = target

	#部分class=lazyload元素中的图片的后缀可能和原图不同，会出现404的状况
	def format_url(self,obj):
		'''
			格式化从class=lazyload的元素中提取的URL，转为相应的原图URL。
			
		'''
		#获取class=lazyload的元素的预览URL
		#sample: https://th.wallhaven.cc/small/2k/2kv1y9.jpg
		data = obj.get('data-src')
		index = data.rfind('/')+1
		#切片出文件名用于格式化
		#sample:2kv1y9.jpg
		name = data[index:]
		#原文件URL格式化参数之二
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

		preview = bs.find_all('img',class_='lazyload')

		for i in preview:
			'''
				coding here
			'''
			src = self.format_url(i)
			print(src)
			pass
		pass


Downloader('Touhou').run(purity='001')
