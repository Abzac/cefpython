# Simple sample ilustrating the usage of CEFWindow class
# __author__ = "Greg Kacy <grkacy@gmail.com>"

import os
import wx

import cefpython1.wx.chromectrl as chrome

class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                          title='cefwx example1', size=(600,400))

        self.cefWindow = chrome.ChromeWindow(self,
                #url=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                # "../cefsimple.html"))
                url=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "../withpopup.html"))

        sizer = wx.BoxSizer()
        sizer.Add(self.cefWindow, 1, wx.EXPAND, 0)
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        self.Destroy()

if __name__ == '__main__':
    chrome.Initialize()
    print('wx.version=%s' % wx.version())
    app = wx.PySimpleApp()
    MainFrame().Show()
    app.MainLoop()
    del app # Let wx.App destructor do the cleanup before calling cefpython.Shutdown().
    chrome.Shutdown()


