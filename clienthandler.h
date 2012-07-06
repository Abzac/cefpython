#include "include/cef_client.h"
#include "setup/cefpython_api.h"
#include <stdio.h>
#include "util.h"

// CefLoadHandler types.

typedef void (*OnLoadEnd_type)(CefRefPtr<CefBrowser> browser,
			 CefRefPtr<CefFrame> frame,
			 int httpStatusCode);

typedef void (*OnLoadStart_type)(CefRefPtr<CefBrowser> browser,
			   CefRefPtr<CefFrame> frame);
	
typedef bool (*OnLoadError_type)(CefRefPtr<CefBrowser> browser,
		   CefRefPtr<CefFrame> frame,
		   cef_handler_errorcode_t errorCode,
		   const CefString& failedUrl,
		   CefString& errorText);

// end of types.
			

class ClientHandler : public CefClient,
				public CefLoadHandler
{
public:
	ClientHandler(){}
	virtual ~ClientHandler(){}

	// CefClient methods
	virtual CefRefPtr<CefLifeSpanHandler> GetLifeSpanHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefLoadHandler> GetLoadHandler() OVERRIDE
	{ return this; }
	
	virtual CefRefPtr<CefRequestHandler> GetRequestHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefDisplayHandler> GetDisplayHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefFocusHandler> GetFocusHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefKeyboardHandler> GetKeyboardHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefMenuHandler> GetMenuHandler() OVERRIDE
	{ return NULL; }  
	
	virtual CefRefPtr<CefPermissionHandler> GetPermissionHandler() OVERRIDE
	{ return NULL; }  
	
	virtual CefRefPtr<CefPrintHandler> GetPrintHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefFindHandler> GetFindHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefJSDialogHandler> GetJSDialogHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefV8ContextHandler> GetV8ContextHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefRenderHandler> GetRenderHandler() OVERRIDE
	{ return NULL; }
	
	virtual CefRefPtr<CefDragHandler> GetDragHandler() OVERRIDE
	{ return NULL; }

	// CefLoadHandler methods.

	// OnLoadEnd.

	OnLoadEnd_type OnLoadEnd_callback;
	void SetCallback_OnLoadEnd(OnLoadEnd_type callback) 
	{
		this->OnLoadEnd_callback = callback; 
	}
	virtual void OnLoadEnd(CefRefPtr<CefBrowser> browser,
			 CefRefPtr<CefFrame> frame,
			 int httpStatusCode) OVERRIDE
	{
		REQUIRE_UI_THREAD();
		this->OnLoadEnd_callback(browser, frame, httpStatusCode);
	}
	
	// OnLoadStart.

	OnLoadStart_type OnLoadStart_callback;
	void SetCallback_OnLoadStart(OnLoadStart_type callback)
	{
		this->OnLoadStart_callback = callback;
	}
	virtual void OnLoadStart(CefRefPtr<CefBrowser> browser,
			   CefRefPtr<CefFrame> frame) OVERRIDE
	{
		REQUIRE_UI_THREAD();
		this->OnLoadStart_callback(browser, frame);
	}
	
	// OnLoadError.

	OnLoadError_type OnLoadError_callback;
	void SetCallback_OnLoadError(OnLoadError_type callback)
	{
		this->OnLoadError_callback = callback;
	}
	virtual bool OnLoadError(CefRefPtr<CefBrowser> browser,
			   CefRefPtr<CefFrame> frame,
			   cef_handler_errorcode_t errorCode,
			   const CefString& failedUrl,
			   CefString& errorText) OVERRIDE
	{
		REQUIRE_UI_THREAD();
		return this->OnLoadError_callback(browser, frame, errorCode, failedUrl, errorText);
	}

	
	
protected:
	 
	// Include the default reference counting implementation.
	IMPLEMENT_REFCOUNTING(ClientHandler);
	
	// Include the default locking implementation.
	IMPLEMENT_LOCKING(ClientHandler);

};
