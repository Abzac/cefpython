# An example of embedding CEF in wxPython application.

import platform
if platform.architecture()[0] != "32bit":
	raise Exception("Architecture not supported: %s" % platform.architecture()[0])

import sys
if sys.hexversion >= 0x02070000 and sys.hexversion < 0x03000000:
	import cefpython_py27 as cefpython
elif sys.hexversion >= 0x03000000 and sys.hexversion < 0x04000000:
	import cefpython_py32 as cefpython
else:
	raise Exception("Unsupported python version: %s" % sys.version)

import wx

class MainFrame(wx.Frame):

	browser = None

	def __init__(self):
		
		wx.Frame.__init__(self, parent=None, id=wx.ID_ANY, title='wxPython example', size=(600,400))
		self.CreateMenu()
		self.browser = cefpython.CreateBrowser(self.GetHandle(), browserSettings={}, navigateURL="cefsimple.html")		
		
		self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		"""self.Bind(wx.EVT_IDLE, self.OnIdle)"""
		
	def CreateMenu(self):

		filemenu = wx.Menu()
		filemenu.Append(1, "Open")
		filemenu.Append(2, "Exit")

		aboutmenu = wx.Menu()
		aboutmenu.Append(1, "CEF Python")

		menubar = wx.MenuBar()
		menubar.Append(filemenu,"&File")
		menubar.Append(aboutmenu, "&About")

		self.SetMenuBar(menubar)

	def OnSetFocus(self, event):

		cefpython.wm_SetFocus(self.GetHandle(), 0, 0, 0)

	def OnSize(self, event):

		cefpython.wm_Size(self.GetHandle(), 0, 0, 0)
      
	def OnClose(self, event):

		self.browser.CloseBrowser()
		self.Destroy()

	"""def OnIdle(self, event):
		cefpython.SingleMessageLoop()"""

class MyApp(wx.App):

	timer = None
	timerID = 1

	def OnInit(self):

		self.CreateTimer()
		frame = MainFrame()
		self.SetTopWindow(frame)
		frame.Show()
		return True

	def CreateTimer(self):

		# See "Making a render loop": http://wiki.wxwidgets.org/Making_a_render_loop
		# Another approach is to use EVT_IDLE in MainFrame, see which fits you better.
		self.timer = wx.Timer(self, self.timerID)
		self.timer.Start(10) # 10ms
		wx.EVT_TIMER(self, self.timerID, self.OnTimer)

	def OnTimer(self, event):

		cefpython.SingleMessageLoop()

	def OnExit(self):

		# When app.MainLoop() returns, SingleMessageLoop() should not be called anymore.
		self.timer.Stop()

if __name__ == '__main__':
	
	cefpython.Initialize() # Initialize cefpython before wx.
	sys.excepthook = cefpython.ExceptHook
	print('wx.version=%s' % wx.version())
	app = MyApp(False)
	app.MainLoop()
	cefpython.Shutdown()
