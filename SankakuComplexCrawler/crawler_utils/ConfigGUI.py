import json
import asyncio

import wx
from wxasync import WxAsyncApp, AsyncBind


class MainFrame(wx.Frame):
    def __init__(self, parent=None):
        super(MainFrame, self).__init__(parent)

        self.InitUI()


    def InitUI(self):
        panel = wx.Panel(self)

        #bs = wx.BoxSizer()
        sb = wx.StaticBox(panel, label='Config', pos=(10, 10), size=(300, 300))
        wx.StaticText(panel, label='123', pos=(50, 70))
        wx.CheckBox(panel, label='Male', pos=(15, 30))
        wx.CheckBox(panel, label='Married', pos=(15, 55))
        wx.StaticText(panel, label='Age', pos=(15, 95))
        wx.SpinCtrl(panel, value='1', pos=(55, 90), size=(60, -1), min=1, max=120)

        #bs.Add(sb, 1, flag=wx.EXPAND|wx.ALL, border=5)
        #panel.SetSizer(bs)



if __name__ == '__main__':
    app = WxAsyncApp()
    frame = MainFrame()
    app.SetTopWindow(frame)
    frame.Show()

    evt = asyncio.get_event_loop()
    evt.run_until_complete(app.MainLoop())
