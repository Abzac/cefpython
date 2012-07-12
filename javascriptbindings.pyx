# Copyright (c) 2012 CefPython Authors. All rights reserved.
# License: New BSD License.
# Website: http://code.google.com/p/cefpython/

include "imports.pyx"

class JavascriptBindings:

	# By default we bind only to top frame.
	__bindToFrames = False
	__bindToPopups = False
	__functions = {}
	__properties = {}
	__v8properties = {}

	def __init__(self, bindToFrames=False, bindToPopups=False):

		self.__bindToFrames = bindToFrames
		self.__bindToPopups = bindToPopups

	def GetBindToFrames(self):

		return self.__bindToFrames

	def GetBindToPopups(self):

		return self.__bindToPopups

	def SetFunction(self, name, func):

		if type(func) == types.FunctionType or type(func) == types.MethodType:
			self.__functions[name] = func
		else:
			raise Exception("JavascriptBindings.SetFunction() failed: not allowed type: %s" % type(func).__name__)

	def GetFunction(self, name):

		if name in self.__functions:
			return self.__functions[name]

	def GetFunctions(self):

		return self.__functions

	def SetProperty(self, name, value):

		allowed = self.__IsTypeAllowed(value) # returns True or string.
		if allowed is not True:
			raise Exception("JavascriptBindings.SetProperty() failed: not allowed type: %s" % allowed)
		self.__properties[name] = value
	
	def GetProperty(self, name):

		# We must query CefV8Value for the real current value of property,
		# it could have been changed in javascript, use self.__v8properties.
		pass

	def __IsTypeAllowed(self, value):

		# Return value: True - allowed, string - not allowed

		# Not using type().__name__ here as it is not consistent, for int it is "int" but for None it is "NoneType".
		valueType = type(value) 
		if valueType == types.ListType:
			for val in value:
				valueType2 = self.__IsTypeAllowed(val)
				if valueType2 is not True:
					return valueType2.__name__
			return True
		elif valueType == types.BooleanType:
			return True
		elif valueType == types.FloatType:
			return True
		elif valueType == types.IntType:
			return True
		elif valueType == types.NoneType:
			return True
		elif valueType == types.DictType:
			for key in value:
				valueType2 = self.__IsTypeAllowed(value[key])
				if valueType2 is not True:
					return valueType2.__name__
			return True
		elif valueType == types.StringType:
			return True
		else:
			return valueType.__name__
