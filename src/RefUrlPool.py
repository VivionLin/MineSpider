# -*- coding: UTF-8 -*-

class RefUrlPool:
	'访问链接池'
	class NoUrlError(LookupError):pass
	class NoRefUrlError(LookupError):pass

	def __init__(self): # 实例参数初始化控制,TODO
		self.allUrls = {} # 存储所有链接
		self.finReadUrls = [] # 存储已访问过的链接
		self.depth = 0 # 访问深度

	# 添加相关链接列表
	def addRefUrls(self, parent_url, ref_urls):
		self.allUrls[parent_url] = ref_urls

	# 根据key和列表序号查找相关链接
	def getRefUrl(self, parent_url, ref_url_idx):
		try:
			ref_urls = self.allUrls[parent_url]
		except KeyError:
			raise self.NoRefUrlError, "Can't find url with the given infomation:%s %d" % (parent_url, ref_url_idx)
		if ref_urls != None:
			if len(ref_urls) >= ref_url_idx + 1:
				return ref_urls[ref_url_idx]
			elif len(ref_urls) == 0:
				return None
			else:
				raise self.NoRefUrlError, "Can't find url with the given infomation:%s %d" % (parent_url, ref_url_idx)
		else:
			raise self.NoUrlError, "Can't find url:%s" % parent_url

	# 下一个兄弟链接
	def siblingUrl(self, parent_url, ref_url):
		if parent_url == None:
			ridx = self.finReadUrls.index(ref_url) # 在已访问列表找此链接的索引位置
			while True:
				ridx -= 1 # 在已访问列表往前找
				p_candiate = self.finReadUrls[ridx] # 父链接候选
				p_candiate_refs = self.allUrls[p_candiate] # 父链接候选的子相关链接列表
				if ref_url in p_candiate_refs:
					return self.siblingUrl(p_candiate, ref_url) # 找到父链接，返回兄弟链接
				else:
					continue # 继续往前找父链接
		else:
			ref_urls = self.allUrls[parent_url]
			idx = ref_urls.index(ref_url)
			if len(ref_urls) > idx + 1:
				return self.getRefUrl(parent_url, idx + 1)
			else:
				return None # 无下个兄弟

	# 链接是否已被访问
	def urlHasRead(self, url):
		if url in self.finReadUrls:
			return True
		else:
			return False

	# 将链接放入已访问列表
	def markRead(self, url):
		self.finReadUrls.append(url)

	# 访问深度
	def getDepth(self):
		return self.depth

	# 下一个要访问的链接
	def nextUrlToVisit(self, parent_url, now_ref_url):
		return self.nextBFSUrl(parent_url, now_ref_url)

	# 广度优先遍历顺序的下一个链接
	def nextBFSUrl(self, parent_url, now_ref_url):
		aim_url = None
		try:
			if parent_url == now_ref_url: # 首次遍历，默认遍历第一个链接
				aim_url = self.getRefUrl(parent_url, 0)
				self.depth += 1
			else: # 非首次遍历，找下一个兄弟链接
				flag = True
				while flag:
					next_ref = self.siblingUrl(parent_url, now_ref_url)
					if next_ref != None: # 有下个兄弟链接
						if self.urlHasRead(next_ref):
							now_ref_url = next_ref # 被访问过，继续找下一个
						else:
							aim_url = next_ref # 未被访问过，跳出循环
							flag = False
					else: # 无下个兄弟链接，本页链接全部遍历完，遍历页变成本页的链接页
						pidx = 0
						ridx = 0
						self.depth += 1 # BFS
						while flag:
							nparent_url = self.getRefUrl(parent_url, pidx) # 索引过长异常处理
							try:
								nref_url = self.getRefUrl(nparent_url, ridx) # 获取新页的链接
								if nref_url == None: # 新链接页无链接，找下一链接页
									pidx += 1
									ridx = 0
								else:
									if not(self.urlHasRead(nref_url)): # 找到链接且未被访问过
										aim_url = {}
										aim_url["val"] = nref_url
										aim_url["par"] = nparent_url
										flag = False
									else: # 被访问过，继续新链接页的下一个链接
										ridx += 1
							except RefUrlPool.NoRefUrlError: # 新链接页已没有链接，找下一链接页
								pidx += 1
								ridx = 0
		except RefUrlPool.NoRefUrlError, RefUrlPool.NoUrlError:
			pass
		return aim_url