# 关于多生产者消费者模型回调的一点思路

使用多生产者消费者模型时其实大部分功能都是一样的，比如创建生产者队列、阻塞队列等待程序运行结束、任务结束后取消协程的运行等。代码的区别主要在于处理不同的需求，有的是要处理`JSON`数据，有的是解析`HTML`，还有的是将内容写入本地，这些代码我们可以考虑使用回调函数实现。

## 生产者 & 消费者

我们可以定义两个类`Producer`和`Consumer`，分别对应生产者和消费者。其中`Producer`类负责接收初始数据（如URL）然后返回处理结果，而`Consumer`则根据`Producer`返回的结果进行其他操作（比如写入本地，入库等）。关于Python中的队列处理事实上`Producer`和`Consumer`的代码都是差不多的，需要注意的是要捕获可能的异常以避免队列阻塞。

## Task 对象

一个与 [`Future 类似`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.Future) 的对象，可运行 Python [协程](https://docs.python.org/zh-cn/3/library/asyncio-task.html#coroutine)。非线程安全。

使用高层级的 [`asyncio.create_task()`](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.create_task) 函数来创建 Task 对象，也可用低层级的 [`loop.create_task()`](https://docs.python.org/zh-cn/3/library/asyncio-eventloop.html#asyncio.loop.create_task) 或 [`ensure_future()`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.ensure_future) 函数。

[`asyncio.Task`](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio.Task) 从 [`Future`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.Future) 继承了其除 [`Future.set_result()`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.Future.set_result) 和 [`Future.set_exception()`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.Future.set_exception) 以外的所有 API。

### 取消Task

```python
async def work():
    while True:
        await asyncio.sleep(1)
        
async def main():
    task = asycio.create_task(work())
    await asyncio.sleep(1) # 等待协程启动
    task.cancel() # 取消协程
    await asyncio.gather(task, return_exceptions=True) # 等待协程取消
    
if __name__ == '__main__':
    asyncio.run(main())
```

### 迭代协程返回结果

`asyncio.as_completed(aws, *, loop=None, timeout=None)`

 并发地运行 *aws* 集合中的 [可等待对象](https://docs.python.org/zh-cn/3/library/asyncio-task.html#asyncio-awaitables)。返回一个 [`Future`](https://docs.python.org/zh-cn/3/library/asyncio-future.html#asyncio.Future) 对象的迭代器。返回的每个 Future 对象代表来自剩余可等待对象集合的最早结果。

```python
for f in as_completed(aws):
    earliest_result = await f
```

# 其他笔记

## 使用asyncio的方法

1. 将有io操作（比如网络连接，读写文件）的函数定义为协程函数，CPU操作部分（解析网页等不需要io的部分）则可直接使用普通函数
2. 直接调用协程函数不会执行函数代码，使用asyncio提供的接口才能执行函数

## 可等待对象

如果一个对象可以在 [`await`](https://docs.python.org/zh-cn/3/reference/expressions.html#await) 语句中使用，那么它就是 **可等待** 对象。许多 asyncio API 都被设计为接受可等待对象。

*可等待* 对象有三种主要类型: **协程**, **任务** 和 **Future**.

## 获取协程返回值

两种方法：

1. 使用asyncio.ensure_future(协程)
2. 使用loop.create_task(协程)

以上两种方法前者返回一个future对象，后者返回一个task对象，都可以使用result()方法获取返回结果

*两种方法都是非阻塞式

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