#ifndef __PYX_HAVE__cefpython
#define __PYX_HAVE__cefpython


#ifndef __PYX_HAVE_API__cefpython

#ifndef __PYX_EXTERN_C
  #ifdef __cplusplus
    #define __PYX_EXTERN_C extern "C"
  #else
    #define __PYX_EXTERN_C extern
  #endif
#endif

__PYX_EXTERN_C DL_IMPORT(bool) RequestHandler_OnBeforeBrowse(CefRefPtr<CefBrowser>, CefRefPtr<CefFrame>, CefRefPtr<CefRequest>, enum cef_handler_navtype_t, bool);
__PYX_EXTERN_C DL_IMPORT(bool) RequestHandler_OnBeforeResourceLoad(CefRefPtr<CefBrowser>, CefRefPtr<CefRequest>, CefString &, CefRefPtr<CefStreamReader> &, CefRefPtr<CefResponse>, int);
__PYX_EXTERN_C DL_IMPORT(void) RequestHandler_OnResourceRedirect(CefRefPtr<CefBrowser>, CefString &, CefString &);
__PYX_EXTERN_C DL_IMPORT(void) RequestHandler_OnResourceResponse(CefRefPtr<CefBrowser>, CefString &, CefRefPtr<CefResponse>, CefRefPtr<CefContentFilter> &);
__PYX_EXTERN_C DL_IMPORT(bool) RequestHandler_OnProtocolExecution(CefRefPtr<CefBrowser>, CefString &, bool &);
__PYX_EXTERN_C DL_IMPORT(bool) RequestHandler_GetDownloadHandler(CefRefPtr<CefBrowser>, CefString &, CefString &, int64, CefRefPtr<CefDownloadHandler> &);
__PYX_EXTERN_C DL_IMPORT(bool) RequestHandler_GetAuthCredentials(CefRefPtr<CefBrowser>, bool, CefString &, int, CefString &, CefString &, CefString &, CefString &);
__PYX_EXTERN_C DL_IMPORT(CefRefPtr<CefCookieManager>) RequestHandler_GetCookieManager(CefRefPtr<CefBrowser>, CefString &);
__PYX_EXTERN_C DL_IMPORT(void) DisplayHandler_OnAddressChange(CefRefPtr<CefBrowser>, CefRefPtr<CefFrame>, CefString &);
__PYX_EXTERN_C DL_IMPORT(bool) DisplayHandler_OnConsoleMessage(CefRefPtr<CefBrowser>, CefString &, CefString &, int);
__PYX_EXTERN_C DL_IMPORT(void) DisplayHandler_OnContentsSizeChange(CefRefPtr<CefBrowser>, CefRefPtr<CefFrame>, int, int);
__PYX_EXTERN_C DL_IMPORT(void) DisplayHandler_OnNavStateChange(CefRefPtr<CefBrowser>, bool, bool);
__PYX_EXTERN_C DL_IMPORT(void) DisplayHandler_OnStatusMessage(CefRefPtr<CefBrowser>, CefString &, enum cef_handler_statustype_t);
__PYX_EXTERN_C DL_IMPORT(void) DisplayHandler_OnTitleChange(CefRefPtr<CefBrowser>, CefString &);
__PYX_EXTERN_C DL_IMPORT(bool) DisplayHandler_OnTooltip(CefRefPtr<CefBrowser>, CefString &);

#endif /* !__PYX_HAVE_API__cefpython */

#if PY_MAJOR_VERSION < 3
PyMODINIT_FUNC initcefpython(void);
#else
PyMODINIT_FUNC PyInit_cefpython(void);
#endif

#endif /* !__PYX_HAVE__cefpython */
