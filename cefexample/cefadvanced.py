# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

import cefpython # cefpython.pyd
import cefwindow
import win32con # pywin32 extension
import win32gui
import win32api
import sys
import re
import os

__browser = None

def CloseApplication(windowID, msg, wparam, lparam):

	browser = cefpython.GetBrowserByWindowID(windowID)
	browser.CloseBrowser()
	return win32gui.DefWindowProc(windowID, msg, wparam, lparam)

def QuitApplication(windowID, msg, wparam, lparam):

	win32gui.PostQuitMessage(0)
	return 0

def CefAdvanced():

	# This hook does the following: in case of exception display it, write to error.log, shutdown CEF and exit application.
	sys.excepthook = cefpython.ExceptHook 
	
	# Whether to print debug output to console.
	cefpython.__debug = True
	cefwindow.__debug = True 	

	# ApplicationSettings, see: http://code.google.com/p/cefpython/wiki/ApplicationSettings
	appSettings = dict()
	appSettings["multi_threaded_message_loop"] = False
	appSettings["log_file"] = cefpython.GetRealPath("debug.log")
	appSettings["log_severity"] = cefpython.LOGSEVERITY_VERBOSE # LOGSEVERITY_DISABLE - will not create "debug.log" file.
	cefpython.Initialize(applicationSettings=appSettings)

	wndproc = {
		win32con.WM_CLOSE: CloseApplication, 
		win32con.WM_DESTROY: QuitApplication,
		win32con.WM_SIZE: cefpython.wm_Size,
		win32con.WM_SETFOCUS: cefpython.wm_SetFocus,
		win32con.WM_ERASEBKGND: cefpython.wm_EraseBkgnd
	}
	windowID = cefwindow.CreateWindow("CefAdvanced", "cefadvanced", 800, 600, None, None, "icon.ico", wndproc)

	# BrowserSettings, see: http://code.google.com/p/cefpython/wiki/BrowserSettings
	browserSettings = dict() 
	browserSettings["history_disabled"] = False # Backspace key will act as "History back" action in browser.
	browserSettings["universal_access_from_file_urls_allowed"] = True
	browserSettings["file_access_from_file_urls_allowed"] = True
	
	handlers = dict()
	# Handler function for LoadHandler may be a tuple.
	# tuple[0] - the handler to call for the main frame.
	# tuple[1] - the handler to call for the inner frames (not in popups).
	# tuple[2] - the handler to call for the popups (only main frame).
	handlers["OnLoadStart"] = (OnLoadStart, None, OnLoadStart) # Document is ready. Developer tools window is also a popup, so this handler may be called.
	handlers["OnLoadError"] = OnLoadError
	handlers["OnKeyEvent"] = (OnKeyEvent, None, OnKeyEvent)

	# If you want a way to rebind javascript functions later, for example combined with use of Python's reload()
	# on module, so that you can make changes to app without re-launching application, then see Issue 12
	# for an example on how to do this: http://code.google.com/p/cefpython/issues/detail?id=12 (test_noreload2.zip).

	bindings = cefpython.JavascriptBindings(bindToFrames=False, bindToPopups=False)

	bindings.SetFunction("PyJavascriptError", PyJavascriptError)

	bindings.SetFunction("PyVersion", PyVersion)
	bindings.SetFunction("PyTest1", PyTest1)
	bindings.SetFunction("PyTest2", PyTest2)
	
	bindings.SetProperty("PyConfig", {"option1": True, "option2": 20})
	bindings.SetFunction("PrintPyConfig", PrintPyConfig)
	bindings.SetFunction("ChangePyConfig", ChangePyConfig)

	bindings.SetFunction("TestJavascriptCallback", TestJavascriptCallback)
	bindings.SetFunction("TestPythonCallbackThroughReturn", TestPythonCallbackThroughReturn)
	bindings.SetFunction("TestPythonCallbackThroughJavascriptCallback", TestPythonCallbackThroughJavascriptCallback)

	bindings.SetFunction("PyResizeWindow", PyResizeWindow)
	bindings.SetFunction("PyMoveWindow", PyMoveWindow)

	bindings.SetFunction("alert", PyAlert) # same as: bindings.SetProperty("alert", PyAlert)
	bindings.SetFunction("ChangeAlertDuringRuntime", ChangeAlertDuringRuntime)
	bindings.SetFunction("PyFind", PyFind)

	bindings.SetFunction("PyLoadURL", PyLoadURL)
	bindings.SetFunction("PyExecuteJavascript", PyExecuteJavascript)

	global __browser
	__browser = cefpython.CreateBrowser(windowID, browserSettings, "cefadvanced.html", handlers, bindings)
	print("CefAdvanced(): browser created")

	cefpython.MessageLoop()
	cefpython.Shutdown()

def PyExecuteJavascript(jsCode):

	__browser.GetMainFrame().ExecuteJavascript(jsCode)

def PyLoadURL():

	__browser.GetMainFrame().LoadURL(cefpython.GetRealPath("cefsimple.html"))

def PyJavascriptError(errorMessage, url, lineNumber):

	if re.match(r"file:/+", url):
		# Get a relative path of the html/js file, get rid of the "file://d:/.../cefpython/".
		url = re.sub(r"^file:/+", "", url)
		url = re.sub(r"[/\\]+", re.escape(os.sep), url)
		url = re.sub(r"%s" % re.escape(cefpython.GetRealPath()), "", url, flags=re.IGNORECASE)
		url = re.sub(r"^%s" % re.escape(os.sep), "", url)
	raise Exception("%s\n  in %s on line %s" % (errorMessage, url, lineNumber))

def PyVersion():

	return sys.version

def PyTest1(arg1):

	print("PyTest1(%s) called" % arg1)
	return "This string was returned from Python function PyTest1()"

def PyTest2(arg1, arg2):

	print("PyTest2(%s, %s) called" % (arg1, arg2))
	return [1,2, [2.1, {'3': 3, '4': [5,6]}]] # testing nested return values.

def PrintPyConfig():

	print("PrintPyConfig(): %s" % __browser.GetMainFrame().GetProperty("PyConfig"))

def ChangePyConfig():

	__browser.GetMainFrame().SetProperty("PyConfig", "Changed in python during runtime in ChangePyConfig()")

def TestJavascriptCallback(jsCallback):

	if isinstance(jsCallback, cefpython.JavascriptCallback):
		print("TestJavascriptCallback(): jsCallback.GetName(): %s" % jsCallback.GetName())
		print("jsCallback.Call(1, [2,3], ('tuple', 'tuple'), 'unicode string')")
		if bytes == str:
			# Python 2.7
			jsCallback.Call(1, [2,3], ('tuple', 'tuple'), unicode('unicode string'))
		else:
			# Python 3.2 - there is no "unicode()" in python 3
			jsCallback.Call(1, [2,3], ('tuple', 'tuple'), 'bytes string'.encode('utf-8'))
	else:
		raise Exception("TestJavascriptCallback() failed: given argument is not a javascript callback function")

def TestPythonCallbackThroughReturn():

	print("TestPythonCallbackThroughReturn() called, returning PyCallback.")
	return PyCallback

def PyCallback(*args):

	print("PyCallback() called, args: %s" % str(args))

def TestPythonCallbackThroughJavascriptCallback(jsCallback):

	print("TestPythonCallbackThroughJavascriptCallback(jsCallback) called")
	print("jsCallback.Call(PyCallback)")
	jsCallback.Call(PyCallback)

def PyAlert(msg):

	print("PyAlert() called instead of window.alert()")
	win32gui.MessageBox(__browser.GetWindowID(), msg, "PyAlert()", win32con.MB_ICONQUESTION)

def ChangeAlertDuringRuntime():

	__browser.GetMainFrame().SetProperty("alert", PyAlert2)

def PyAlert2(msg):

	print("PyAlert2() called instead of window.alert()")
	win32gui.MessageBox(__browser.GetWindowID(), msg, "PyAlert2()", win32con.MB_ICONWARNING)

def PyFind(searchText, findNext=False):

	__browser.Find(1, searchText, forward=True, matchCase=False, findNext=findNext)

def OnLoadStart(browser, frame):

	print("OnLoadStart(): frame URL: %s" % frame.GetURL())

def OnLoadError(browser, frame, errorCode, failedURL, errorText):

	print("OnLoadError() failedURL: %s" % (failedURL))
	errorText[0] = "Custom error message when loading URL fails, see: def OnLoadError()"
	return True

def OnKeyEvent(browser, eventType, keyCode, modifiers, isSystemKey, isAfterJavascript):

	# print("eventType = %s, keyCode=%s, modifiers=%s, isSystemKey=%s" % (eventType, keyCode, modifiers, isSystemKey))
	
	if eventType != cefpython.KEYEVENT_RAWKEYDOWN or isSystemKey:
		return False

	# Bind F12 to developer tools.
	if keyCode == cefpython.VK_F12 and cefpython.IsKeyModifier(cefpython.KEY_NONE, modifiers):
		browser.ShowDevTools()
		return True

	# Bind F5 to refresh browser window.
	if keyCode == cefpython.VK_F5 and cefpython.IsKeyModifier(cefpython.KEY_NONE, modifiers):
		browser.ReloadIgnoreCache()
		return True

	# Bind Ctrl(+) to increase zoom level
	if keyCode in (187, 107) and cefpython.IsKeyModifier(cefpython.KEY_CTRL, modifiers):
		browser.SetZoomLevel(browser.GetZoomLevel() +1)
		return True

	# Bind Ctrl(-) to reduce zoom level
	if keyCode in (189, 109) and cefpython.IsKeyModifier(cefpython.KEY_CTRL, modifiers):
		browser.SetZoomLevel(browser.GetZoomLevel() -1)
		return True

	return False

def PyResizeWindow():

	cefwindow.MoveWindow(__browser.GetWindowID(), width=500, height=500)

def PyMoveWindow():

	cefwindow.MoveWindow(__browser.GetWindowID(), xpos=0, ypos=0)

def PopupWindow():

	# TODO: creating popup windows through python.
	pass

def ModalWindow():

	# TODO: creating modal windows throught python.
	pass

def LoadContentFromZip():

	# TODO. Allow to pack html/css/images to a zip and run content from this file.
	# Optionally allow to password protect this zip file.
	pass

def LoadContentFromEncryptedZip():

	# TODO. This will be useful only if you protect your python sources by compiling them
	# to exe by using for example "pyinstaller", or even better you could compile sources
	# to a dll-like file called "pyd" by using cython extension, or you could combine them both.
	# See WBEA for implementation.
	pass

if __name__ == "__main__":
	
	CefAdvanced()
