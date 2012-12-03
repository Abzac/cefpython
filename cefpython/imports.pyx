# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

include "include_cython/compile_time_constants.pxi"

import os
import sys
import cython
import platform
import traceback
import time
import types
import re
import copy
import inspect # used by JavascriptBindings.__SetObjectMethods()

# pywin32 extension is required by window_utils_win.pyx
import win32api
import win32gui
import win32con

if sys.version_info.major == 2:
	from urllib import pathname2url as urllib_pathname2url
else:
	from urllib.request import pathname2url as urllib_pathname2url

from libcpp cimport bool as c_bool
from libcpp.map cimport map as c_map
from multimap cimport multimap as c_multimap
from libcpp.pair cimport pair as c_pair
from libcpp.vector cimport vector as c_vector
from libcpp.string cimport string as c_string

# preincrement and dereference must be "as" otherwise not seen.
from cython.operator cimport preincrement as preinc, dereference as deref

# from cython.operator cimport address as addr # Address of an c++ object?

from libc.stdlib cimport calloc, malloc, free
from libc.stdlib cimport atoi

# When pyx file cimports * from a pxd file and that pxd cimports * from another pxd
# then these names will be visible in pyx file.

# Circular imports are allowed in form "cimport ...", but won't work if you do 
# "from ... cimport *", this is important to know in pxd files.

IF UNAME_SYSNAME == "Windows":
	from windows cimport *

from cef_string cimport *
from cef_types_wrappers cimport *
from cef_task cimport *

IF UNAME_SYSNAME == "Windows":
	from cef_win cimport *

from cef_ptr cimport *
from cef_app cimport *
from cef_browser cimport *
from cef_client cimport *
from client_handler cimport *
from cef_frame cimport *
cimport cef_types # cannot cimport *, that would cause name conflicts with constants.

IF UNAME_SYSNAME == "Windows":
	cimport cef_types_win # cannot cimport *, name conflicts

IF CEF_VERSION == 1:
	from cef_v8 cimport *
	cimport cef_v8_static
	cimport cef_v8_stack_trace
	from v8function_handler cimport *
	from cef_request cimport *
	from cef_response cimport *
	from cef_stream cimport *
	from cef_content_filter cimport *
	from cef_download_handler cimport *
	from cef_cookie cimport *

IF UNAME_SYSNAME == "Windows":
	IF CEF_VERSION == 1:
		from http_authentication cimport *
