// d:\cefpython\src\setup/cefpython.h(22) : warning C4190: 'RequestHandler_GetCookieManager'
// has C-linkage specified, but returns UDT 'CefRefPtr<T>' which is incompatible with C
#if defined(OS_WIN)
#pragma warning(disable:4190)
#endif

// All the imports that are required when including "cefpython.h".
#include "include/cef_client.h"
#include "include/cef_web_urlrequest.h"
#include "include/cef_cookie.h"
#include "util.h"

// To be able to use 'public' declarations you need to include Python.h and cefpython.h.
#include "Python.h"

// Python 3.2 fix - DL_IMPORT is not defined in Python.h
#ifndef DL_IMPORT /* declarations for DLL import/export */
#define DL_IMPORT(RTYPE) RTYPE
#endif
#ifndef DL_EXPORT /* declarations for DLL import/export */
#define DL_EXPORT(RTYPE) RTYPE
#endif

#if defined(OS_WIN)
#include "windows/setup/cefpython.h"
#endif

#if defined(OS_LINUX)
#include "linux/setup/cefpython.h"
#endif
