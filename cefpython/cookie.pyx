# Copyright (c) 2012-2013 The CEF Python authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

#cdef Cookie cookie = Cookie()
#cookie.SetName("asd1")
#print("cookie.cefCookie: %s" % cookie.cefCookie)
#print("cookie.GetName(): %s" % cookie.GetName())
#print("cookie.GetCreation(): %s" % cookie.GetCreation())
#cookie.SetCreation(datetime.datetime(2013,5,23))
#print("cookie.GetCreation(): %s" % cookie.GetCreation())
#print("cookie: %s" % cookie.Get())

# ------------------------------------------------------------------------------
# Globals
# ------------------------------------------------------------------------------

cdef PyCookieManager g_globalCookieManager = None
# See StoreUserCookieVisitor().
cdef object g_userCookieVisitors = weakref.WeakValueDictionary()
cdef int g_userCookieVisitorMaxId = 0

# ------------------------------------------------------------------------------
# Cookie
# ------------------------------------------------------------------------------

ctypedef Cookie PyCookie

cdef PyCookie CreatePyCookie(CefCookie cefCookie):
    cdef PyCookie pyCookie = Cookie()
    pyCookie.cefCookie = cefCookie
    return pyCookie

cdef class Cookie:
    cdef CefCookie cefCookie

    cpdef py_void Set(self, dict cookie):
        for key in cookie:
            if key == "name":
                self.SetName(cookie[key])
            elif key == "value":
                self.SetValue(cookie[key])
            elif key == "domain":
                self.SetDomain(cookie[key])
            elif key == "path":
                self.SetPath(cookie[key])
            elif key == "secure":
                self.SetSecure(cookie[key])
            elif key == "httpOnly":
                self.SetHttpOnly(cookie[key])
            elif key == "creation":
                self.SetCreation(cookie[key])
            elif key == "lastAccess":
                self.SetLastAccess(cookie[key])
            elif key == "hasExpires":
                    self.SetHasExpires(cookie[key])
            elif key == "expires":
                self.SetExpires(cookie[key])
            else:
                raise Exception("Invalid key: %s" % key)

    cpdef dict Get(self):
        return {
            "name": self.GetName(),
            "value": self.GetValue(),
            "domain": self.GetDomain(),
            "path": self.GetPath(),
            "secure": self.GetSecure(),
            "httpOnly": self.GetHttpOnly(),
            "creation": self.GetCreation(),
            "lastAccess": self.GetLastAccess(),
            "hasExpires": self.GetHasExpires(),
            "expires": self.GetExpires(),
        }

    cpdef py_void SetName(self, py_string name):
        # This works:
        # | CefString(&self.cefCookie.name).FromString(name)
        # This does not work:
        # | cdef CefString cefString = CefString(&self.cefCookie.name)
        # | PyToCefString(name, cefString)
        # Because it's a Copy Constructor, it does not reference the
        # same underlying cef_string_t, instead it copies the value.
        # "T a(b)" - direct initialization (not supported by cython)
        # "T a = b" - copy initialization        
        # But this works:
        # | cdef CefString* cefString = new CefString(&self.cefCookie.name)
        # | PyToCefStringPointer(name, cefString)
        # | del cefString
        # Solution: use Attach() method to pass reference to cef_string_t.
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.name, False)
        PyToCefString(name, cefString)

    cpdef str GetName(self):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.name, False)
        return CefToPyString(cefString)

    cpdef py_void SetValue(self, py_string value):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.value, False)
        PyToCefString(value, cefString)

    cpdef str GetValue(self):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.value, False)
        return CefToPyString(cefString)

    cpdef py_void SetDomain(self, py_string domain):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.domain, False)
        PyToCefString(domain, cefString)

    cpdef str GetDomain(self):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.domain, False)
        return CefToPyString(cefString)

    cpdef py_void SetPath(self, py_string path):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.path, False)
        PyToCefString(path, cefString)

    cpdef str GetPath(self):
        cdef CefString cefString
        cefString.Attach(&self.cefCookie.path, False)
        return CefToPyString(cefString)

    cpdef py_void SetSecure(self, py_bool secure):
        self.cefCookie.secure = secure

    cpdef py_bool GetSecure(self):
        return self.cefCookie.secure

    cpdef py_void SetHttpOnly(self, py_bool httpOnly):
        self.cefCookie.httponly = httpOnly

    cpdef py_bool GetHttpOnly(self):
        return self.cefCookie.httponly

    cpdef py_void SetCreation(self, object creation):
        DatetimeToCefTimeT(creation, self.cefCookie.creation)

    cpdef object GetCreation(self):
        return CefTimeTToDatetime(self.cefCookie.creation)

    cpdef py_void SetLastAccess(self, object lastAccess):
        DatetimeToCefTimeT(lastAccess, self.cefCookie.last_access)

    cpdef object GetLastAccess(self):
        return CefTimeTToDatetime(self.cefCookie.last_access)

    cpdef py_void SetHasExpires(self, py_bool hasExpires):
        self.cefCookie.has_expires = hasExpires

    cpdef py_bool GetHasExpires(self):
        return self.cefCookie.has_expires

    cpdef py_void SetExpires(self, object expires):
        DatetimeToCefTimeT(expires, self.cefCookie.expires)

    cpdef object GetExpires(self):
        return CefTimeTToDatetime(self.cefCookie.expires)

# ------------------------------------------------------------------------------
# CookieManager
# ------------------------------------------------------------------------------

class CookieManager:
    @staticmethod
    def GetGlobalManager():
        global g_globalCookieManager
        cdef CefRefPtr[CefCookieManager] cefCookieManager
        if not g_globalCookieManager:
            cefCookieManager = cef_cookie_static.GetGlobalManager()
            g_globalCookieManager = CreatePyCookieManager(cefCookieManager)
        return g_globalCookieManager

    @staticmethod
    def CreateManager(py_string path):
        cdef CefRefPtr[CefCookieManager] cefCookieManager
        cefCookieManager = cef_cookie_static.CreateManager(
                PyToCefStringValue(path))
        if <void*>cefCookieManager != NULL and cefCookieManager.get():
            return CreatePyCookieManager(cefCookieManager)
        return None

# ------------------------------------------------------------------------------
# PyCookieManager
# ------------------------------------------------------------------------------

cdef PyCookieManager CreatePyCookieManager(
        CefRefPtr[CefCookieManager] cefCookieManager):
    cdef PyCookieManager pyCookieManager = PyCookieManager()
    pyCookieManager.cefCookieManager = cefCookieManager
    return pyCookieManager

cdef class PyCookieManager:
    cdef CefRefPtr[CefCookieManager] cefCookieManager

    cpdef py_void SetSupportedSchemes(self, list schemes):
        cdef cpp_vector[CefString] schemesVector
        for scheme in schemes:
            schemesVector.push_back(PyToCefStringValue(scheme))
        self.cefCookieManager.get().SetSupportedSchemes(schemesVector)

    cdef cpp_bool ValidateUserCookieVisitor(self, object userCookieVisitor
            ) except *:
        if userCookieVisitor and hasattr(userCookieVisitor, "Visit") and (
                callable(getattr(userCookieVisitor, "Visit"))):
            return True
        raise Exception("CookieVisitor object is missing Visit() method")

    cpdef cpp_bool VisitAllCookies(self, object userCookieVisitor) except *:
        self.ValidateUserCookieVisitor(userCookieVisitor)
        cdef int cookieVisitorId = StoreUserCookieVisitor(userCookieVisitor)
        cdef CefRefPtr[CefCookieVisitor] cefCookieVisitor = (
                <CefRefPtr[CefCookieVisitor]?>new CookieVisitor(
                        cookieVisitorId))
        self.cefCookieManager.get().VisitAllCookies(cefCookieVisitor)

    cpdef cpp_bool VisitUrlCookies(self, py_string url, 
            py_bool includeHttpOnly, object userCookieVisitor) except *:
        self.ValidateUserCookieVisitor(userCookieVisitor)
        cdef int cookieVisitorId = StoreUserCookieVisitor(userCookieVisitor)
        cdef CefRefPtr[CefCookieVisitor] cefCookieVisitor = (
                <CefRefPtr[CefCookieVisitor]?>new CookieVisitor(
                        cookieVisitorId))
        self.cefCookieManager.get().VisitUrlCookies(PyToCefStringValue(url),
                includeHttpOnly, cefCookieVisitor)

    cpdef py_void SetCookie(self, py_string url, PyCookie cookie):
        assert isinstance(cookie, Cookie), "cookie object is invalid"
        CefPostTask(TID_IO, NewCefRunnableMethod(self.cefCookieManager.get(),
                &cef_cookie_manager_namespace.SetCookie, 
                PyToCefStringValue(url), cookie.cefCookie))

    cpdef py_void DeleteCookies(self, py_string url, py_string cookie_name):
        CefPostTask(TID_IO, NewCefRunnableMethod(self.cefCookieManager.get(),
                &cef_cookie_manager_namespace.DeleteCookies, 
                PyToCefStringValue(url), PyToCefStringValue(cookie_name)))

    cpdef cpp_bool SetStoragePath(self, py_string path) except *:
        return self.cefCookieManager.get().SetStoragePath(
                PyToCefStringValue(path))

# ------------------------------------------------------------------------------
# PyCookieVisitor
# ------------------------------------------------------------------------------

cdef int StoreUserCookieVisitor(object userCookieVisitor) except * with gil:
    global g_userCookieVisitorMaxId
    global g_userCookieVisitors
    g_userCookieVisitorMaxId += 1
    g_userCookieVisitors[g_userCookieVisitorMaxId] = userCookieVisitor
    return g_userCookieVisitorMaxId

cdef PyCookieVisitor GetPyCookieVisitor(int cookieVisitorId):
    global g_userCookieVisitors
    cdef object userCookieVisitor
    cdef PyCookieVisitor pyCookieVisitor
    if cookieVisitorId in g_userCookieVisitors:
        userCookieVisitor = g_userCookieVisitors[cookieVisitorId]
        pyCookieVisitor = PyCookieVisitor(userCookieVisitor)
        return pyCookieVisitor

cdef class PyCookieVisitor:
    cdef object userCookieVisitor

    def __init__(self, object userCookieVisitor):
        self.userCookieVisitor = userCookieVisitor

    cdef object GetCallback(self, str funcName):
        if self.userCookieVisitor and (
                hasattr(self.userCookieVisitor, funcName) and (
                callable(getattr(self.userCookieVisitor, funcName)))):
            return getattr(self.userCookieVisitor, funcName)

# ------------------------------------------------------------------------------
# C++ CookieVisitor
# ------------------------------------------------------------------------------

cdef public cpp_bool CookieVisitor_Visit(
        int cookieVisitorId,
        const CefCookie& cookie,
        int count,
        int total,
        cpp_bool& deleteCookie
        ) except * with gil:
    assert IsThread(TID_IO), "Must be called on the IO thread"
    cdef PyCookieVisitor pyCookieVisitor = GetPyCookieVisitor(cookieVisitorId)
    cdef object callback
    cdef py_bool ret
    cdef PyCookie pyCookie = CreatePyCookie(cookie)
    cdef list pyDeleteCookie = [False]
    if pyCookieVisitor:
        callback = pyCookieVisitor.GetCallback("Visit")
        if callback:
            ret = callback(pyCookie, count, total, pyDeleteCookie)
            (&deleteCookie)[0] = bool(pyDeleteCookie[0])
            return bool(ret)
    return False
