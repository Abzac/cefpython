# An example of embedding CEF in wxPython application.

import platform
if platform.architecture()[0] != "32bit":
    raise Exception("Only 32bit architecture is supported")

import os, sys
libcef_dll = os.path.join(os.path.dirname(os.path.abspath(__file__)),
        'libcef.dll')
if os.path.exists(libcef_dll):
    # Import the local module.
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython
    elif 0x03000000 <= sys.hexversion < 0x04000000:
        import cefpython_py32 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import the package.
    from cefpython1 import cefpython

import wx
import time
import re
import uuid

# Which method to use for message loop processing.
#   EVT_IDLE - wx application has priority (default)
#   EVT_TIMER - cef browser has priority
# From the tests it seems that Flash content behaves
# better when using a timer.
USE_EVT_IDLE = True

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

def ExceptHook(excType, excValue, traceObject):
    import traceback, os, time, codecs
    # This hook does the following: in case of exception write it to
    # the "error.log" file, display it to the console, shutdown CEF
    # and exit application immediately by ignoring "finally" (_exit()).
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    errorFile = GetApplicationPath("error.log")
    try:
        appEncoding = cefpython.g_applicationSettings["string_encoding"]
    except:
        appEncoding = "utf-8"
    if type(errorMsg) == bytes:
        errorMsg = errorMsg.decode(encoding=appEncoding, errors="replace")
    try:
        with codecs.open(errorFile, mode="a", encoding=appEncoding) as fp:
            fp.write("\n[%s] %s\n" % (
                    time.strftime("%Y-%m-%d %H:%M:%S"), errorMsg))
    except:
        print("cefpython: WARNING: failed writing to error file: %s" % (
                errorFile))
    # Convert error message to ascii before printing, otherwise
    # you may get error like this:
    # | UnicodeEncodeError: 'charmap' codec can't encode characters
    errorMsg = errorMsg.encode("ascii", errors="replace")
    errorMsg = errorMsg.decode("ascii", errors="replace")
    print("\n"+errorMsg+"\n")
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    os._exit(1)

class MainFrame(wx.Frame):
    browser = None

    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                          title='wxPython example', size=(800,600))
        self.CreateMenu()

        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(self.GetHandle())
        self.browser = cefpython.CreateBrowserSync(windowInfo,
                browserSettings={},
                navigateUrl=GetApplicationPath("wxpython.html"))

        self.browser.SetClientHandler(ClientHandler())
        jsBindings = cefpython.JavascriptBindings(
            bindToFrames=False, bindToPopups=False)
        jsBindings.SetObject("external", JavascriptBindings(self.browser))
        self.browser.SetJavascriptBindings(jsBindings)

        self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        if USE_EVT_IDLE:
            # Bind EVT_IDLE only for the main application frame.
            self.Bind(wx.EVT_IDLE, self.OnIdle)

    def CreateMenu(self):
        filemenu = wx.Menu()
        filemenu.Append(1, "Open")
        exit = filemenu.Append(2, "Exit")
        self.Bind(wx.EVT_MENU, self.OnClose, exit)
        aboutmenu = wx.Menu()
        aboutmenu.Append(1, "CEF Python")
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        menubar.Append(aboutmenu, "&About")
        self.SetMenuBar(menubar)

    def OnSetFocus(self, event):
        cefpython.WindowUtils.OnSetFocus(self.GetHandle(), 0, 0, 0)

    def OnSize(self, event):
        cefpython.WindowUtils.OnSize(self.GetHandle(), 0, 0, 0)

    def OnClose(self, event):
        self.browser.CloseBrowser()
        self.Destroy()

    def OnIdle(self, event):
        cefpython.MessageLoopWork()

class JavascriptBindings:
    mainBrowser = None
    webRequest = None
    webRequestId = 0
    cookieVisitor = None

    def __init__(self, mainBrowser):
        self.mainBrowser = mainBrowser

    def WebRequest(self, url):
        request = cefpython.Request.CreateRequest()
        request.SetUrl(url)
        webRequestClient = WebRequestClient()
        # Must keep the reference otherwise WebRequestClient
        # callbacks won't be called.
        self.webRequest = cefpython.WebRequest.CreateWebRequest(request,
                webRequestClient)

    def DoCallFunction(self):
        self.mainBrowser.GetMainFrame().CallFunction(
                "MyFunction", "abc", 12, [1,2,3], {"qwe": 456, "rty": 789})

    def VisitAllCookies(self):
        # Need to keep the reference alive.
        self.cookieVisitor = CookieVisitor()
        cookieManager = self.mainBrowser.GetUserData("cookieManager")
        if not cookieManager:
            print("\nCookie manager not yet created! Visit http website first")
            return
        cookieManager.VisitAllCookies(self.cookieVisitor)

    def VisitUrlCookies(self):
        # Need to keep the reference alive.
        self.cookieVisitor = CookieVisitor()
        cookieManager = self.mainBrowser.GetUserData("cookieManager")
        if not cookieManager:
            print("\nCookie manager not yet created! Visit http website first")
            return
        cookieManager.VisitUrlCookies(
            "http://www.html-kit.com/tools/cookietester/",
            False, self.cookieVisitor)
        # .www.html-kit.com

    def SetCookie(self):
        cookieManager = self.mainBrowser.GetUserData("cookieManager")
        if not cookieManager:
            print("\nCookie manager not yet created! Visit http website first")
            return
        cookie = cefpython.Cookie()
        cookie.SetName("Created_Via_Python")
        cookie.SetValue("yeah really")
        cookieManager.SetCookie("http://www.html-kit.com/tools/cookietester/",
                cookie)
        print("\nCookie created! Visit html-kit cookietester to see it")

    def DeleteCookies(self):
        cookieManager = self.mainBrowser.GetUserData("cookieManager")
        if not cookieManager:
            print("\nCookie manager not yet created! Visit http website first")
            return
        cookieManager.DeleteCookies(
                "http://www.html-kit.com/tools/cookietester/",
                "Created_Via_Python")
        print("\nCookie deleted! Visit html-kit cookietester to see the result")

class CookieVisitor:
    def Visit(self, cookie, count, total, deleteCookie):
        if count == 0:
            print("\nCookieVisitor.Visit(): total cookies: %s" % total)
        print("\nCookieVisitor.Visit(): cookie:")
        print(cookie.Get())
        # True to continue visiting cookies
        return True

class WebRequestClient:
    def OnStateChange(self, webRequest, state):
        stateName = "unknown"
        for key, value in cefpython.WebRequest.State.iteritems():
            if value == state:
                stateName = key
        print("\nWebRequestClient::OnStateChange(): state = %s" % stateName)

    def OnRedirect(self, webRequest, request, response):
        print("\nWebRequestClient::OnRedirect(): url = %s" % (
                request.GetUrl()[:80]))

    def OnHeadersReceived(self, webRequest, response):
        print("\nWebRequestClient::OnHeadersReceived(): headers = %s" % (
                response.GetHeaderMap()))

    def OnProgress(self, webRequest, bytesSent, totalBytesToBeSent):
        print("\nWebRequestClient::OnProgress(): bytesSent = %s, "
                "totalBytesToBeSent = %s" % (bytesSent, totalBytesToBeSent))

    def OnData(self, webRequest, data):
        print("\nWebRequestClient::OnData(): data:")
        print("-" * 60)
        print(data)
        print("-" * 60)

    def OnError(self, webRequest, errorCode):
        print("\nWebRequestClient::OnError(): errorCode = %s" % errorCode)

class ContentFilterHandler:
    def OnData(self, data, substitute_data):
        if data == "body { color: red; }":
            substitute_data.SetData("body { color: green; }")

    def OnDrain(self, remainder):
        remainder.SetData("body h3 { color: orange; }")

class ClientHandler:
    # --------------------------------------------------------------------------
    # RequestHandler
    # --------------------------------------------------------------------------
    contentFilter = None

    def OnBeforeBrowse(self, browser, frame, request, navType, isRedirect):
        # - frame.GetUrl() returns current url
        # - request.GetUrl() returns new url
        # - Return true to cancel the navigation or false to allow
        # the navigation to proceed.
        # - Modifying headers or post data can be done only in
        # OnBeforeResourceLoad()
        print("\nOnBeforeBrowse(): request.GetUrl() = %s, "
                "request.GetHeaderMap(): %s" % (
                request.GetUrl()[:80], request.GetHeaderMap()))
        if request.GetMethod() == "POST":
            print("\nOnBeforeBrowse(): POST data: %s" % (
                    request.GetPostData()))

    def OnBeforeResourceLoad(self, browser, request, redirectUrl,
            streamReader, response, loadFlags):
        print("\nOnBeforeResourceLoad(): request.GetUrl() = %s" % (
                request.GetUrl()[:80]))
        if request.GetMethod() == "POST":
            if request.GetUrl().startswith(
                        "https://accounts.google.com/ServiceLogin"):
                postData = request.GetPostData()
                postData["Email"] = "--changed via python"
                request.SetPostData(postData)
                print("\nOnBeforeResourceLoad(): modified POST data: %s" % (
                        request.GetPostData()))
        if request.GetUrl().endswith("replace-on-the-fly.css"):
            print("\nOnBeforeResourceLoad(): replacing css on the fly")
            response.SetStatus(200)
            response.SetStatusText("OK")
            response.SetMimeType("text/css")
            streamReader.SetData("body { color: red; }")

    def OnResourceRedirect(self, browser, oldUrl, newUrl):
        print("\nOnResourceRedirect(): oldUrl: %s, newUrl: %s" % (
                oldUrl, newUrl[0]))

    def OnResourceResponse(self, browser, url, response, contentFilter):
        print("\nOnResourceResponse(): url = %s, headers = %s" % (
                url[:80], response.GetHeaderMap()))
        if url.endswith("content-filter/replace-on-the-fly.css"):
            print("\nOnResourceResponse(): setting contentFilter handler")
            contentFilter.SetHandler(ContentFilterHandler())
            # Must keep the reference to contentFilter otherwise
            # ContentFilterHandler callbacks won't be called.
            self.contentFilter = contentFilter

    def GetCookieManager(self, browser, mainUrl):
        # Create unique cookie manager for each browser.
        cookieManager = browser.GetUserData("cookieManager")
        if cookieManager:
            return cookieManager
        else:
            cookieManager = cefpython.CookieManager.CreateManager("")
            browser.SetUserData("cookieManager", cookieManager)
            return cookieManager

    # --------------------------------------------------------------------------
    # DragHandler
    # --------------------------------------------------------------------------

    def OnDragStart(self, browser, dragData, mask):
        maskNames = ""
        for key, value in cefpython.Drag.Operation.iteritems():
            if value and (value & mask) == value:
                maskNames += " "+key
        print("\nOnDragStart(): mask=%s" % maskNames)
        print("  IsLink(): %s" % dragData.IsLink())
        print("  IsFragment(): %s" % dragData.IsFragment())
        print("  IsFile(): %s" % dragData.IsFile())
        print("  GetLinkUrl(): %s" % dragData.GetLinkUrl())
        print("  GetLinkTitle(): %s" % dragData.GetLinkTitle())
        print("  GetLinkMetadata(): %s" % dragData.GetLinkMetadata())
        print("  GetFragmentText(): %s" % dragData.GetFragmentText())
        print("  GetFragmentHtml(): %s" % dragData.GetFragmentHtml())
        print("  GetFragmentBaseUrl(): %s" % dragData.GetFragmentBaseUrl())
        print("  GetFile(): %s" % dragData.GetFile())
        print("  GetFiles(): %s" % dragData.GetFiles())
        # Returning True on Linux causes segmentation fault,
        # reported the bug here:
        # http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=10693
        # Not being able to cancel a drag event is a problem
        # only when a link or a folder is dragged, as this will
        # cause loading the link or the folder in the browser window.
        # When dragging text/html or a file it is not a problem, as
        # it does not lead to browser navigating.
        if platform.system() == "Windows":
            # Return true to cancel the drag event.
            return True
        else:
            return False

    def OnDragEnter(self, browser, dragData, mask):
        maskNames = ""
        for key, value in cefpython.Drag.Operation.iteritems():
            if value and (value & mask) == value:
                maskNames += " "+key
        print("\nOnDragEnter(): mask=%s" % maskNames)
        print("  IsLink(): %s" % dragData.IsLink())
        print("  IsFragment(): %s" % dragData.IsFragment())
        print("  IsFile(): %s" % dragData.IsFile())
        print("  GetLinkUrl(): %s" % dragData.GetLinkUrl())
        print("  GetLinkTitle(): %s" % dragData.GetLinkTitle())
        print("  GetLinkMetadata(): %s" % dragData.GetLinkMetadata())
        print("  GetFragmentText(): %s" % dragData.GetFragmentText())
        print("  GetFragmentHtml(): %s" % dragData.GetFragmentHtml())
        print("  GetFragmentBaseUrl(): %s" % dragData.GetFragmentBaseUrl())
        print("  GetFile(): %s" % dragData.GetFile())
        print("  GetFiles(): %s" % dragData.GetFiles())
        # Returning True on Linux causes segmentation fault,
        # reported the bug here:
        # http://www.magpcss.org/ceforum/viewtopic.php?f=6&t=10693
        # Not being able to cancel a drag event is a problem
        # only when a link or a folder is dragged, as this will
        # cause loading the link or the folder in the browser window.
        # When dragging text/html or a file it is not a problem, as
        # it does not lead to browser navigating.
        if platform.system() == "Windows":
            # Return true to cancel the drag event.
            return True
        else:
            return False

    # --------------------------------------------------------------------------
    # DownloadHandler
    # --------------------------------------------------------------------------

    downloadHandler = None

    def GetDownloadHandler(self, browser, mimeType, filename, contentLength):
        # Close the browser window if it is a popup with
        # no other document contents.
        if browser.IsPopup() and not browser.HasDocument():
            browser.CloseBrowser()
        # The reference to DownloadHandler must be kept alive
        # while download proceeds.
        if self.downloadHandler and self.downloadHandler.downloading:
            print("\nDownload is already in progress")
            return False
        self.downloadHandler = DownloadHandler(mimeType, filename,
                contentLength)
        return self.downloadHandler

class DownloadHandler:
    mimeType = ""
    filename = ""
    contentLength = -1 # -1 means that file size was not provided.
    fp = None
    downloadsDir = "./downloads"
    alreadyDownloaded = 0
    downloading = False

    def __init__(self, mimeType, filename, contentLength):
        self.downloading = True
        if not os.path.exists(self.downloadsDir):
            os.mkdir(self.downloadsDir)
        filename = filename.strip()
        if not len(filename):
            filename = self.GetUniqueFilename()
        filename = self.GetSafeFilename(filename)
        print("\nDownloadHandler() created")
        print("mimeType: %s" % mimeType)
        print("filename: %s" % filename)
        print("contentLength: %s" % contentLength)
        # Append ".downloading" to the filename, in OnComplete()
        # when download finishes get rid of this extension.
        filename += ".downloading"
        if os.path.exists(self.downloadsDir+"/"+filename):
            # If the last download did not succeed, the
            # "xxx.downloading" might still be there.
            os.remove(self.downloadsDir+"/"+filename)
        self.mimeType = mimeType
        self.filename = filename
        self.contentLength = contentLength
        self.fp = open(self.downloadsDir+"/"+filename, "wb")

    def GetSafeFilename(self, filename):
        # TODO:
        # - remove any unsafe characters (".." or "/" or "\" and
        #   others), the safest way is to have a regexp with a list
        #   safe characters. The dots ".." is a special case that
        #   needs to be treated separately.
        if os.path.exists(self.downloadsDir+"/"+filename):
            filename = self.GetUniqueFilename()[:4]+"_"+filename
            assert not os.path.exists(self.downloadsDir+"/"+filename), (
                    "File aready exists")
        return filename

    def GetUniqueFilename(self):
        # The filename may be empty, in that case generate
        # an unique name.
        # TODO:
        # - guess the extension using the mimeType (but mimeType
        #   may also be empty), "text/css" => ".css".
        return str(uuid.uuid4()).replace("-", "")[:16]

    def OnData(self, data):
        # TODO: display progress in percentage or/and KiB/MiB.
        if self.alreadyDownloaded == 0:
            sys.stdout.write("Download progress: ")
        sys.stdout.write(".")
        sys.stdout.flush()
        self.alreadyDownloaded += len(data)
        self.fp.write(data)
        # time.sleep(1) # Let's make the progress a bit slower (if cached)
        # Return True to continue receiving data, False to cancel.
        return True

    def OnComplete(self):
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.fp.close()
        currentFile = self.downloadsDir+"/"+self.filename
        newFilename = re.sub(".downloading$", "", self.filename)
        os.rename(self.downloadsDir+"/"+self.filename,
                self.downloadsDir+"/"+newFilename)
        self.downloading = False
        print("\nDownload complete!")
        print("Total downloaded: %s" % self.PrettyBytes(
                self.alreadyDownloaded))
        print("See the 'downloads' directory.")

    def PrettyBytes(self, bytes):
        KiB = 1024
        return "%.3g KiB" % (bytes / KiB)

class MyApp(wx.App):
    timer = None
    timerID = 1

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
        cefpython.MessageLoopWork()

    def OnExit(self):
        # When app.MainLoop() returns, MessageLoopWork() should
        # not be called anymore.
        if not USE_EVT_IDLE:
            self.timer.Stop()

if __name__ == '__main__':
    sys.excepthook = ExceptHook
    # cefpython.g_debug = True
    # cefpython.g_debugFile = GetApplicationPath("debug.log")
    settings = {
        "log_severity": cefpython.LOGSEVERITY_INFO,
        "log_file": GetApplicationPath("debug.log"),
        "release_dcheck_enabled": True # Enable only when debugging.
    }
    cefpython.Initialize(settings)
    print('wx.version=%s' % wx.version())
    app = MyApp(False)
    app.MainLoop()
    # Let wx.App destructor do the cleanup before calling cefpython.Shutdown().
    del app
    cefpython.Shutdown()
