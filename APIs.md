# 写爬虫至今收集的接口

> 2020年6月20日 可用

## 404 漫画

https://www.bilibili.com/activity/web/view/data/31

## 下方推荐
https://api.bilibili.com/x/web-interface/archive/related?aid={aid}

## 视频播放量回复等信息
可av bv互转（返回所需流量小于view接口）。

如果稿件被删除，则无法获得结果， 貌似现在的BV表示就有这一限制。
https://api.bilibili.com/x/web-interface/archive/stat?bvid={bv}

## 发送弹幕接口
https://api.bilibili.com/x/v2/dm/post

## 弹幕接口

https://api.bilibili.com/x/v2/dm/history?oid={oid}&date=2019-12-20&type=1

## 收藏夹
https://api.bilibili.com/medialist/gateway/base/spaceDetail?media_id={id}&pn=4&ps=20&keyword=&order=mtime&type=0&tid=0&jsonp=jsonp

## 掉了参数暂且蒙古
https://api.bilibili.com/medialist/gateway/coll/resource/deal
https://api.bilibili.com/x/web-interface/broadcast/servers?platform=web

## 用户相册接口
https://api.vc.bilibili.com/link_draw/v1/doc/doc_list?uid=2&page_num=1&page_size=20

## 失效视频信息
https://api.bilibili.com/medialist/gateway/base/resource/info?rid={av}&type=2

## 多失效视频信息
https://api.bilibili.com/medialist/gateway/base/resource/infos?resources=81731732%3A2

https://api.bilibili.com/medialist/gateway/base/resource/infos?resources=54606985%3A2%2C55238206%3A2%2C53214459%3A2%2C53032205%3A2%2C62681809%3A2%2C63175571%3A2%2C63355662%3A2%2C61310704%3A2%2C66373145%3A2%2C59607723%3A2%2C66674741%3A2%2C65487232%3A2%2C49067092%3A2%2C54387281%3A2%2C60184448%3A2%2C54440421%3A2
以%3A2%2C结尾
解码后：
https://api.bilibili.com/medialist/gateway/base/resource/infos?resources=54606985:2,55238206:2,53214459:2,53032205:2,62681809:2,63175571:2,63355662:2,61310704:2,66373145:2,59607723:2,66674741:2,65487232:2,49067092:2,54387281:2,60184448:2,54440421:2

## 用户动态列表 （参数offset的值是动态id，这个可以从json中获取）
https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/w_dyn_personal?host_uid=2&offset=374060152195131353

## 视频简介
https://api.bilibili.com/x/web-interface/archive/desc?aid={aid}

## 视频信息（简介、tag等）（仅未被消除稿件）
https://api.bilibili.com/x/web-interface/view?aid={aid}

## 视频信息（简介、tag等）（仅未被消除稿件）(BVID版）
https://api.bilibili.com/x/web-interface/view?bvid={bvid}

## 搜索接口（被屏蔽稿件无法获得结果）
https://api.bilibili.com/x/web-interface/search/all/v2?keyword={keyword}

## 根据search_type精确检索稿件
https://api.bilibili.com/x/web-interface/search/type?context=&keyword={kw}&page=1&search_type=video

## 关注接口
https://api.bilibili.com/x/relation/followings?vmid={vmid}&pn=2&ps=50&order=desc
```
获取自己的关注列表，最多40页，最多2000条
获取用户的关注列表，系统限制访问前5页，分页最大为50，倒序正序各获取250条记录，共500条
vmid: 用户id
pn: 页数 
ps: 每显示条数大小
order: desc or asc
```

## 用户信息 

来源https://github.com/uupers/BiliSpider/wiki/Bilibili-API-%E7%94%A8%E6%88%B7%E4%BF%A1%E6%81%AF

https://api.bilibili.com/x/web-interface/card?mid={mid}

## 专栏信息接口
专栏图片什么的还是需要请求网页 
https://api.bilibili.com/x/article/viewinfo?id={id}

## 网易云音乐接口
http://music.163.com/song/media/outer/url?id={id}.mp3
