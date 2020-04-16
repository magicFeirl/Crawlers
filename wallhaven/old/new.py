from bs4 import BeautifulSoup
import requests
import time
import sys

def parser():
	r = requests.get('https://wallhaven.cc/search?q=touhou')
	r.encoding = 'utf-8'
	bs = BeautifulSoup(r.text)
	
	div_list = bs.find_all('div',attrs={'class':'thumb-info'})
	
	for i in div_list:
		png = i.find('span',attrs={'class':'png'})
		print(png)


parser()