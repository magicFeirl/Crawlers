import requests
import json
import os

##外层循环可添加

#接口地址
url = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid=7117493&offset_dynamic_id=0" 
#获取接口返回值
res_json = requests.get(url).json();
#获取要抓取的元素的值
cards = res_json['data']['cards']
#获取拉取下一轮动态的URL参数
offset_dynamic_id = cards[-1]['desc']['dynamic_id_str'] 

file_path = os.getcwd()+os.sep()+"imgs"


print(offset_dynamic_id)

#循环抓取本轮动态
for i in range(0,len(cards)):
	card_items = cards[i]['card']
	
	#指定键可能不存在
	try:
		img_card = json.loads(card_items)['item']['pictures']

		for j in range(0,len(img_card)):
			#文件地址
			img_src = img_card[j]['img_src']
			with open(
	except:
		pass
		
pass