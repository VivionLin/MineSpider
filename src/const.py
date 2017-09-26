# -*- coding: UTF-8 -*-
import sys

class _const:
	'python中没有类似const的常量，此类实现不可修改的常量'
	class SetConstError(TypeError):pass
	class GetConstError(LookupError):pass

	def __setattr__(self, key, value):
		if key in self.__dict__:
			print("Can't rebind const(%s)" % key) # 类字典中存在该变量名直接抛出异常
			raise self.SetConstError
		self.__dict__[key] = value

	def __getattr__(self, key):
		if key in self.__dict__:
			return self.key
		else:
			print("No const name %s" % key) # 类字典中没有该变量名时抛出异常
			raise self.GetConstError

sys.modules[__name__] = _const() # 向全局模块字典中注册_const