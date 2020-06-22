import json
import asyncio

import wx
from wxasync import WxAsyncApp, AsyncBind


from client_config import get_config, save_config, ClientConfig

class SettingFrame(wx.Frame):
    def __init__(self, parent=None):
        super(SettingFrame, self).__init__(parent, style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
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

        wrapper.Add(grid_sizer, 1, wx.ALL|wx.CENTER, 30)
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
        super(MainFrame, self).__init__(parent, size=(600, 300), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)

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

        self.tag_ctrl = wx.TextCtrl(panel, value='TAG HERE', size=(300, -1))
        self.begin = wx.TextCtrl(panel, value='起始页', size=(50, -1))
        self.end = wx.TextCtrl(panel, value='结束页', size=(50, -1))

        self.dwbtn = wx.Button(panel, label='下载', size=(-1, 27))
        grid_sizer.AddMany([(self.tag_ctrl, 1, wx.EXPAND),
        (self.begin), (self.end),(self.dwbtn)])

        AsyncBind(wx.EVT_BUTTON, self.download, self.dwbtn)

        box_sizer.Add(grid_sizer, 1, wx.ALL|wx.CENTER, 20)

        self.img_list = wx.ListCtrl(panel, -1, style=wx.LC_REPORT)
        self.img_list.InsertColumn(0, '图片名')

        box_sizer.Add(self.img_list, 1, wx.EXPAND|wx.ALL^wx.TOP, 20)

        panel.SetSizer(box_sizer)

        self.Centre()

    async def download(self, evt):
        pass


if __name__ == '__main__':
    app = WxAsyncApp()
    frame = MainFrame()
    app.SetTopWindow(frame)
    frame.Show()

    evt = asyncio.get_event_loop()
    evt.run_until_complete(app.MainLoop())
