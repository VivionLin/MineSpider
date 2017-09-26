# -*- coding: UTF-8 -*-
import urllib
import urllib2
import httplib
import cookielib
import os
import sys
import xlwt
import re
import bs4
import time
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from ConstPara import const
from RefUrlPool import RefUrlPool
from Config import *

class MySpider:
	'抓取程序后台'
	class IncorrectDriver(ImportError):pass

	def __init__(self):
		self.log_save_base = ""
		self.opener = None
		self.rup = None
		self.threads = None
		self.threadLock = threading.Lock()
		self.handles = None

	# 初始化全局opener
	def initOpener(self):
		if glb.mode == 0:
			cj = cookielib.CookieJar()
			self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
			self.opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')]
		elif glb.mode in [1, 2]:
			try:
				self.opener = webdriver.Chrome()
				self.opener.implicitly_wait(glb.ref_load)
			except Exception:
				raise self.IncorrectDriver, "Can't find the driver."

	# 自动跳过登录页面(登录地址，登录要提交的数据)，访问后自动带上cookie
	def autoLogin(self, login_url, login_form, login_data):
		if glb.mode == 0:
			if glb.login_type == const.LOGIN_TYPE_NOLOGIN: # 无需登录
				if login_url != None:
					self.opener.open(login_url)
			elif glb.login_type == const.LOGIN_TYPE_AUTO: # 自动识别表单登录
				login_datas = self.builtLoginFormData(login_url, login_form)
				data = urllib.urlencode(login_datas[glb.login_form_idx - 1])
				self.opener.open(login_url, data)
			elif glb.login_type == const.LOGIN_TYPE_MANUAL: # POST数据填写登录
				data = urllib.urlencode(login_data)
				self.opener.open(login_url, data)
		elif glb.mode == 1:
			if glb.login_type == const.LOGIN_TYPE_NOLOGIN: # 无需登录
				pass
			elif glb.login_type == const.LOGIN_TYPE_AUTO: # 自动识别表单登录
				if login_url != None:
					self.opener.get(login_url)
					login_datas = self.builtLoginFormData(login_url, login_form)
					login_data = login_datas[glb.login_form_idx - 1]
					for data in login_data.keys():
						elem = self.opener.find_element_by_name(data)
						try:
							elem.send_keys(login_data[data])
						except Exception:
							continue
					elem.send_keys(Keys.RETURN)
		elif glb.mode == 2:
			if glb.login_type == const.LOGIN_TYPE_NOLOGIN:pass
			elif glb.login_type == const.LOGIN_TYPE_AUTO: # 要登录
				if login_url != None:
					self.opener.get(login_url)
					return False
			elif glb.login_type == const.LOGIN_TYPE_MANUAL:pass
		return True

	# 识别登录页的表单并填入数据
	def builtLoginFormData(self, login_url, login_form):
		login_datas = []
		if glb.mode == 0:
			login_op = self.opener.open(login_url)
			html = login_op.read()
		elif glb.mode == 1:
			html = self.opener.page_source
		soup = BeautifulSoup(html)
		fms = soup.select("form")
		glb.login_form_num = []
		for fm_idx in range(0, len(fms)): # 每一个表单
			fm = fms[fm_idx]
			if fm_idx + 1 not in glb.login_form_num:
				glb.login_form_num.append(fm_idx + 1)
			login_data = {}
			rinps = []
			inps = fm.select("input")
			for inp in inps: # 输入标签检查
				if inp["type"] != "text" and inp["type"] != "input" and inp["type"] != "" and inp["type"] != "password":
					if inp["name"] != "":
						try:
							login_data[inp["name"]] = inp["value"] # 要提交但不是输入的域添加默认值
						except:
							login_data[inp["name"]] = ""
					inp.extract()
				else:
					rinps.append(inp)
			if len(rinps) < len(login_form): # 不正确的表单去除
				pass
			else:
				i = 0
				for inp in rinps:
					login_data[inp["name"]] = login_form[i]
					i += 1
			login_datas.append(login_data)
		return login_datas

	# 获取页面内容(目标地址)
	def getHtml(self, threadName, ref_url):
		html = ""
		url = ""
		if glb.ref_type == const.REF_TYPE_DIR or (glb.ref_ori == const.REF_ORI_PROJECT and glb.ref_type == const.REF_TYPE_FILE):
			# 读取本地文件
			url = self.addUrlPrefix(ref_url)
			ori_urlfn = self.getFileName(url)
			urlfilename_idx = url.find(ori_urlfn)
			if urlfilename_idx == -1:
				urlfilename_idx = url.rfind("/") + 1
			fmt_idx = url[urlfilename_idx:].rfind(".");
			if len(ori_urlfn) > 0 and fmt_idx > -1:
				# 有文件名也有后缀名
				pass
			else:
				# 无文件名或也无后缀名
				if len(ori_urlfn) == 0:
					url = url + self.addUrlSuffix(ori_urlfn)
				else:
					# 有文件名没有后缀名
					url = url[:urlfilename_idx] + self.addUrlSuffix(ori_urlfn)
			self.saveLog("-"*10 + "\n[" + threadName + "] 开始访问......" + time.asctime(time.localtime(time.time())) + "\n" + url)
			html += self.getContentFromLocalFile(url)
		else:
			# 网站
			if glb.ref_ori != const.REF_ORI_LOCAL:
				url = self.addUrlPrefix(ref_url)
			elif glb.ref_ori != const.REF_ORI_PROJECT:
				url = ref_url
			self.saveLog("-"*10 + "\n[" + threadName + "] 开始访问......" + time.asctime(time.localtime(time.time())) + "\n" + url)
			if glb.mode == 0:
				while True:
					try:
						op = self.opener.open(url)	# 以带cookie的方式访问其它页面
						break
					except httplib.BadStatusLine:
						self.opener = None
						time.sleep(300)
						self.initOpener()
						self.saveLog("-"*10 + "\n尝试重新连接......")
				html += op.read()
			elif glb.mode in [1, 2]:
				self.threadLock.acquire()
				time.sleep(glb.ref_break)
				self.saveLog("-"*10 + "\n[" + threadName + "] 正在访问......" + time.asctime(time.localtime(time.time())) + "\n" + url)
				print(threadName)
				if len(self.opener.window_handles) == 1 and self.handles[0] == None:
					self.opener.get(url)
					self.refreshHandles(threadName)
				else:
					handle = self.handles[self.getIdxByThreadName(threadName)]
					if handle == None:
						self.opener.execute_script('window.open("' + url + '");')
						self.opener.switch_to_window(self.refreshHandles(threadName))
					else:
						self.opener.switch_to_window(handle)
						self.opener.get(url)
				html += self.opener.page_source
				self.threadLock.release()
		print("visiting......" + url)
		return html

	# 根据线程名称获取数组下标
	def getIdxByThreadName(self, threadName):
		return (int)(threadName[threadName.find("-")+2:]) - 1

	# 更新浏览器窗口对象数组
	def refreshHandles(self, threadName):
		idx_num = self.getIdxByThreadName(threadName)
		tabs = self.opener.window_handles
		self.handles[idx_num] = tabs[len(tabs) - 1]
		return self.handles[idx_num]

	# 关闭多打开的窗口
	def closeHandles(self, threadName):
		idx_num = self.getIdxByThreadName(threadName)
		if self.opener != None and self.opener.window_handles != None and len(self.opener.window_handles) > 1:
			hd = self.handles[idx_num]
			if hd != None:
				self.opener.switch_to_window(hd)
				self.opener.close()
				self.handles[idx_num] = None

	# 筛选页面内容（待筛选内容，筛选条件）
	def filterHtml(self, html, res_type, rmv_term, slc_term):
		# 默认固定条件
		if res_type == const.SPIDER_TYPE_TXT:
			rmv_term["script, style"] = const.FILTER_TYPE_CSS
		html = self.rmvContent(html, rmv_term, res_type)
		html = self.slcContent(html, slc_term, res_type)
		return html

	# 筛选出相关链接
	def extractHref(self, html):
		ref_urls = []
		if html != None:
			soup = BeautifulSoup(html)
			adoms = soup.select("a")
			for adom in adoms:
				try:
					ref_url = adom["href"]
					if ref_url != "" and "javascript:" not in ref_url and "#" not in ref_url and ref_url not in ref_urls:
						ref_urls.append(ref_url)
				except KeyError:
					pass
		return ref_urls

	# 筛选出图片元素（待筛选内容）
	def extractImgs(self, html, url):
		imgurls = []
		soup = BeautifulSoup(html)
		imgdoms = soup.select("img")
		for imgdom in imgdoms:
			src = imgdom["src"]
			if len(src) > 0 and not(src.isspace()):
				src = self.addUrlPrefix(src)
				if not(self.filterFmt(src)) and not(src in imgurls): # 去掉格式不符合的和重复的
					imgurls.append(src)
		return imgurls

	# 抽取出网页内容
	def extractHtml(self, html):
		return html

	# 抽取出文本内容
	def extractWords(self, html):
		soup = BeautifulSoup(html)
		if glb.export_type[const.SPIDER_TYPE_TXT] == const.EXPORT_TYPE_TXT:pass
		elif glb.export_type[const.SPIDER_TYPE_TXT] == const.EXPORT_TYPE_EXCEL:
			return self.extractTableAndList(soup)
		return self.extractText(soup)

	# 抽取出文本list
	def extractText(self, soup):
		words = []
		doms = soup.findAll(text = True)
		for dom in doms:
			if type(dom) not in [bs4.element.Doctype, bs4.element.Comment] and not(dom.isspace()):
				words.append(dom.strip())
		return words

	# 抽取出表格
	def extractTable(self, wordsfam, soup):
		tabledoms = soup.select("table") # 所有表格
		for tabledom in tabledoms:
			trdoms = tabledom.select("tr") # 表格的每一行
			tb = []
			for trdom in trdoms:
				tddoms = trdom.select("td") # 表格的每一行的每一列
				if len(tddoms) == 0:
					tddoms = trdom.select("th")
				line = []
				for tddom in tddoms:
					txts = tddom.findAll(text = True)
					tdtxt = ""
					for txt in txts:
						if type(txt) != bs4.element.Comment and not(txt.isspace()): # 去除空格文本
							tdtxt += txt.strip()
					if len(tdtxt) > 0:
						line.append(tdtxt)
				if len(line) > 0:
					tb.append(line)
			if len(tb) > 0:
				wordsfam[str(len(wordsfam)) + " - Table"] = tb
			tabledom.extract()

	# 抽取出列表
	def extractList(self, wordsfam, soup):
		ullis = []
		uldoms = soup.select("ul") # 所有无序列表
		for uldom in uldoms:
			lidoms = uldom.select("li")
			ul = []
			for lidom in lidoms:
				litxt = ""
				txts = lidom.findAll(text = True)
				for txt in txts:
					if type(txt) != bs4.element.Comment and not(txt.isspace()):
						litxt += txt.strip()
				if len(litxt) > 0:
					ul.append(litxt)
			if len(ul) > 0:
				ullis.append(ul)
			uldom.extract()
		if len(ullis) > 0:
			wordsfam[str(len(wordsfam)) + " - Unordered Lists"] = ullis
		ollis = []
		oldoms = soup.select("ol") # 所有有序列表
		for oldom in oldoms:
			lidoms = oldom.select("li")
			ol = []
			for lidom in lidoms:
				litxt = ""
				txts = lidom.findAll(text = True)
				for txt in txts:
					if type(txt) != bs4.element.Comment and not(txt.isspace()):
						litxt += txt.strip()
				if len(litxt) > 0:
					ol.append(litxt)
			if len(ol) > 0:
				ollis.append(ol)
			oldom.extract()
		if len(ollis) > 0:
			wordsfam[str(len(wordsfam)) + " - Ordered Lists"] = ollis

	# 抽取出带表格格式的内容
	def extractTableAndList(self, soup):
		wordsfam = {}
		self.extractTable(wordsfam, soup)
		self.extractList(wordsfam, soup)
		wordsfam[str(len(wordsfam)) + " - Normal"] = self.extractText(soup) # 抽取不是表格的部分的文本
		return wordsfam

	# 移除指定内容(待筛选内容，移除条件)
	def rmvContent(self, html, rmv_term, res_type):
		soup = BeautifulSoup(html)
		for term in rmv_term:
			if rmv_term[term] == const.FILTER_TYPE_TXT: # 关键字删除
				self.extractRegContent(soup, re.compile(self.fmtRegToTxt(term)), res_type)
			elif rmv_term[term] == const.FILTER_TYPE_REG: # 正则表达式删除
				self.extractRegContent(soup, re.compile(term), res_type)
			elif rmv_term[term] == const.FILTER_TYPE_CSS:	# css选择器删除
				doms = soup.select(term)
				[dom.extract() for dom in doms]
		return soup.__str__()

	# 将正则表达式中的特殊字符转义成文本，防止正则注入(~.~)
	def fmtRegToTxt(self, reg):
		spchrs = ["\\", "$", "(", ")", "*", "+", ".", "[", "?", "^", "{", "|"] # 斜杠必需最先判断
		for spchr in spchrs:
			reg = reg.replace(spchr, "\\" + spchr)
		return reg

	# 将符合正则表达式的img元素抽出
	def extractRegImg(self, soup, reg):
		doms = soup.find_all("img")
		for dom in doms:
			imgfn = self.getFileName(dom["src"])
			if re.search(reg, imgfn.encode()) == None: # 除去图片名不符合正则的
				doms.remove(dom)
		return doms

	# 将符合正则表达式的dom元素抽出(此方法只对属性值或文本内容作中文处理)
	def extractRegDom(self, soup, reg):
		doms = []
		while True:
			content = soup.__str__()
			m = re.search(reg, content.encode())
			if m != None:
				strg = content[:m.span()[0]]
				strcp = strg
				lts = strg.rfind("<") # 找最近的开标签
				flag = False
				while True:
					if lts != -1:
						if strcp[lts + 1:lts + 2] != "/": # 不是闭标签
							break
						else:
							strcp = strcp[:lts]
							flag = True
						lts = strcp.rfind("<")
						if flag: # 有没匹配到开标签的闭标签
							strcp = strcp[:lts]
							lts = strcp.rfind("<")
							flag = False
					else:
						break
				if lts != -1:
					strg = strg[lts:]
					tagp = strg.find(" ") # 离开标签"<"最近的一个空格
					ltp = strg.find(">") # 离开标签"<"最近的一个">"
					if ltp == -1 and tagp >= ltp: # 标签元素不完整
						if tagp == -1: # 标签名符合正则
							for dom in soup.find_all(reg):
								dom.extract()
								doms.append(dom)
						else: # 正则是属性之一
							for dom in soup.find_all(strg[1:tagp]):
								if re.search(reg, dom.__str__().encode()) != None:
									dom.extract()
									doms.append(dom)
					else: # 标签元素完整
						if tagp != -1 and tagp < ltp: # 有属性的完整标签
							rss = soup.find_all(strg[1:tagp])
						else: # 无属性的完整标签
							rss = soup.find_all(strg[1:ltp])
						for dom in rss:
							if re.search(reg, dom.text.encode()) != None:
								dom.extract()
								doms.append(dom)
				else:
					break
			else:
				break
		return doms

	# 将符合正则表达式的文本抽出
	def extractRegTxt(self, soup, reg):
		doms = []
		txts = soup.find_all(text = True)
		for txt in txts:
			if re.search(reg, txt.encode()) != None: # 符合正则
				tag = soup.new_tag("p")
				tag.string = txt
				doms.append(tag)
		return doms

	# 将符合正则表达式的内容抽出
	def extractRegContent(self, soup, reg, res_type):
		if res_type == const.SPIDER_TYPE_IMG:
			return self.extractRegImg(soup, reg)
		elif res_type in [const.SPIDER_TYPE_HREF, const.SPIDER_TYPE_HTML]:
			return self.extractRegDom(soup, reg)
		elif res_type == const.SPIDER_TYPE_TXT:
			return self.extractRegTxt(soup, reg)

	# 选择指定内容(待筛选内容，选择条件)
	def slcContent(self, html, slc_term, res_type):
		soup = BeautifulSoup(html)
		if(len(slc_term) == 0):
			return soup.__str__()
		else:
			nsoup = BeautifulSoup("")
			for term in slc_term:
				if slc_term[term] == const.FILTER_TYPE_TXT: # 关键字选择
					doms = self.extractRegContent(soup, re.compile(self.fmtRegToTxt(term)), res_type)
					[nsoup.append(dom) for dom in doms]
				elif slc_term[term] == const.FILTER_TYPE_REG: # 正则表达式选择
					doms = self.extractRegContent(soup, re.compile(term), res_type)
					[nsoup.append(dom) for dom in doms]
				elif slc_term[term] == const.FILTER_TYPE_CSS: # css选择器选择
					doms = soup.select(term)
					[nsoup.append(dom) for dom in doms]
			return nsoup.__str__()

	# 根据路径生成本地目录树
	def autoGenDir(self, dirpath):
		if len(dirpath) > 0:
			if not(os.path.exists(dirpath)):
				os.makedirs(dirpath)
		return

	# 显示图片下载进度的回调函数（已下载的数据块数量，数据块大小，文件总大小）
	def saveImgProcess(self, blocknum, bs, size):
		per = blocknum * bs * 100 / size
		if per > 100:
			per = 100
		print('--- %3.2f%%' % per)

	# 下载图片地址列表的数据到本地
	def saveImgs(self, imgurls):
		filepath = glb.save_base[const.SPIDER_TYPE_IMG]
		self.autoGenDir(filepath)
		for imgurl in imgurls:
			print("downloading resource[" + imgurl + "]")
			try:
				urllib.urlretrieve(imgurl, filepath + self.getFileName(imgurl) + self.getFileFormat(imgurl), self.saveImgProcess)
			except httplib.InvalidURL:
				print("Invalid Url :%s" % imgurl)
		return

	# 保存网页内容到本地(文件名，读取到的网页内容)
	def saveHtml(self, pathfile, content):
		if len(content.strip()) > 0:
			path = glb.save_base[const.SPIDER_TYPE_HTML]
			if glb.ref_type == const.REF_TYPE_FILE:
				pass
			elif glb.ref_type in [const.REF_TYPE_HTTP, const.REF_TYPE_DIR]:
				path += self.getDirPath(pathfile)
			filename = self.getFileName(pathfile)
			if glb.export_type[const.SPIDER_TYPE_HTML] == const.EXPORT_TYPE_HTML:
				self.saveHtmlFile(path, self.addUrlSuffix(filename), content)
			elif glb.export_type[const.SPIDER_TYPE_HTML] == const.EXPORT_TYPE_TXT:
				self.saveTxtFile(path, filename, [content])
		return
		
	# 保存成网页文件到本地(文件名，读取到的网页内容)
	def saveHtmlFile(self, filepath, filename, content):
		self.autoGenDir(filepath)
		filepath = filepath + filename
		fo = open(filepath, "w")
		fo.write(content)
		fo.close()
		return

	# 保存关键词到本地(文件名，筛选出的文本内容)
	def saveWords(self, pathfile, words):
		if len(words) > 0:
			path = glb.save_base[const.SPIDER_TYPE_TXT]
			filename = self.getFileName(pathfile)
			if glb.export_type[const.SPIDER_TYPE_TXT] == const.EXPORT_TYPE_TXT:
				self.saveTxtFile(path, filename, words)
			elif glb.export_type[const.SPIDER_TYPE_TXT] == const.EXPORT_TYPE_EXCEL:
				self.saveExcelFile(path, filename, words)
		return

	# 保存文本文件(文件名，筛选出的文本内容)
	def saveTxtFile(self, filepath, filename, words):
		self.autoGenDir(filepath)
		filepath = filepath + filename + ".txt"
		self.saveLog("-"*10 + "\n保存到 : " + filepath)
		fo = open(filepath, "w")
		[fo.write(word + "\n") for word in words]
		fo.close()
		return

	# 保存excel文件(文件名，筛选出的文本内容)
	def saveExcelFile(self, filepath, filename, wordsfam):
		self.autoGenDir(filepath)
		filepath = filepath + filename + ".xls"
		wb = xlwt.Workbook()
		for key in wordsfam.keys(): # 每个子list为一张表
			ws = wb.add_sheet(str(key))
			tb = wordsfam[key]
			line = 0
			for tr in tb:
				if type(tr) == type([]):
					row = 0
					for td in tr:
						ws.write(line, row, td)
						row += 1
				else:
					ws.write(line, 0, tr)
				line += 1
		wb.save(filepath)
		return

	# 获取文件夹部分路径
	def getDirPath(self, path):
		dirpart = ""
		rs = re.search(r'.*/', path)
		if rs != None:
			dirpart = rs.group()
		return dirpart

	# 根据访问地址截取文本文件名
	def getFileName(self, url):
		st = url.rfind("/") + 1
		# sp = url.rfind(".")
		# if sp == -1:
			# url = url[st:]
		# else:
			# url = url[st:sp]
		url = url[st:]
		url = re.sub(r'[\\/:*?>"<>|]', "", url)
		return url

	# 根据访问地址截取后缀名
	def getFileFormat(self, url):
		st = url.rfind(".")
		if st == -1:
			return ""
		else:
			return url[st:]

	# 是否过滤掉指定格式的文件
	def filterFmt(self, src):
		suf = self.getFileFormat(src)[1:].lower()
		for img_fmt in glb.img_fmt:
			fmts = img_fmt.keys()
			if len(fmts) == 1:
				fmtlst = fmts[0].split(";")
				for fmt in fmtlst:
					if fmt.strip() == suf:
						return not(img_fmt[fmts[0]])
		return False # 没找到指定格式的不过滤

	# 根据地址模式组织正则式
	def getUrlPrefRegx(self, ref_type=None):
		regx = ""
		if ref_type == None:
			ref_type = glb.ref_type
		if ref_type in [const.REF_TYPE_FILE, const.REF_TYPE_DIR]:
			if glb.ref_ori == const.REF_ORI_LOCAL:
				regx = r"(^\w:[/|\\\\].*[/|\\\\])|(^(http)s{0,1}://(\w+\.)+\w+(:\d+){0,1}/)"
			elif glb.ref_ori == const.REF_ORI_PROJECT:
				regx = r"^\w:[/|\\\\](.*[/|\\\\])*"
		elif ref_type == const.REF_TYPE_HTTP:
			regx = r"^(http)s{0,1}://(\w+\.)+\w+(:\d+){0,1}/"
		return regx

	# 获取访问路径的协议及域名部分（不包含项目名）
	def getUrlPrefix(self, url):
		pref = re.search(self.getUrlPrefRegx(), glb.ref_url)
		if pref == None:
			if glb.ref_type == const.REF_TYPE_FILE:
				pref = "C:/"
			elif glb.ref_type == const.REF_TYPE_HTTP:
				pref = "http://127.0.0.1/"
			return pref
		else:
			return pref.group()

	# 根据访问地址截取项目部分路径（不包含协议和域名部分）
	def getProjectPart(self, url, ref_type=const.REF_TYPE_HTTP):
		pref = re.search(self.getUrlPrefRegx(ref_type), url)
		if pref != None:
			return url[len(pref.group()):]
		else:
			pref = re.search(self.getUrlPrefRegx(ref_type), url + "/")
			if pref != None:
				return ""
			else:
				return url

	# 为目标访问路径加上访问前缀
	def addUrlPrefix(self, aimurl):
		regx = self.getUrlPrefRegx()
		if re.search(regx, aimurl) != None:
			return aimurl
		else:
			if aimurl.find("/") == 0:
				return self.getUrlPrefix(glb.ref_url) + aimurl[1:]
			else:
				if glb.ref_type == const.REF_TYPE_FILE:
					aimurl = self.getProjectPart(aimurl)
				return self.getUrlPrefix(glb.ref_url) + aimurl

	# 为目标文件名加上默认后缀
	def addUrlSuffix(self, urlfilename):
		if re.search(r'.*\.html', urlfilename) != None:
			return urlfilename
		else:
			return urlfilename + ".html"
		# return urlfilename + ".html"

	# 读取本地文件
	def getContentFromLocalFile(self, filepath):
		fo = open(filepath, "r")
		content = fo.read()
		fo.close()
		return content

	# 读取文件夹下的文件列表
	def getFilesFromLocalDir(self, filepath):
		files = []
		for dirpath, diranames, filenames in os.walk(filepath):
			files.extend(filenames)
		return files

	# 记录日志文件 debug
	def saveLog(self, content):
		filepath = self.log_save_base
		self.autoGenDir(filepath)
		filepath = filepath + "log.txt"
		fo = open(filepath, "a")
		fo.write(content + "\n")
		fo.close()
		return

	# 每一页的爬取方法
	def scrapOnePage(self, threadName, now_ref_url, depth):
		try:
			ori_page = self.getHtml(threadName, now_ref_url) # 访问
			for res_type in glb.spider_type.keys(): # 资源抽取
				if glb.spider_type[res_type]:
					if res_type == const.SPIDER_TYPE_IMG:	# 图片
						page = self.filterHtml(ori_page, res_type, glb.dom_rmv[res_type], glb.dom_slc[res_type])
						imgurls = self.extractImgs(page, now_ref_url)
						self.saveImgs(imgurls)
					elif res_type == const.SPIDER_TYPE_HTML:	# 网页
						page = self.filterHtml(ori_page, res_type, glb.dom_rmv[res_type], glb.dom_slc[res_type])
						page = self.extractHtml(page)
						self.saveHtml(self.getProjectPart(now_ref_url), page)
					elif res_type == const.SPIDER_TYPE_TXT:	# 文本
						page = self.filterHtml(ori_page, res_type, glb.dom_rmv[res_type], glb.dom_slc[res_type])
						words = self.extractWords(page)
						self.saveWords(self.getProjectPart(now_ref_url), words)
			# 页面遍历链接
			if glb.ref_ori == const.REF_ORI_PROJECT and depth < glb.ref_deep:
				href_page = self.filterHtml(ori_page, const.SPIDER_TYPE_HREF, glb.dom_rmv[const.SPIDER_TYPE_HREF], glb.dom_slc[const.SPIDER_TYPE_HREF])
				rs = self.extractHref(href_page)
				self.saveLog("抽取出的地址 : \n")
				[self.saveLog(srs) for srs in rs]
				self.saveLog("-"*20)
				self.threadLock.acquire()
				self.rup.addRefUrls(now_ref_url, rs) # 相关链接列表放入链接池
				self.threadLock.release()
		except urllib2.HTTPError, e:
			self.saveLog("-"*10 + "\n" + str(e.code) + " 访问失败 : " + now_ref_url + "\n")
		except urllib2.URLError, e:
			self.saveLog("-"*10 + "\n" + e.reason.__str__() + "访问失败 : " + now_ref_url + "\n")
		# except IOError, e:
		# 	if glb.ref_type == const.REF_TYPE_FILE:
		# 		self.saveLog("-"*10 + "\n读取文件失败 : " + now_ref_url + "\n")
		# 	elif glb.ref_type == const.REF_TYPE_HTTP:
		# 		self.saveLog("-"*10 + "\n" + e.__str__() + "保存失败 : " + now_ref_url + "\n")
		# 	elif glb.ref_type == const.REF_TYPE_DIR:
		# 		self.saveLog("-"*10 + "\n读取文件失败 : " + now_ref_url + "\n")
		# except KeyError:
			# self.saveLog("可能是配置文件被人为修改致格式错误")

	def loopScrap(self, threadName=""):
		parent_url = glb.ref_url
		if glb.ref_ori == const.REF_ORI_LOCAL:
			now_ref_url = self.rup.nextUrlToVisit(parent_url, glb.ref_url)
		elif glb.ref_ori == const.REF_ORI_PROJECT:
			now_ref_url = glb.ref_url			
		depth = 0
		while True:
			if now_ref_url == None:
				self.closeHandles(threadName)
				self.saveLog("-"*10 + "\n[" + threadName + "] 线程结束")
				return
			else:
				self.saveLog("-"*10 + time.asctime(time.localtime(time.time())) + "\n[" + threadName + "] 新目标链接 :" + now_ref_url)
				# 标记链接已访问
				self.threadLock.acquire()
				flag = self.rup.urlHasRead(now_ref_url)
				if not flag:
					self.rup.markRead(now_ref_url)
				self.threadLock.release()
				if not flag:
					# 访问链接
					self.saveLog("-"*10 + "\n[" + threadName + "] " + time.asctime(time.localtime(time.time())) + "\n目标地址 :" + now_ref_url)
					self.scrapOnePage(threadName, now_ref_url, depth)
			# 找下一个链接
			if glb.ref_ori == const.REF_ORI_LOCAL:
				self.saveLog("-"*10 + "\n[" + threadName + "] 找下一个链接 : \n现链接 - " + now_ref_url)
			elif glb.ref_ori == const.REF_ORI_PROJECT:
				self.saveLog("-"*10 + "\n[" + threadName + "] 找下一个链接 : \n现父链接 - " + parent_url + "\n现链接 - " + now_ref_url)
			now_ref_url = self.rup.nextUrlToVisit(parent_url, now_ref_url) # 下一个链接
			if glb.ref_ori == const.REF_ORI_PROJECT:
				if type(now_ref_url) == type({}):
					parent_url = now_ref_url["par"]
					now_ref_url = now_ref_url["val"]
				depth = self.rup.getDepth()

	def start(self, init_flag):
		if init_flag:
			self.rup = RefUrlPool()
			self.threads = []
			self.handles = []
			# 多线程
			for i in range(0, glb.thread_num):
				th = threading.Thread(target=self.loopScrap, args=("Thread - " + str(i + 1),))
				self.threads.append(th)
				self.handles.append(None)
			if glb.ref_ori == const.REF_ORI_LOCAL:
				if glb.ref_type == const.REF_TYPE_FILE:
					# 本地url文件可读取远程url，将列表放入爬取池并初始化selenium
					self.rup.addRefUrls(glb.ref_url, self.getContentFromLocalFile(glb.ref_url).split("\n"))
					self.initOpener()
					self.autoLogin(glb.login_url, glb.login_form, glb.login_data)
					return False
				elif glb.ref_type == const.REF_TYPE_DIR:
					# 本地文件夹只读取本地文件，按顺序将目录下文件放入爬取池中
					self.rup.addRefUrls(glb.ref_url, self.getFilesFromLocalDir(glb.ref_url))
			elif glb.ref_ori == const.REF_ORI_PROJECT:
				if glb.ref_type == const.REF_TYPE_FILE:
					pass
				elif glb.ref_type == const.REF_TYPE_HTTP:
					# 远程项目，初始化selenium
					self.initOpener()
					self.autoLogin(glb.login_url, glb.login_form, glb.login_data) # 跳过登录
					return False
		else:
			if glb.ref_ori == const.REF_ORI_LOCAL:
				for th in self.threads:
					th.start()
			elif glb.ref_ori == const.REF_ORI_PROJECT:
				# 只有第一个线程才访问目标url，第一次抽取了地址才开后面的线程
				if len(self.threads) > 0:
					self.threads[0].start()
 				while True:
					if len(self.rup.allUrls) > 0 or glb.ref_deep == 0:
						break
				for i in range(1, glb.thread_num):
					self.threads[i].start()
			for th in self.threads:
				th.join()
			# 关闭浏览器
			if glb.mode == 1 or glb.mode == 2:
				if self.opener != None:
					self.opener.quit()
		return True;