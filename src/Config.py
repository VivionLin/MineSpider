# -*- coding: UTF-8 -*-
import ConfigParser
import globals as glb
import const

class ConfigOperator:
	'配置文件保存与读取'

	def __init__(self):
		glb.cfgfile = 'settings.conf'
		self.sections = ['login', 'basic', 'advance', 'other']
		self.options = [
			['login_type', 'login_url'],
			['ref_ori', 'ref_type', 'ref_url', 'ref_deep', 'ref_load', 'ref_break', 'spider_type'],
			['img_fmt', 'dom_slc', 'dom_rmv', 'export_type', 'save_base'],
			['mode', 'thread_num']
		]
		self.defaults = [
			[const.LOGIN_TYPE_NOLOGIN, ''], 
			[0, 1, '', 0, 10, 10, {const.SPIDER_TYPE_IMG:0, const.SPIDER_TYPE_HTML:0, const.SPIDER_TYPE_TXT:0}],
			[
				[{'bmp':1}, {'gif':1}, {'jpg;jpeg':1}, {'png':1}, {'':0}],
				{
					const.SPIDER_TYPE_HREF:{},
					const.SPIDER_TYPE_IMG:{}, 
					const.SPIDER_TYPE_HTML:{}, 
					const.SPIDER_TYPE_TXT:{
						'body': const.FILTER_TYPE_CSS
					}
				},
				{
					const.SPIDER_TYPE_HREF:{},
					const.SPIDER_TYPE_IMG:{}, 
					const.SPIDER_TYPE_HTML:{}, 
					const.SPIDER_TYPE_TXT:{
						'script': const.FILTER_TYPE_CSS
					}
				},
				{const.SPIDER_TYPE_HTML:const.EXPORT_TYPE_HTML, const.SPIDER_TYPE_TXT:const.EXPORT_TYPE_TXT},
				{const.SPIDER_TYPE_IMG:'C:/Users/Administrator/Desktop/myspider/', const.SPIDER_TYPE_HTML:'C:/Users/Administrator/Desktop/myspider/', const.SPIDER_TYPE_TXT:'C:/Users/Administrator/Desktop/myspider/'}
			],
			[2, 3]
		]

	def loadConfig(self):
		# init
		cp = ConfigParser.ConfigParser()
		cp.read(glb.cfgfile)
		try:
			for idx in range(0, len(self.sections)):
				section = self.sections[idx]
				for option in self.options[idx]:
					glb.__setattr__(option, cp.get(section, option))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			self.initConfig()
		self.parseComplexPara()

	def saveConfig(self):
		# init
		cp = ConfigParser.ConfigParser()
		cp.read(glb.cfgfile)
		try:
			# update object
			for idx in range(0, len(self.sections)):
				section = self.sections[idx]
				for option in self.options[idx]:
					cp.set(section, option, glb.get(option))
			# write to file
			cp.write(open(glb.cfgfile, 'w'))
		except (ConfigParser.NoSectionError, ConfigParser.NoOptionError):
			self.initConfig()

	def initConfig(self):
		cp = ConfigParser.ConfigParser()
		cp.read(glb.cfgfile)
		for sidx in range(0, len(self.sections)):
			section = self.sections[sidx]
			if section not in cp.sections():
				cp.add_section(section)
			for oidx in range(0, len(self.options[sidx])):
				option = self.options[sidx][oidx]
				if option not in cp.options(section):
					value = self.defaults[sidx][oidx]
					glb.__setattr__(option, value)
					cp.set(section, option, value)
				else:
					if option not in glb.__dict__:
						glb.__setattr__(option, self.defaults[sidx][oidx])
		cp.write(open(glb.cfgfile, 'w'))

	def parseComplexPara(self):
		if type(glb.spider_type) != dict:
			glb.spider_type = self.parseStrToDict(glb.spider_type, int, int)
		if type(glb.img_fmt) != list:
			glb.img_fmt = self.parseStrToList(glb.img_fmt, dict, str, int)
		if type(glb.export_type) != dict:
			glb.export_type = self.parseStrToDict(glb.export_type, int, int)
		if type(glb.save_base) != dict:
			glb.save_base = self.parseStrToDict(glb.save_base, int, str)
		if type(glb.dom_slc) != dict:
			glb.dom_slc = self.parseStrToDict(glb.dom_slc, int, dict, str, int)
		if type(glb.dom_rmv) != dict:
			glb.dom_rmv = self.parseStrToDict(glb.dom_rmv, int, dict, str, int)

	def parseStrToDict(self, aimstr, keytype = None, valtype = None, valdict_keytype = None, valdict_valtype = None):
		dic = {}
		temp = aimstr
		temp = temp[1:len(temp) - 1].split(",")
		wait = False
		for temp_idx in range(0, len(temp)):
			tmp = temp[temp_idx]
			if wait != False:
				if tmp.rfind("}") == -1:
					wait = wait + "," + tmp
					continue
				else:
					tmp = wait + "," + tmp
					wait = False
			idx = tmp.find(":")
			key = tmp[:idx].strip()
			val = tmp[idx+1:].strip()
			if keytype != None:
				if keytype == int:
					key = int(key)
				elif keytype == bool:
					key = bool(key)
				elif keytype == str:
					if key.find("u'") == 0 and key.rfind("'") == len(key) - 1:
						key = unicode(key[2:len(key) - 1], "utf-8")
					if (key.find("'") == 0 and key.rfind("'") == len(key) - 1) or (key.find("\"") == 0 and key.rfind("\"") == len(key) - 1):
						key = key[1:len(key) - 1]
			if valtype != None:
				if valtype == int:
					val = int(val)
				elif valtype == bool:
					val = bool(val)
				elif valtype == str:
					if val.find("u'") == 0 and val.rfind("'") == len(val) - 1:
						val = unicode(val[2:len(val) - 1], "utf-8")
					if (val.find("'") == 0 and val.rfind("'") == len(val) - 1) or (val.find("\"") == 0 and val.rfind("\"") == len(val) - 1):
						val = val[1:len(val) - 1]
				elif valtype == dict:
					try:
						if val.find("{") != -1 and val.find("}") == -1:
							wait = tmp
							continue
						tmp = self.parseStrToDict(val, valdict_keytype, valdict_valtype)
						if valdict_keytype == None or valdict_keytype == str:
							val = {}
							for tmpk in tmp.keys():
								okey = tmpk
								if tmpk.find("'") == 0 and tmpk.rfind("'") == len(tmpk) - 1:
									tmpk = tmpk[1:len(tmpk) - 1]
								val[tmpk] = tmp[okey]
						else:
							val = tmp
					except ValueError:
						val = {}
			dic[key] = val
		return dic

	def parseStrToList(self, aimstr, valtype = None, valdict_keytype = None, valdict_valtype = None):
		lst = []
		temp = aimstr
		temp = temp[1:len(temp) - 1].split(",")
		for val in temp:
			val = val.strip()
			if valtype != None:
				if valtype == int:
					val = int(val)
				elif valtype == bool:
					val = int(val)
				elif valtype == dict:
					tmp = self.parseStrToDict(val, valdict_keytype, valdict_valtype)
					if valdict_keytype == None or valdict_keytype == str:
						val = {}
						for key in tmp.keys():
							okey = key
							if key.find("'") == 0 and key.rfind("'") == len(key) - 1:
								key = key[1:len(key) - 1]
							val[key] = tmp[okey]
					else:
						val = tmp
			lst.append(val)
		return lst