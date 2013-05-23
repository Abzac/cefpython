# An example of embedding CEF browser in wxPython on Linux.

import ctypes, os, sys
libcef_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcef.so')
if os.path.exists(libcef_so):
    # Import local module
    ctypes.CDLL(libcef_so, ctypes.RTLD_GLOBAL)
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import from package
    from cefpython1 import cefpython

import wx
import time

# Which method to use for message loop processing.
#   EVT_IDLE - wx application has priority (default)
#   EVT_TIMER - cef browser has priority
# It seems that Flash content behaves better when using a timer.
# IMPORTANT! On Linux EVT_IDLE does not work, the events seems to 
# be propagated only when you move your mouse, which is not the 
# expected behavior, it is recommended to use EVT_TIMER on Linux,
# so set this value to False.
USE_EVT_IDLE = False

def GetApplicationPath(file=None):
    import re, os, platform
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        if hasattr(sys, "frozen"):
            path = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            path = os.path.dirname(os.path.realpath(__file__))
        else:
            path = os.getcwd()
        path = path + os.sep + file
        if platform.system() == "Windows":
            path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path
    return str(file)

def ExceptHook(type, value, traceObject):
    import traceback, os, time
    # This hook does the following: in case of exception display it,
    # write to error.log, shutdown CEF and exit application.
    error = "\n".join(traceback.format_exception(type, value, traceObject))
    error_file = GetApplicationPath("error.log")
    try:
        with open(error_file, "a") as file:
            file.write("\n[%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), error))
    except:
        # If this is an example run from 
        # /usr/local/lib/python2.7/dist-packages/cefpython1/examples/
        # then we might have not permission to write to that directory.
        print("cefpython: WARNING: failed writing to error file: %s" % (
                error_file))
    print("\n"+error+"\n")
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    # So that "finally" does not execute.
    os._exit(1)

class MainFrame(wx.Frame):
    browser = None
    initialized = False
    idleCount = 0
    box = None

    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                          title='wxPython example', size=(1024,768))
        self.CreateMenu()

        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(self.GetGtkWidget())
        # Linux requires adding "file://" for local files,
        # otherwise /home/some will be replaced as http://home/some
        self.browser = cefpython.CreateBrowserSync(
            windowInfo,
            # Flash will crash app in CEF 1 on Linux, setting
            # plugins_disabled to True.
            browserSettings={"plugins_disabled": True},
            navigateUrl="file://"+GetApplicationPath("wxpython.html"))

        self.browser.SetClientHandler(ClientHandler())
        
        jsBindings = cefpython.JavascriptBindings(
            bindToFrames=False, bindToPopups=True)
        jsBindings.SetObject("external", JavascriptBindings(self.browser))
        self.browser.SetJavascriptBindings(jsBindings)

        self.Bind(wx.EVT_CLOSE, self.OnClose)
        if USE_EVT_IDLE:
            # Bind EVT_IDLE only for the main application frame.
            self.Bind(wx.EVT_IDLE, self.OnIdle)

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

    def OnClose(self, event):
        self.browser.CloseBrowser()
        self.Destroy()

    def OnIdle(self, event):
        # self.idleCount += 1
        # print("wxpython.py: OnIdle() %d" % self.idleCount)
        cefpython.MessageLoopWork()

class JavascriptBindings:
    browser = None
    webRequest = None
    
    def __init__(self, browser):
        self.browser = browser

    def WebRequest(self, url):
        request = cefpython.Request.CreateRequest()
        request.SetUrl(url)
        webRequestClient = WebRequestClient()
        # Must keep the reference otherwise WebRequestClient 
        # callbacks won't be called.
        self.webRequest = cefpython.WebRequest.CreateWebRequest(request,
                webRequestClient)

    def DoCallFunction(self):
        self.browser.GetMainFrame().CallFunction(
                "MyFunction", "abc", 12, [1,2,3], {"qwe": 456, "rty": 789})

class WebRequestClient:
    def OnStateChange(self, webRequest, state):
        stateName = "unknown"
        for key, value in cefpython.WebRequest.State.iteritems():
            if value == state:
                stateName = key        
        print("WebRequestClient::OnStateChange(): state = %s" % stateName)

    def OnRedirect(self, webRequest, request, response):
        print("WebRequestClient::OnRedirect(): url = %s" % request.GetUrl())

    def OnHeadersReceived(self, webRequest, response):
        print("WebRequestClient::OnHeadersReceived(): headers = %s" % (
                response.GetHeaderMap()))

    def OnProgress(self, webRequest, bytesSent, totalBytesToBeSent):
        print("WebRequestClient::OnProgress(): bytesSent = %s, "
                "totalBytesToBeSent = %s" % (bytesSent, totalBytesToBeSent))

    def OnData(self, webRequest, data):
        print("WebRequestClient::OnData(): data:")
        print("-" * 60)
        print(data)
        print("-" * 60)

    def OnError(self, webRequest, errorCode):
        print("WebRequestClient::OnError(): errorCode = %s" % errorCode)

class ContentFilterHandler:
    def ProcessData(self, data, substitute_data):
        if data == "body { color: red; }":
            substitute_data.SetData("body { color: green; }")

    def Drain(self, remainder):
        remainder.SetData("body h3 { color: orange; }")

class ClientHandler:
    # Request handler, see documentation at:
    # https://code.google.com/p/cefpython/wiki/RequestHandler
    contentFilter = None    

    def OnBeforeBrowse(self, browser, frame, request, navType, isRedirect):
        # - frame.GetUrl() returns current url
        # - request.GetUrl() returns new url
        # - Return true to cancel the navigation or false to allow 
        # the navigation to proceed.
        # - Modifying headers or post data can be done only in
        # OnBeforeResourceLoad()
        print("OnBeforeBrowse(): request.GetUrl() = %s, "
                "request.GetHeaderMap(): %s" % (
                request.GetUrl(), request.GetHeaderMap()))
        if request.GetMethod() == "POST":
            print("OnBeforeBrowse(): POST data: %s" % (
                    request.GetPostData()))

    def OnBeforeResourceLoad(self, browser, request, redirectUrl, 
            streamReader, response, loadFlags):
        print("OnBeforeResourceLoad(): request.GetUrl() = %s" % (
                request.GetUrl()))
        if request.GetMethod() == "POST":
            if request.GetUrl().startswith(
                        "https://accounts.google.com/ServiceLogin"):
                postData = request.GetPostData()
                postData["Email"] = "--changed via python"
                request.SetPostData(postData)
                print("OnBeforeResourceLoad(): modified POST data: %s" % (
                        request.GetPostData()))
        if request.GetUrl().endswith("replace-on-the-fly.css"):
            print("OnBeforeResourceLoad(): replacing css on the fly")
            response.SetStatus(200)
            response.SetStatusText("OK")
            response.SetMimeType("text/css")
            streamReader.SetData("body { color: red; }")

    def OnResourceRedirect(self, browser, oldUrl, newUrl):
        print("OnResourceRedirect(): oldUrl: %s, newUrl: %s" % (
                oldUrl, newUrl[0]))

    def OnResourceResponse(self, browser, url, response, contentFilter):
        print("OnResourceResponse()")
        if url.endswith("content-filter/replace-on-the-fly.css"):
            print("OnResourceResponse(): setting contentFilter handler")
            contentFilter.SetHandler(ContentFilterHandler())
            # Must keep the reference to contentFilter otherwise
            # ContentFilterHandler callbacks won't be called.
            self.contentFilter = contentFilter

class MyApp(wx.App):
    timer = None
    timerID = 1
    timerCount = 0

    def OnInit(self):
        if not USE_EVT_IDLE:
            self.CreateTimer()
        frame = MainFrame()
        self.SetTopWindow(frame)
        frame.Show()
        return True

    def CreateTimer(self):
        # See "Making a render loop": 
        # http://wiki.wxwidgets.org/Making_a_render_loop
        # Another approach is to use EVT_IDLE in MainFrame,
        # see which one fits you better.
        self.timer = wx.Timer(self, self.timerID)
        self.timer.Start(10) # 10ms
        wx.EVT_TIMER(self, self.timerID, self.OnTimer)

    def OnTimer(self, event):
        self.timerCount += 1
        # print("wxpython.py: OnTimer() %d" % self.timerCount)
        cefpython.MessageLoopWork()

    def OnExit(self):
        # When app.MainLoop() returns, MessageLoopWork() should 
        # not be called anymore.
        if not USE_EVT_IDLE:
            self.timer.Stop()

if __name__ == '__main__':
    sys.excepthook = ExceptHook
    cefpython.g_debug = True
    cefpython.g_debugFile = GetApplicationPath("debug.log")
    settings = {
        "log_severity": cefpython.LOGSEVERITY_INFO,
        "log_file": GetApplicationPath("debug.log"),
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory()
    }
    cefpython.Initialize(settings)

    print('wx.version=%s' % wx.version())
    app = MyApp(False)
    app.MainLoop()
    # Let wx.App destructor do the cleanup before calling cefpython.Shutdown().
    del app

    cefpython.Shutdown()
