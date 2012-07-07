# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

from windows cimport HWND
from cef_ptr cimport CefRefPtr
cimport cef_win
from cef_string cimport CefString
cimport cef_client
from cef_type_wrappers cimport CefSettings, CefBrowserSettings
from libcpp cimport bool as cbool
from libcpp.vector cimport vector
from cef_frame cimport CefFrame

cdef extern from "include/cef_browser.h":
	
	cdef cppclass CefBrowser:

		cbool CanGoBack()
		cbool CanGoForward()
		void ClearHistory()
		void CloseBrowser()
		void CloseDevTools()
		void Find(int identifier, CefString& searchText, cbool forward, cbool matchCase, cbool findNext)
		CefRefPtr[CefFrame] GetFocusedFrame()
		CefRefPtr[CefFrame] GetFrame(CefString& name)
		void GetFrameNames(vector[CefString]& names)
		# bool GetImage( CefBrowser::PaintElementType type, int width, int height, void* buffer )
		CefRefPtr[CefFrame] GetMainFrame()
		HWND GetOpenerWindowHandle()
		# bool GetSize( CefBrowser::PaintElementType type, int& width, int& height )
		HWND GetWindowHandle()
		double GetZoomLevel()
		void GoBack()
		void GoForward()
		cbool HasDocument()
		void HidePopup()
		# void Invalidate( const CefRect& dirtyRect )

		# ----------------------
		
		void ParentWindowWillClose()
		
		void SetZoomLevel(double zoomLevel)
		
		void ShowDevTools()
		
		void Reload()
		void ReloadIgnoreCache()
		void StopLoad()

		cbool IsPopup()


cdef extern from "include/cef_browser.h" namespace "CefBrowser":
	
	# Namespace is also a way to import a static method.	
	cdef CefRefPtr[CefBrowser] CreateBrowserSync(
		cef_win.CefWindowInfo, 
		CefRefPtr[cef_client.CefClient], 
		CefString,
		CefBrowserSettings)
