# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

from cef_base cimport CefBase

cdef extern from "include/cef_response.h":
	
	cdef cppclass CefResponse(CefBase):
		pass
