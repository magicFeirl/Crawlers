'''wxPythonGUI Program
考虑复用性的话应该继承 MainFrame 并重写其 download 方法
然而编码时并没有考虑那么多，等有时间再写个好了。'''

import os
import json
import asyncio

import wx
from wxasync import WxAsyncApp, AsyncBind

from crawler_utils.client_config import get_config, save_config, ClientConfig
from sankaku_downloader import SankakuDownloader


class SettingFrame(wx.Frame):
    def __init__(self, parent=None):
        super(SettingFrame, self).__init__(parent,
        style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.InitUI()
        self.InitSetting()

    def InitUI(self):
        panel = wx.Panel(self)
        wrapper = wx.BoxSizer(wx.VERTICAL)
        labels = ['连接超时:', '并发下载数:', '并发连接数:', '本地代理端口（可选）:']
        grid_sizer = wx.FlexGridSizer(len(labels), 2, 5, 50)

        texts = [wx.StaticText(panel, label=label) for label in labels]
        self.ctrls = [wx.TextCtrl(panel) for i in range(len(labels))]

        li = []
        for item in zip(texts, self.ctrls):
            li.append((item[0],))
            li.append((item[1],))

        grid_sizer.AddMany(li)

        save_btn = wx.Button(panel, label='保存', size=(200, 30))
        save_btn.Bind(wx.EVT_BUTTON, self.OnBtnClick)

        wrapper.Add(grid_sizer, 1, wx.TOP|wx.CENTER, border=20)
        wrapper.Add(save_btn, flag=wx.CENTER|wx.BOTTOM, border=20)
        panel.SetSizer(wrapper)

        self.SetTitle('设置')

    def OnBtnClick(self, evt):
        ccf = ClientConfig(timeout=self.ctrls[0].GetValue(),
        max_download_num=int(self.ctrls[1].GetValue()),
        max_connect_num=int(self.ctrls[2].GetValue()),
        port=(self.ctrls[3].GetValue()))

        save_config(ccf)
        self.Close()

    def InitSetting(self):
        config = get_config()
        self.config = config
        self.ctrls[0].SetValue(str(config.timeout))
        self.ctrls[1].SetValue(str(config.max_download_num))
        self.ctrls[2].SetValue(str(config.max_connect_num))
        self.ctrls[3].SetValue(str(config.port))


class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent, size=(600, 400),
        style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

        self.time_counter = 0
        self.is_running = False
        self.InitUI()

    def setting(self, evt):
        s = SettingFrame(self)
        s.Show()

    def InitMenu(self):
        # panel = wx.Panel(self)
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(-1, '&设置')
        menu.Bind(wx.EVT_MENU, self.setting)

        menubar.Append(menu, '&选项')
        self.SetMenuBar(menubar)

    def InitUI(self):
        self.InitMenu()
        panel = wx.Panel(self)
        # labels = ['标签名']

        box_sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(1, 4, 10, 20)
        self.path_ctrl = wx.TextCtrl(panel, value=os.getcwd()+'\\')

        box_sizer.Add(self.path_ctrl, 1, wx.ALL|wx.EXPAND, 20)

        self.tag_ctrl = wx.TextCtrl(panel, value='TAG HERE', size=(300, -1))
        self.begin = wx.TextCtrl(panel, value='1', size=(50, -1))
        self.end = wx.TextCtrl(panel, value='1', size=(50, -1))

        self.dwbtn = wx.Button(panel, label='下载', size=(-1, 27))
        grid_sizer.AddMany([(self.tag_ctrl, 1, wx.EXPAND),
        (self.begin), (self.end),(self.dwbtn)])

        AsyncBind(wx.EVT_BUTTON, self.download, self.dwbtn)

        self.dwbtn.SetDefault()

        box_sizer.Add(grid_sizer, 1, wx.LEFT|wx.RIGHT|wx.CENTER, 20)

        self.img_list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
        self.img_list.InsertColumn(0, '任务列表', width=400)
        self.img_list.InsertColumn(1, '状态', width=130)
        box_sizer.Add(self.img_list, 1, wx.EXPAND|wx.ALL^wx.TOP, 20)
        panel.SetSizer(box_sizer)
        self.tag_ctrl.SetFocus()
        # 当焦点为自身时会失效
        self.path_ctrl.SetInsertionPoint(0)

        self.sb = self.CreateStatusBar()
        self.sb.SetFieldsCount(3)
        self.sb.SetStatusWidths([-1, -2, -1])

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)

        self.sb.SetStatusText('等待下载', 0)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetTitle('SankakuComplexDownloader')
        self.Centre()

    def OnClose(self, evt):
        if self.is_running:
            dial = wx.MessageDialog(None, '有任务正在进行，确定退出？', '提示',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

            ret = dial.ShowModal()

            if ret == wx.ID_YES:
                self.Destroy()
            else:
                evt.Veto()
        else:
            evt.Skip()

    def OnTimer(self, evt):
        self.sb.SetStatusText(f'耗时: {self.time_counter} s', 2)
        self.time_counter += 1

    async def download(self, evt):
        self.is_running = True
        await self.start()
        self.clear()
        self.is_running = False

    async def start(self):
        self.dwbtn.Disable()
        tag = self.tag_ctrl.GetValue()
        dest = self.path_ctrl.GetValue()

        if dest == os.getcwd() + '\\':
            dest += tag

        begin = int(self.begin.GetValue())
        end = int(self.end.GetValue())

        ccf = get_config()

        self.timer.Start(1000)
        downloader = SankakuDownloader(tag, self, dest=dest,
        begin=begin, end=end, ccf=ccf)

        await downloader.start()

    def clear(self):
        self.dwbtn.Enable()
        self.img_list.DeleteAllItems()
        self.timer.Stop()
        # self.sb.SetStatusText('', 3)
        self.sb.SetStatusText('下载完成', 1)
        self.sb.SetStatusText('', 0)
        self.time_counter = 0


def about():
    print('该窗口用来输出异常信息，关闭会导致程序终止。')


if __name__ == '__main__':
    app = WxAsyncApp()
    frame = MainFrame()
    app.SetTopWindow(frame)
    frame.Show()

    about()

    evt = asyncio.get_event_loop()
    evt.run_until_complete(app.MainLoop())
    input('输入回车键退出。')
