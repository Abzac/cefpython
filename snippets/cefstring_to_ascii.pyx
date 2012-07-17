print("Converting back cefUrl to ascii:")
cdef wchar_t* urlwide = <wchar_t*> cefUrl.c_str()
cdef int urlascii_size = WideCharToMultiByte(CP_UTF8, 0, urlwide, -1, NULL, 0, NULL, NULL)
print("urlascii_size: %s" % urlascii_size)
cdef char* urlascii = <char*>malloc(urlascii_size*sizeof(char))
WideCharToMultiByte(CP_UTF8, 0, urlwide, -1, urlascii, urlascii_size, NULL, NULL)
if bytes == str:
		urlascii = "" + urlascii # Python 2.7
	else:
		urlascii = (b"" + urlascii).decode("utf-8") # Python 3
print("urlascii: %s" % urlascii)
free(urlascii)
print("GetLastError(): %s" % GetLastError())
