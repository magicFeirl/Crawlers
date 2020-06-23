'''
GelboourDownload GUI Program
2020年6月23日14:57:51

聊胜于无
'''
import time
import asyncio

import wx
import wxasync

from GelbooruDownloader import GelBooruDownloader


class MainFrame(wx.Frame):
    def __init__(self, parent=None, title='WX', size=(600, -1)):
        super(MainFrame, self).__init__(parent, title=title, size=size)
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)
        container = wx.BoxSizer(wx.VERTICAL)

        inner = wx.FlexGridSizer(1, 5, 10, 10)

        tag_ctrl = wx.TextCtrl(panel, value='Tag')
        begin_ctrl = wx.TextCtrl(panel, value='0')
        end_ctrl = wx.TextCtrl(panel, value='1')
        output_filename = wx.TextCtrl(panel)

        start_btn = wx.Button(panel, label='下载')

        wxasync.AsyncBind(wx.EVT_BUTTON, self.run, start_btn)

        self.ctrls = [tag_ctrl, begin_ctrl, end_ctrl, output_filename, start_btn]
        ctrl_font = wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL)

        for ctrl in self.ctrls:
            ctrl.SetFont(ctrl_font)

        inner.AddMany([(tag_ctrl, 1, wx.EXPAND),
        (begin_ctrl, 1, wx.EXPAND),
        (end_ctrl, 1, wx.EXPAND),
        (output_filename, 1, wx.EXPAND),
        (start_btn, 1, wx.EXPAND)])

        inner.AddGrowableCol(0, 1)

        container.Add(inner, 0, wx.EXPAND|wx.ALL, 10)

        text = '''欢迎使用GelbooruDownloader，这是一个简单的爬虫程序，用于爬取 Gelbooru 上的图片链接并保存至本地。你可以通过IDM等下载工具批量下载图片链接。

四个输入框分别对应：标签名、起始页、结束页、输出文件名，爬取的链接文件会以指定的输出文件名保存\n至当前目录，如果没有填写输出文件名则默认使用标签名作为输出文件名。
        '''

        tips = wx.StaticText(panel, label=text)
        container.Add(tips, 0, wx.LEFT|wx.RIGHT, 10)

        panel.SetSizer(container)

        self.Center()

    async def run(self, evt):
        tag_name = self.ctrls[0].GetValue()
        begin = int(self.ctrls[1].GetValue())
        end = int(self.ctrls[2].GetValue())
        output_filename = self.ctrls[3].GetValue()

        if not all([tag_name, str(begin), str(end)]):
            wx.MessageBox('标签名、起始页、结束页不能为空', '提示', wx.OK | wx.ICON_INFORMATION)
        else:
            st = time.time()

            # 限制最大并发数
            mcn = end - begin

            if mcn > 5:
                mcn = 5

            gbd = GelBooruDownloader(tag_name, begin=begin, end=end,
            destfile=output_filename,
            rating='a',
            max_connect_num=mcn)
            self.ctrls[4].Disable()
            await gbd.start()
            gbd.clear()
            self.ctrls[4].Enable()

            et = time.time()

            wx.MessageBox(f'下载完成！\n耗时: {round(et-st, 2)} s',
            '提示', wx.OK | wx.ICON_INFORMATION)


if __name__ == '__main__':
    app = wxasync.WxAsyncApp()
    frame = MainFrame(title='GelbooruDownloader')

    frame.Show()
    app.SetTopWindow(frame)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.MainLoop())
