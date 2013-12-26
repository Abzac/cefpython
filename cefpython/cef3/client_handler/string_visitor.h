// Copyright (c) 2012-2013 The CEF Python authors. All rights reserved.
// License: New BSD License.
// Website: http://code.google.com/p/cefpython/

#pragma once

#if defined(_WIN32)
#include "../windows/stdint.h"
#endif

#include "cefpython_public_api.h"

class StringVisitor : public CefStringVisitor
{
public:
    int stringVisitorId_;
public:
    StringVisitor(int stringVisitorId)
        : stringVisitorId_(stringVisitorId) {
    }

    virtual void Visit(
            const CefString& string
            ) OVERRIDE;
    
protected:
  // Include the default reference counting implementation.
  IMPLEMENT_REFCOUNTING(StringVisitor);
};
