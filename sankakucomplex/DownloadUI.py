'''UI_SankakuDownloader'''

import asyncio
import multiprocessing

import wx

from downloader import Downloader


async def download_img(tag, dir_name, proxy, begin, end, conn, dw):
    downloader = Downloader(tag, dir_name, begin, end,
            timeout=5*60, max_conn_num=conn, max_download_num=dw)

    await downloader.start()

def go(tag, dir_name, proxy, begin, end, conn, dw):
    asyncio.run(download_img(tag, dir_name, proxy, begin, end, conn, dw))

class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None, title='SankakuDownloader',
        size=(330, 500), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.InitUI()

    def run(self, event):
        tag = self.tag_name.GetValue()
        dir_name = self.dir_name.GetValue()
        proxy = self.proxy.GetValue()
        begin = int(self.begin.GetValue())
        end = int(self.end.GetValue())
        conn = int(self.conn.GetValue())
        dw = int(self.download.GetValue())

        if not all([tag, dir_name, begin, end, conn, dw]):
            print('参数有误或未填写完整')
        else:
            proc = multiprocessing.Process(target=go,
            args=(tag, dir_name, proxy, begin, end, conn, dw, ))

            proc.daemon = True
            proc.start()

            '''
            # downloader.start()
            print('in')
            await asyncio.sleep(3)
            print('out')

            task = asyncio.create_task(asyncio.sleep(3))
            task.add_done_callback(functools.partial(self.callback, self))
            self.download_button.Disable()
            await task
            '''

    def InitUI(self):
        panel = wx.Panel(self)

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

        self.download_button.Bind(wx.EVT_BUTTON, self.run)

        wrapper.Add(self.download_button, flag=wx.EXPAND|wx.ALL^wx.BOTTOM, border=30)
        panel.SetSizer(wrapper)


if __name__ == '__main__':
    app = wx.App()
    f = Frame()
    f.Show()
    app.MainLoop()





