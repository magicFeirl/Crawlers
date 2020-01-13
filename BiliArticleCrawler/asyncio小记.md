## 使用asyncio的方法

1. 将有io操作（比如网络连接，读写文件）的函数定义为协程函数，CPU操作部分（解析网页等不需要io的部分）则可直接使用普通函数
3. 直接调用协程函数不会执行函数代码，使用asyncio提供的接口才能执行函数

## 可等待对象

如果一个对象可以在 [`await`](https://docs.python.org/zh-cn/3/reference/expressions.html#await) 语句中使用，那么它就是 **可等待** 对象。许多 asyncio API 都被设计为接受可等待对象。

*可等待* 对象有三种主要类型: **协程**, **任务** 和 **Future**.

## 获取协程返回值

两种方法：

1. 使用asyncio.ensure_future(协程)
2. 使用loop.create_task(协程)

以上两种方法前者返回一个future对象，后者返回一个task对象，都可以使用result()方法获取返回结果

## 添加回调函数

```python
def callback(future): # 必须传入一个future对象
	print('All done!')
    
async def get_html(url):
    print('get url:',url)
    await asyncio.sleep(1)
    print('done')
    
loop = asyncio.get_event_loop() # 获取时间循环
task = loop.create_task(get_html('b')) # 创建一个task对象
task.add_done_callback(callback) # 添加回调函数
loop.run_until_complete(task) # 阻塞运行
print(task.result()) # 打印协程返回值
loop.close() # 关闭事件循环

```

