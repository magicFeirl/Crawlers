## SankakuComplex图片下载器

* 输入tag即可下载图片
* 使用aio，可自行设置并发量
* ~~然而在不科学上网的情况下还是很慢~~

#### 使用方法

1. 请确保代码文件`main.py`和`downloader.py`在同一目录下，且该目录可供读写。
2. 打开`main.py`设置下载参数，启动程序即可。关于下载参数`downloader.py`中有详细的介绍，一般来说只需要关心前四个参数，它们分别是:
   1. 要下载的图片的tag名
   2. 保存图片文件夹的名字
   3. 起始下载页
   4. 结束下载页
3. 需要Python3.7+版本及`aiohttp`和`aiofiles`包，如果你之前没有安装过的话，请使用使用`pip install `安装包。
4. 程序启动后会显示下载提示信息，在确认后才会进行下载操作。

![示例](example.jpg)

### 2020年1月20日更新

1. 修复队列可能阻塞的bug；当抛出异常时无法完成相应的`task_done`操作，因此会导致阻塞。
2. 将默认超时时间调整为45s，如果超时则停止下载。

关于超时，aiohttp官方文档的描述：

> By default *aiohttp* uses a *total* 5min timeout, **it means that the whole operation should finish in 5 minutes.**

也就是说，如果发生超时可能会导致图片没有完全下载的情况，然而考虑到大部分图片都能在45s内下载完毕，所以还是将超时设为45s了。

#### 补充更新

当获取到空数据列表时，应该取出队列中所有剩余数据以清空生产者队列，同时要捕获可能发生的异常。当队列取消堵塞后调用`task.cancel()`协程会抛出一个`asyncio.CancelledError`以取消协程，在`finally`代码块中不应该直接使用`queue.task_done()`，而是要判断数据列表是否为空，若不为空则调用`task_done()`方法，否则会抛出调用`task_done()`次数过多的异常，具体原因应该是当数据列表为空时会进入while循环首先调用一遍`task_done()`，而最后取消阻塞则会引发异常，此时已经调用了`task_done()`，无需重复调用。

### 2020年1月22日更新

将实现封装为类，其中关键代码可以复用，准备添加回调。

### 2020年1月25日更新

优化了代码格式，同时去除了部分错误代码。

关于`Task`对象的`cancel()`方法，在调用后还要执行await 语句以等待协程取消完毕。可以在协程内捕获`asyncio.CancelledError`异常并将其raise下去，不推荐直接抑制异常。在执行`await task.cancel()`后异常会被传递到当前代码块，要使用try...except asyncio.CancelledError捕获异常，或者直接使用`asyncio.gather(task, return_exceptions=True)`等待协程取消完毕，示例代码:

```python
'''取消协程运行的几种方法'''

import asyncio

async def run():
    
    try:
    	print('Running')
    	await asyncio.sleep(10)
    except asyncio.CancelledError:
        print('Cancelled')
        raise # 将异常传递下去 
    print('Done')
    
async def main():
    
    task = asyncio.create_task(run())
    
    await asyncio.sleep(0) # 等待协程运行
    
    task.cancel()
    
    # 第一种方法
    
    try:
        await task
    except asyncio.CancelledError:
        pass
    
    # 第二种方法
    asyncio.gather(task, return_exceptions=True)
    
    
```

#### 补充更新

当请求超时会导致队列阻塞，需要捕获`asyncio.TimeoutError`以告知队列任务结束。

### 2020年2月1日更新

加了回调类，不过仍然鸡肋。

### 2020年4月17日更新

> 有些小更新之前没有记录到 README 中，所以此处更新是从2月1日截至到目前的所有更新内容。

* 增加代理支持
* 加入进度条

### 2020年5月8日更新

实现了万众瞩目的GUI。

代码量很少，但是写起来很累。

关于 wxPython 中协程和多进程的使用还不熟练，多进程传 wx.App 的子类会报 can't pickle Frame object，目测是因为传入的对象不是 Python 的标准对象导致 Pickle 出错。

### 心得

aio算是新技术，虽然也出来很久了，但是目前看到的电子书上都没有相关的介绍，官方文档如果能耐得下心去看的话其实还是有很大帮助的，不要以为浮躁而错失了一项新技术。性能上aio比多线程要好，用法上个人感觉也比多线程容易，不过想要发挥aio的全部威力还是得借助`asyncio.Queue()`的生产者消费者模型。此外分析页面也是爬虫必不可少的一步，解析静态网页很容易，如果是动态加载的页面就可能会涉及到ajax、js等技术，还是得活到老学到老。