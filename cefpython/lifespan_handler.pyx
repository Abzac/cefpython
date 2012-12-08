# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

cdef public c_bool LifespanHandler_DoClose(
        CefRefPtr[CefBrowser] cefBrowser
        ) except * with gil:

    cdef PyBrowser pyBrowser
    try:
        pyBrowser = GetPyBrowser(cefBrowser)
        if not pyBrowser:
            Debug("LifespanHandler_DoClose() failed: pyBrowser is %s" % pyBrowser)
            return False
        callback = pyBrowser.GetClientCallback("DoClose")
        if callback:
            return bool(callback(pyBrowser))
        else:
            return False
    except:
        (exc_type, exc_value, exc_trace) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_trace)

cdef public void LifespanHandler_OnAfterCreated(
        CefRefPtr[CefBrowser] cefBrowser
        ) except * with gil:

    cdef PyBrowser pyBrowser
    try:
        pyBrowser = GetPyBrowser(cefBrowser)
        if not pyBrowser:
            Debug("LifespanHandler_OnAfterCreated() failed: pyBrowser is %s" % pyBrowser)
            return

        # Popup windows has no mouse/keyboard focus (Issue 14).
        pyBrowser.SetFocus(True)
        callback = pyBrowser.GetClientCallback("OnAfterCreated")
        if callback:
            callback(pyBrowser)
    except:
        (exc_type, exc_value, exc_trace) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_trace)

cdef public void LifespanHandler_OnBeforeClose(
        CefRefPtr[CefBrowser] cefBrowser
        ) except * with gil:

    cdef PyBrowser pyBrowser
    try:
        pyBrowser = GetPyBrowser(cefBrowser)
        if not pyBrowser:
            Debug("LifespanHandler_OnBeforeClose() failed: pyBrowser is %s" % pyBrowser)
            return
        callback = pyBrowser.GetClientCallback("OnBeforeClose")
        if callback:
            callback(pyBrowser)
    except:
        (exc_type, exc_value, exc_trace) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_trace)

cdef public c_bool LifespanHandler_RunModal(
        CefRefPtr[CefBrowser] cefBrowser
        ) except * with gil:

    cdef PyBrowser pyBrowser
    try:
        pyBrowser = GetPyBrowser(cefBrowser)
        if not pyBrowser:
            Debug("LifespanHandler_RunModal() failed: pyBrowser is %s" % pyBrowser)
            return False
        callback = pyBrowser.GetClientCallback("RunModal")
        if callback:
            return bool(callback(pyBrowser))
        return False
    except:
        (exc_type, exc_value, exc_trace) = sys.exc_info()
        sys.excepthook(exc_type, exc_value, exc_trace)

