'''GUI SankakuDownloader'''

import asyncio

import wx
import wxasync
import aiohttp

from downloader import Downloader

'''
异步 http 请求测试
async def req_test(event):
    async with aiohttp.ClientSession() as session:
        proxy = 'http://127.0.0.1:1081'
        async with session.get('https://www.google.com', proxy=proxy) as resp:
            print(await resp.text())
'''


class Frame(wx.Frame):
    def __init__(self):

        super(Frame, self).__init__(None, title='SankakuDownloader',
        size=(330, 500),
        style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)

        menubar = wx.MenuBar() # 新建一个Menubar对象
        about = wx.Menu() # 新建一个menu选项卡

        about.Append(-1, '&关于') # 添加子选项
        self.SetBackgroundColour('white')
        menubar.Append(about, '&选项') # 将选项卡添加至menubar


        tag_name_lable = wx.StaticText(panel, label='标签名: ')
        dir_name_lable = wx.StaticText(panel, label='保存文件夹名: ')
        proxy_lable = wx.StaticText(panel, label='本地代理端口（可选): ')

        begin_lable = wx.StaticText(panel, label='起始页: ')
        end_lable = wx.StaticText(panel, label='结束页: ')
        conn_lable = wx.StaticText(panel, label='并发连接数: ')
        download_lable = wx.StaticText(panel, label='并发下载数: ')

        self.tag_name = wx.TextCtrl(panel)
        self.dir_name = wx.TextCtrl(panel)
        self.proxy = wx.TextCtrl(panel)

        self.begin = wx.TextCtrl(panel, value='1')
        self.end = wx.TextCtrl(panel, value='1')
        self.conn = wx.TextCtrl(panel, value='5')
        self.download = wx.TextCtrl(panel, value='20')

        wrapper = wx.BoxSizer(wx.VERTICAL)
        fgs = wx.FlexGridSizer(7, 2, 10, 20)

        fgs.AddMany([
            tag_name_lable, self.tag_name,
            dir_name_lable, self.dir_name,
            proxy_lable, self.proxy,
            begin_lable, self.begin,
            end_lable, self.end,
            conn_lable, self.conn,
            download_lable, self.download])

        title = wx.StaticText(panel, label='SankakuComplex 图片下载器 V1.0')
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)

        wrapper.Add(title, flag=wx.ALL, border=30)
        wrapper.Add(fgs, flag=wx.EXPAND|wx.ALL^wx.TOP, border=30)

        self.download_button = wx.Button(panel, label='下载')

        wxasync.AsyncBind(wx.EVT_BUTTON, self.async_run, self.download_button)

        wrapper.Add(self.download_button, flag=wx.EXPAND|wx.ALL^wx.BOTTOM, border=30)
        panel.SetSizer(wrapper)

        self.SetMenuBar(menubar)

    async def async_run(self, event):
        tag = self.tag_name.GetValue()
        dir_name = self.dir_name.GetValue()
        port = self.proxy.GetValue()
        begin = int(self.begin.GetValue())
        end = int(self.end.GetValue())
        conn = int(self.conn.GetValue())
        dw = int(self.download.GetValue())

        if not all([tag, dir_name, begin, end, conn, dw]):
            print('参数有误或未填写完整')
        else:
            self.download_button.Disable()
            proxy = None

            if port:
                proxy = f'http://127.0.0.1:{port}'

            downloader = Downloader(tag, dir_name, begin, end,
            proxy=proxy, max_conn_num=conn, max_download_num=dw)

            await downloader.start()

            self.download_button.Enable()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    app = wxasync.WxAsyncApp()
    frame_obj = Frame()
    frame_obj.Show()

    loop.run_until_complete(app.MainLoop())







