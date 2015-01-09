// d:\cefpython\src\setup/cefpython.h(22) : warning C4190: 'RequestHandler_GetCookieManager'
// has C-linkage specified, but returns UDT 'CefRefPtr<T>' which is incompatible with C

#ifndef CEFPYTHON_PUBLIC_API_H
#define CEFPYTHON_PUBLIC_API_H

#if defined(OS_WIN)
#pragma warning(disable:4190)
#endif

// To be able to use 'public' declarations you need to include Python.h and cefpython.h.
// This include must be before including CEF, otherwise you get errors like:
// | /usr/include/python2.7/pyconfig.h:1161:0: warning: "_POSIX_C_SOURCE" redefined
// This file needs to be included first before CEF.
#include "Python.h"

// All the imports that are required when including "cefpython.h".
#include "include/cef_client.h"
#include "include/cef_urlrequest.h"
#include "include/cef_command_line.h"
#include "util.h"

// Python 3.2 fix - DL_IMPORT is not defined in Python.h
#ifndef DL_IMPORT /* declarations for DLL import/export */
#define DL_IMPORT(RTYPE) RTYPE
#endif
#ifndef DL_EXPORT /* declarations for DLL import/export */
#define DL_EXPORT(RTYPE) RTYPE
#endif

#if defined(OS_WIN)
#include "windows/setup/cefpython.h"
#elif defined(OS_LINUX)
#include "linux/setup/cefpython.h"
#elif defined(OS_MACOSX)
#include "mac/setup/cefpython.h"
#endif

// CEFPYTHON_PUBLIC_API_H
#endif
