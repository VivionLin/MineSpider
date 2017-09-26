# -*- coding: UTF-8 -*-
import sys

class _global:
	'可修改的全局变量类，跨文件共享变量'

	def __setattr__(self, key, value):
		self.__dict__[key] = value

	def get(self, key):
		return self.__dict__[key]

sys.modules[__name__] = _global()