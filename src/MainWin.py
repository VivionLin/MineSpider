# -*- coding: UTF-8 -*-
import sys
import Tkinter as tk
import ttk
import tkFileDialog
import tkMessageBox
import re
from ConstPara import *
from Config import *
from MySpider import MySpider

win = tk.Tk()
lf_href = None
ms = MySpider()

# 0. Global variable
var_login_type = tk.IntVar()
var_login_url = tk.StringVar()
var_login_form = tk.StringVar()
var_login_form_idx = tk.StringVar()
var_login_data = tk.StringVar()
var_ref_ori = tk.IntVar()
var_ref_type = tk.IntVar()
var_ref_url = tk.StringVar()
var_ref_deep = tk.StringVar()
var_ref_thread = tk.StringVar()
var_ref_load = tk.StringVar()
var_ref_break = tk.StringVar()
var_spider_types = {}
var_img_fmts = []
var_cb_img_fmt_custom = tk.IntVar()
var_export_types = {}
var_save_bases = {}
var_dom_items_img = []
var_dom_items_html = []
var_dom_items_txt = []
glb.login_form_num = [1]
var_dom_items_href = []

# 1. Layout parameter


# 2. Callback Function
# 2.1 show or hide the login settings
def loginSettingsShow():
	global lb_login_url, var_login_url, et_login_url
	global lb_login_form, var_login_form, et_login_form
	global lb_login_form_idx, var_login_form_idx, cb_login_form_idx
	global var_login_data
	if lb_login_url != None:
		lb_login_url.destroy()
		et_login_url.destroy()
	if lb_login_form != None:
		lb_login_form.destroy()
		et_login_form.destroy()
	if lb_login_form_idx != None:
		lb_login_form_idx.destroy()
		cb_login_form_idx.destroy()
	if var_login_type.get() == const.LOGIN_TYPE_AUTO or var_login_type.get() == const.LOGIN_TYPE_MANUAL:
		# login url
		lb_login_url = ttk.Label(lf_login, text=const.CHAR_LB_LOGIN_URL)
		lb_login_url.grid(row=1, column=0, sticky=tk.E)
		et_login_url = ttk.Entry(lf_login, textvariable=var_login_url, width=60, validate='all', validatecommand=(luCheck, '%P'))
		et_login_url.grid(row=1, column=1, columnspan=4, sticky=tk.W)
		if glb.mode != 2:
			# login form
			lb_login_form = ttk.Label(lf_login, text=const.CHAR_LB_LOGIN_FORM)
			lb_login_form.grid(row=1, column=5, sticky=tk.E)
			if var_login_type.get() == const.LOGIN_TYPE_AUTO:
				var_login_form.set("")
				et_login_form = ttk.Entry(lf_login, textvariable=var_login_form, width=60)
				et_login_form.grid(row=1, column=6, columnspan=5, sticky=tk.W)
				# login form index
				lb_login_form_idx = ttk.Label(lf_login, text=const.CHAR_LB_LOGIN_FORM_IDX)
				lb_login_form_idx.grid(row=1, column=11, sticky=tk.E)
				cb_login_form_idx = ttk.Combobox(lf_login, state="readonly", textvariable=var_login_form_idx, width=12)
				cb_login_form_idx.grid(row=1, column=12, sticky=tk.W)
				cb_login_form_idx["value"] = glb.login_form_num
			elif glb.mode == 0:
				var_login_data.set("")
				et_login_form = ttk.Entry(lf_login, textvariable=var_login_data, width=60)
				et_login_form.grid(row=1, column=6, columnspan=5, sticky=tk.W)

# 2.2 show or hide the 'other format' entry
def enterOtherFmt():
	global et_img_fmt_custom
	if var_cb_img_fmt_custom.get() == 1:
		val = tk.StringVar()
		if len(var_img_fmts) > len(const.CHAR_LS_IMG_FMTS):
			val.set(var_img_fmts[len(const.CHAR_LS_IMG_FMTS)].get())
			var_img_fmts[len(const.CHAR_LS_IMG_FMTS)] = val
		else:
			var_img_fmts.append(val)
		et_img_fmt_custom = ttk.Entry(lf_adv_img, textvariable=val, width=20)
		et_img_fmt_custom.grid(row=1, column=2, columnspan=3, sticky=tk.W)
	elif var_cb_img_fmt_custom.get() == 0:
		if et_img_fmt_custom != None:
			et_img_fmt_custom.destroy()

# 2.3 manage the grid of settings
def advSettings(flag=0):
	if flag != 0:
		global lf_href
		if lf_href != None and flag != 2:
			advSettings()
		else:
			advImgSettings(0)
			advHtmlSettings(0)
			advTxtSettings(0)
			cfgHrefDoms(1)
	else:
		count = 0
		cfgHrefDoms(0)
		if var_spider_types[const.SPIDER_TYPE_IMG].get() == 0:
			advImgSettings(0)
		else:
			advImgSettings(0)
			advImgSettings(1)
			count += 1
		if var_spider_types[const.SPIDER_TYPE_HTML].get() == 0:
			advHtmlSettings(0)
		else:
			advHtmlSettings(0)
			advHtmlSettings(1, count * 5)
			count += 1
		if var_spider_types[const.SPIDER_TYPE_TXT].get() == 0:
			advTxtSettings(0)
		else:
			advTxtSettings(0)
			advTxtSettings(1, count * 5)

def advImgSettings(flag=0):
	global lf_adv_img
	global var_img_fmts, var_cb_img_fmt_custom, var_save_bases, cb_img_fmt_custom, et_save_base_img
	if flag == 0:
		if lf_adv_img != None:
			lf_adv_img.destroy()
	else:
		lf_adv_img = ttk.LabelFrame(lf_scrapy, text=const.CHAR_LF_IMAGE)
		lf_adv_img.grid(row=8, column=0, padx=10, pady=10, columnspan=5, sticky=tk.N)
		# format filter
		ttk.Label(lf_adv_img, text=const.CHAR_LB_IMG_FMT).grid(row=0, column=0, sticky=tk.E)
		for idx in range(0, len(const.CHAR_LS_IMG_FMTS)):
			cb_img_fmt = tk.Checkbutton(lf_adv_img, text=const.CHAR_LS_IMG_FMTS[idx+1], variable=var_img_fmts[idx])
			cb_img_fmt.grid(row=0, column=idx + 1)
		cb_img_fmt_custom = tk.Checkbutton(lf_adv_img, text=const.CHAR_CB_IMG_CUSTOM, variable=var_cb_img_fmt_custom, command=enterOtherFmt)
		cb_img_fmt_custom.grid(row=1, column=1)
		# savepath
		ttk.Label(lf_adv_img, text=const.CHAR_LB_SAVEBASE).grid(row=2, column=0, sticky=tk.E)
		et_save_base_img = ttk.Entry(lf_adv_img, textvariable=var_save_bases[const.SPIDER_TYPE_IMG], width=36, state='readonly')
		et_save_base_img.grid(row=2, column=1, sticky=tk.W, columnspan=3)
		ttk.Button(lf_adv_img, text=const.CHAR_BT_PATH, command=lambda : chooseCfgSavePath(const.SPIDER_TYPE_IMG)).grid(row=2, column=4, sticky=tk.W)
		# content filter
		ttk.Label(lf_adv_img, text=const.CHAR_LB_DOM_ITEM).grid(row=3, column=0, sticky=tk.W, columnspan=4)
		ttk.Button(lf_adv_img, text=const.CHAR_BT_DOM_ADDITEM, width=4, command=lambda : addItem(const.SPIDER_TYPE_IMG)).grid(row=3, column=4, sticky=tk.E)
		showItem(const.SPIDER_TYPE_IMG)

def advHtmlSettings(flag=0, gcol=0):
	global lf_adv_html
	global var_export_types, var_save_bases, cb_export_type_html, et_save_base_html
	if flag == 0:
		if lf_adv_html != None:
			lf_adv_html.destroy()
	else:
		lf_adv_html = ttk.LabelFrame(lf_scrapy, text=const.CHAR_LF_HTML)
		lf_adv_html.grid(row=8, column=gcol, padx=10, pady=10, columnspan=5, sticky=tk.N)
		# export format
		ttk.Label(lf_adv_html, text=const.CHAR_LB_EXPORT_TYPE).grid(row=0, column=0, sticky=tk.E)
		cb_export_type_html = ttk.Combobox(lf_adv_html, textvariable=var_export_types[const.SPIDER_TYPE_HTML], state="readonly", width=12)
		cb_export_type_html["value"] = const.CHAR_LS_EXPORT_TYPES_HTML.values()
		cb_export_type_html.grid(row=0, column=1, sticky=tk.W)
		# savepath
		ttk.Label(lf_adv_html, text=const.CHAR_LB_SAVEBASE).grid(row=2, column=0, sticky=tk.E)
		et_save_base_html = ttk.Entry(lf_adv_html, textvariable=var_save_bases[const.SPIDER_TYPE_HTML], width=36, state='readonly')
		et_save_base_html.grid(row=2, column=1, sticky=tk.W, columnspan=3)
		ttk.Button(lf_adv_html, text=const.CHAR_BT_PATH, command=lambda : chooseCfgSavePath(const.SPIDER_TYPE_HTML)).grid(row=2, column=4, sticky=tk.W)
		# content filter
		ttk.Label(lf_adv_html, text=const.CHAR_LB_DOM_ITEM).grid(row=3, column=0, sticky=tk.W, columnspan=4)
		ttk.Button(lf_adv_html, text=const.CHAR_BT_DOM_ADDITEM, width=4, command=lambda : addItem(const.SPIDER_TYPE_HTML)).grid(row=3, column=4, sticky=tk.E)
		showItem(const.SPIDER_TYPE_HTML)

def advTxtSettings(flag=0, gcol=0):
	global lf_adv_txt
	global var_export_types, var_save_bases, cb_export_type_txt, et_save_base_txt
	if flag == 0:
		if lf_adv_txt != None:
			lf_adv_txt.destroy()
	else:
		lf_adv_txt = ttk.LabelFrame(lf_scrapy, text=const.CHAR_LF_TXT)
		lf_adv_txt.grid(row=8, column=gcol, padx=10, pady=10, columnspan=5, sticky=tk.N)
		# export format
		ttk.Label(lf_adv_txt, text=const.CHAR_LB_EXPORT_TYPE).grid(row=0, column=0, sticky=tk.E)
		cb_export_type_txt = ttk.Combobox(lf_adv_txt, textvariable=var_export_types[const.SPIDER_TYPE_TXT], state="readonly", width=12)
		cb_export_type_txt["value"] = const.CHAR_LS_EXPORT_TYPES_TXT.values()
		cb_export_type_txt.grid(row=0, column=1, sticky=tk.W)
		# savepath
		ttk.Label(lf_adv_txt, text=const.CHAR_LB_SAVEBASE).grid(row=2, column=0, sticky=tk.E)
		et_save_base_txt = ttk.Entry(lf_adv_txt, textvariable=var_save_bases[const.SPIDER_TYPE_TXT], width=36, state='readonly')
		et_save_base_txt.grid(row=2, column=1, sticky=tk.W, columnspan=3)
		ttk.Button(lf_adv_txt, text=const.CHAR_BT_PATH, command=lambda : chooseCfgSavePath(const.SPIDER_TYPE_TXT)).grid(row=2, column=4, sticky=tk.W)
		# content filter
		ttk.Label(lf_adv_txt, text=const.CHAR_LB_DOM_ITEM).grid(row=3, column=0, sticky=tk.W, columnspan=4)
		ttk.Button(lf_adv_txt, text=const.CHAR_BT_DOM_ADDITEM, width=4, command=lambda : addItem(const.SPIDER_TYPE_TXT)).grid(row=3, column=4, sticky=tk.E)
		showItem(const.SPIDER_TYPE_TXT)

def tabRefTypeSettings():
	global rb_ref_types
	ref_ori = var_ref_ori.get()
	for rb_ref_type in rb_ref_types:
		rb_ref_type.destroy()
	rb_ref_types = []
	if ref_ori == const.REF_ORI_LOCAL:
		rb_ref_types.append(tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_TYPES[ref_ori][0], value=const.REF_TYPE_FILE, variable=var_ref_type, command=tabRefUrlSettings))
		rb_ref_types[0].grid(row=2, column=1, sticky=tk.W)
		rb_ref_types.append(tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_TYPES[ref_ori][1], value=const.REF_TYPE_DIR, variable=var_ref_type, command=tabRefUrlSettings))
		rb_ref_types[1].grid(row=2, column=2, sticky=tk.W)
		sb_ref_deep["state"] = 'disabled'
		var_ref_deep.set(0)
	elif ref_ori == const.REF_ORI_PROJECT:
		rb_ref_types.append(tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_TYPES[ref_ori][0], value=const.REF_TYPE_FILE, variable=var_ref_type, command=tabRefUrlSettings))
		rb_ref_types[0].grid(row=2, column=1, sticky=tk.W)
		rb_ref_types.append(tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_TYPES[ref_ori][1], value=const.REF_TYPE_HTTP, variable=var_ref_type, command=tabRefUrlSettings))
		rb_ref_types[1].grid(row=2, column=2, sticky=tk.W)
		sb_ref_deep["state"] = 'readonly'
	tabRefUrlSettings()
	return

def tabRefUrlSettings():
	global bt_ref_url
	ref_type = var_ref_type.get()
	isweb = False
	if ref_type == const.REF_TYPE_FILE:
		if bt_ref_url != None:
			bt_ref_url.destroy()
		bt_ref_url = ttk.Button(lf_scrapy, text=const.CHAR_BT_PATH, command=lambda : chooseRefFile())
		bt_ref_url.grid(row=3, column=5, sticky=tk.W)
		if var_ref_ori.get() == const.REF_ORI_LOCAL:
			isweb = True
	elif ref_type == const.REF_TYPE_DIR:
		if bt_ref_url != None:
			bt_ref_url.destroy()
		bt_ref_url = ttk.Button(lf_scrapy, text=const.CHAR_BT_PATH, command=lambda : chooseRefDir())
		bt_ref_url.grid(row=3, column=5, sticky=tk.W)
	elif ref_type == const.REF_TYPE_HTTP:
		if bt_ref_url != None:
			bt_ref_url.destroy()
		isweb = True
	refurlCheck(et_ref_url.get())
	if not isweb:
		sb_ref_break["state"] = 'disabled'
		var_ref_break.set(0)
		sb_ref_load["state"] = 'disabled'
	else:
		sb_ref_break["state"] = 'readonly'
		sb_ref_load["state"] = 'readonly'

def addItem(flag, idx=None):
	if flag == const.SPIDER_TYPE_HREF:
		global lf_href, var_dom_items_href
		master = lf_href
		items = var_dom_items_href
		row_start = 1
	else:
		if flag == const.SPIDER_TYPE_IMG:
			global lf_adv_img, var_dom_items_img
			master = lf_adv_img
			items = var_dom_items_img
		elif flag == const.SPIDER_TYPE_HTML:
			global lf_adv_html, var_dom_items_html
			master = lf_adv_html
			items = var_dom_items_html
		elif flag == const.SPIDER_TYPE_TXT:
			global lf_adv_txt, var_dom_items_txt
			master = lf_adv_txt
			items = var_dom_items_txt
		row_start = 4
	len_items = len(items)
	if idx != None:
		len_items = idx
	else:
		items.append([tk.StringVar(), tk.StringVar(), tk.StringVar()])
	ttk.Combobox(master, width=4, textvariable=items[len_items][0], state="readonly", value=const.CHAR_LS_DOM_ITEM_TYPES).grid(row=len_items+row_start, column=0)
	ttk.Combobox(master, width=11, textvariable=items[len_items][1], state="readonly", value=const.CHAR_LS_DOM_ITEM_WAYS).grid(row=len_items+row_start, column=1)
	ttk.Entry(master, width=20, textvariable=items[len_items][2]).grid(row=len_items+row_start, column=2, columnspan=2)
	ttk.Button(master, width=4, text=const.CHAR_BT_DOM_RMVITEM, command=lambda : rmvItem(flag, len_items)).grid(row=len_items+row_start, column=4, sticky=tk.E)

def showItem(flag):
	if flag == const.SPIDER_TYPE_HREF:
		global lf_href
		master = lf_href
		items = var_dom_items_href
	else:
		if flag == const.SPIDER_TYPE_IMG:
			global lf_adv_img, var_dom_items_img
			master = lf_adv_img
			items = var_dom_items_img
		elif flag == const.SPIDER_TYPE_HTML:
			global lf_adv_html, var_dom_items_html
			master = lf_adv_html
			items = var_dom_items_html
		elif flag == const.SPIDER_TYPE_TXT:
			global lf_adv_txt, var_dom_items_txt
			master = lf_adv_txt
			items = var_dom_items_txt
	for idx in range(0, len(items)):
		addItem(flag, idx)

def rmvItem(flag, idx):
	if flag == const.SPIDER_TYPE_HREF:
		global var_dom_items_href, lf_href
		items = var_dom_items_href
		items.remove(items[idx])
		advSettings(2)
	else:
		if flag == const.SPIDER_TYPE_IMG:
			global var_dom_items_img
			items = var_dom_items_img
		elif flag == const.SPIDER_TYPE_HTML:
			global var_dom_items_html
			items = var_dom_items_html
		elif flag == const.SPIDER_TYPE_TXT:
			global var_dom_items_txt
			items = var_dom_items_txt
		items.remove(items[idx])
		advSettings()

def choosePath(params):
	path = tkFileDialog.askdirectory(**params)
	path = path + "/"
	return path

def openFile(params):
	pathfile = tkFileDialog.askopenfilename(**params)
	return pathfile

def saveFile(params):
	pathfile = tkFileDialog.asksaveasfilename(**params)
	return pathfile

def browsePath(params={}, browseway=None, lenlimit=0, var=None, callback=None):
	if browseway:
		path = browseway(params)
		if len(path) > lenlimit:
			if var:
				if isinstance(var, tk.Variable):
					var.set(path)
				else:
					glb.__setattr__(var, path)
			if callback:
				callback()

# Resorce - Save to
def chooseCfgSavePath(mode):
	browsePath({}, choosePath, 1, var_save_bases[mode])

# Config - Load
def openCfgFile():
	params = {"defaultextension":".conf", "filetypes":[("all files", ".conf")], "initialfile":"settings.conf"}
	browsePath(params, openFile, 0, "cfgfile", reloadWin)

# Browse - file
def chooseRefFile():
	if var_ref_ori.get() == const.REF_ORI_LOCAL:
		params = {"filetypes":[("Txt files", ".txt"), ("Other files", ".*")]}
	elif var_ref_ori.get() == const.REF_ORI_PROJECT:
		params = {"filetypes":[("HTML files", ".html"), ("JSP files", ".jsp"), ("Other files", ".*")]}
	browsePath(params, openFile, 0, var_ref_url)

# Browse - dir
def chooseRefDir():
	browsePath({}, choosePath, 1, var_ref_url)

# Config - Save As
def saveCfgFileAs():
	params = {"defaultextension":".conf", "filetypes":[("all files", ".conf")]}
	browsePath(params, saveFile, 0, "cfgfile", lambda : co.saveConfig())

def saveSettings():
	glb.login_type = var_login_type.get()
	glb.login_url = var_login_url.get()
	glb.login_form = var_login_form.get()
	glb.login_form_idx = int(var_login_form_idx.get())
	glb.login_data = var_login_data.get()
	glb.ref_ori = var_ref_ori.get()
	glb.ref_type = var_ref_type.get()
	glb.ref_url = var_ref_url.get()
	glb.ref_deep = int(var_ref_deep.get())
	glb.thread_num = int(var_ref_thread.get())
	glb.ref_load = int(var_ref_load.get())
	glb.ref_break = int(var_ref_break.get())
	# spider type
	glb.spider_type[const.SPIDER_TYPE_HREF] = 1
	for key in var_spider_types.keys():
		glb.spider_type[key] = var_spider_types[key].get()
	# img fmt
	for idx in range(0, len(const.CHAR_LS_IMG_FMTS) + 1):
		if idx < len(const.CHAR_LS_IMG_FMTS):
			glb.img_fmt[idx][glb.img_fmt[idx].keys()[0]] = var_img_fmts[idx].get()
		else:
			dic = {}
			dic[var_img_fmts[idx].get()] = var_cb_img_fmt_custom.get()
			if len(glb.img_fmt) > len(const.CHAR_LS_IMG_FMTS):
				glb.img_fmt[idx] = dic
			else:
				glb.img_fmt.append(dic)
	# export type
	for key in const.CHAR_LS_EXPORT_TYPES_HTML.keys():
		if const.CHAR_LS_EXPORT_TYPES_HTML[key] == var_export_types[const.SPIDER_TYPE_HTML].get():
			glb.export_type[const.SPIDER_TYPE_HTML] = key
	for key in const.CHAR_LS_EXPORT_TYPES_TXT.keys():
		if const.CHAR_LS_EXPORT_TYPES_TXT[key] == var_export_types[const.SPIDER_TYPE_TXT].get():
			glb.export_type[const.SPIDER_TYPE_TXT] = key
	# save base
	for key in var_save_bases.keys():
		val = var_save_bases[key].get()
		glb.save_base[key] = val
	# filter terms
	glb.dom_slc = {}
	glb.dom_rmv = {} # TODO
	parseDomItems(const.SPIDER_TYPE_IMG)
	parseDomItems(const.SPIDER_TYPE_HTML)
	parseDomItems(const.SPIDER_TYPE_TXT)
	parseDomItems(const.SPIDER_TYPE_HREF)
	co.saveConfig()

def parseDomItems(restype):
	global var_dom_items_img, var_dom_items_html, var_dom_items_txt, var_dom_items_href
	glb.dom_slc[restype] = {}
	glb.dom_rmv[restype] = {}
	if restype == const.SPIDER_TYPE_IMG:
		var_dom_items = var_dom_items_img
	elif restype == const.SPIDER_TYPE_HTML:
		var_dom_items = var_dom_items_html
	elif restype == const.SPIDER_TYPE_TXT:
		var_dom_items = var_dom_items_txt
	elif restype == const.SPIDER_TYPE_HREF:
		var_dom_items = var_dom_items_href
	for term in var_dom_items:
		key = term[2].get()
		val = const.CHAR_LS_DOM_ITEM_WAYS.index(term[1].get()) + 1
		if const.CHAR_LS_DOM_ITEM_TYPES.index(term[0].get()) == 0:
			glb.dom_slc[restype][key] = val
		else:
			glb.dom_rmv[restype][key] = val

def initParam(reload=False):
	var_login_type.set(glb.login_type)
	var_login_url.set(glb.login_url)
	var_ref_ori.set(glb.ref_ori)
	var_ref_type.set(glb.ref_type)
	var_ref_url.set(glb.ref_url)
	var_ref_deep.set(glb.ref_deep)
	var_ref_thread.set(glb.thread_num)
	var_ref_load.set(glb.ref_load)
	var_ref_break.set(glb.ref_break)
	for idx in range(0, len(const.CHAR_LS_SPIDER_TYPES)):
		if reload:
			val = var_spider_types[idx+1]
		else:
			val = tk.IntVar()
		val.set(glb.spider_type[idx+1])
		var_spider_types[idx+1] = val
	for idx in range(0, len(glb.img_fmt)):
		if idx < len(const.CHAR_LS_IMG_FMTS):
			if reload:
				val = var_img_fmts[idx]
			else:
				val = tk.IntVar()
				var_img_fmts.append(val)
			val.set(glb.img_fmt[idx][glb.img_fmt[idx].keys()[0]])
		else:
			if reload:
				val = var_img_fmts[idx]
			else:
				val = tk.StringVar()
				var_img_fmts.append(val)
			val.set(glb.img_fmt[idx].keys()[0])
			var_cb_img_fmt_custom.set(glb.img_fmt[idx][glb.img_fmt[idx].keys()[0]])
	for key in glb.save_base.keys():
		if reload:
			val = var_save_bases[key]
		else:
			val = tk.StringVar()
		if len(glb.save_base[key].strip()) == 0:
			val.set("C:/Users/Administrator/Desktop/")
		else:
			val.set(glb.save_base[key])
		var_save_bases[key] = val
	global var_dom_items_img, var_dom_items_html, var_dom_items_txt, var_dom_items_href
	var_dom_items_img = []
	var_dom_items_html = []
	var_dom_items_txt = []
	var_dom_items_href = []
	for key in glb.dom_slc.keys():
		val = glb.dom_slc[key]
		for term in val:
			v1 = tk.StringVar()
			v1.set(const.CHAR_LS_DOM_ITEM_TYPES[0])
			v2 = tk.StringVar()
			v2.set(const.CHAR_LS_DOM_ITEM_WAYS[val[term] - 1])
			v3 = tk.StringVar()
			v3.set(term)
			if key == const.SPIDER_TYPE_IMG:
				var_dom_items_img.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_HTML:
				var_dom_items_html.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_TXT:
				var_dom_items_txt.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_HREF:
				var_dom_items_href.append([v1, v2, v3])
	for key in glb.dom_rmv.keys():
		val = glb.dom_rmv[key]
		for term in val:
			v1 = tk.StringVar()
			v1.set(const.CHAR_LS_DOM_ITEM_TYPES[1])
			v2 = tk.StringVar()
			v2.set(const.CHAR_LS_DOM_ITEM_WAYS[val[term] - 1])
			v3 = tk.StringVar()
			v3.set(term)
			if key == const.SPIDER_TYPE_IMG:
				var_dom_items_img.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_HTML:
				var_dom_items_html.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_TXT:
				var_dom_items_txt.append([v1, v2, v3])
			elif key == const.SPIDER_TYPE_HREF:
				var_dom_items_href.append([v1, v2, v3])
	if not reload:
		var_export_types[const.SPIDER_TYPE_HTML] = tk.StringVar()
		var_export_types[const.SPIDER_TYPE_TXT] = tk.StringVar()
	var_export_types[const.SPIDER_TYPE_HTML].set(const.CHAR_LS_EXPORT_TYPES_HTML[glb.export_type[const.SPIDER_TYPE_HTML]])
	var_export_types[const.SPIDER_TYPE_TXT].set(const.CHAR_LS_EXPORT_TYPES_TXT[glb.export_type[const.SPIDER_TYPE_TXT]])
	glb.mode = int(glb.mode)
	glb.thread_num = int(glb.thread_num)

def reloadWin():
	co.loadConfig()
	initParam(True)
	loginSettingsShow()
	tabRefTypeSettings()
	advSettings()
	enterOtherFmt()

def start(flag):
	saveSettings()
	glb.login_form = []
	temp = var_login_form.get().split(",")
	for tmp in temp:
		glb.login_form.append(tmp.strip())
	glb.login_data = co.parseStrToDict(var_login_data.get(), str, str)
	info = ms.start(flag)
	bt_start['command'] = lambda : start(info)
	if flag:
		if glb.mode == 2 and glb.login_type != const.LOGIN_TYPE_NOLOGIN and ((glb.ref_ori == const.REF_ORI_LOCAL and glb.ref_type == const.REF_TYPE_FILE) or (glb.ref_type == const.REF_TYPE_HTTP)):
			bt_start['text'] = const.CHAR_BT_CONTINUE
		else:
			start(False)
	else:
		if info:
			bt_start['text'] = const.CHAR_BT_START
			tkMessageBox.showinfo("", "Finished!")
		else:
			print("wow"*10)

def canStart():
	bt_start['state'] = 'normal'

def cantStart():
	bt_start['state'] = 'disabled'

def lgurlCheck(val):
	return entryCheck(const.REF_TYPE_HTTP, val, et_login_url)

def refurlCheck(val):
	if var_ref_type.get() == const.REF_TYPE_FILE:
		return entryCheck(const.REF_TYPE_FILE, val, et_ref_url)
	elif var_ref_type.get() == const.REF_TYPE_HTTP:
		return entryCheck(const.REF_TYPE_HTTP, val, et_ref_url)
	elif var_ref_type.get() == const.REF_TYPE_DIR:
		return entryCheck(const.REF_TYPE_DIR, val, et_ref_url)

def entryCheck(mode, val, widget):
	regxes = {const.REF_TYPE_FILE : "^\w:[/|\\\\](.+[/|\\\\])*.[^/]+$", const.REF_TYPE_HTTP : "^(http)s{0,1}://.+", const.REF_TYPE_DIR : "^\w:[/|\\\\](.+[/|\\\\])*$"}
	if re.search(regxes[mode], val) != None:
		widget['style'] = 'Valid.TEntry'
		canStart()
	else:
		widget['style'] = 'Invalid.TEntry'
		cantStart()
	return True

def cfgHrefDoms(flag=0):
	global lf_href
	if lf_href != None:
		lf_href.destroy()
		lf_href = None
	if flag != 0:
		lf_href = ttk.LabelFrame(lf_scrapy, text=const.CHAR_LF_HREF)
		lf_href.grid(row=8, column=0, padx=10, pady=10, columnspan=5, sticky=tk.N)
		# content filter
		ttk.Label(lf_href, text=const.CHAR_LB_HREF_DOM_ITEM).grid(row=0, column=0, sticky=tk.W, columnspan=4)
		ttk.Button(lf_href, text=const.CHAR_BT_DOM_ADDITEM, width=4, command=lambda : addItem(const.SPIDER_TYPE_HREF)).grid(row=0, column=4, sticky=tk.E)
		showItem(const.SPIDER_TYPE_HREF)

# --------------------------------------Main------------------------------------
reload(sys)
sys.setdefaultencoding("utf8")

try:
	# 3. Windows
	win.title(const.CHAR_WIN_TITLE)

	# 3.0 Init parameter
	co = ConfigOperator()
	co.loadConfig()
	initParam(False)
	ttk.Style().configure('Valid.TEntry', foreground='black')
	ttk.Style().configure('Invalid.TEntry', foreground='red')

	# 3.0 Menu
	menubar = tk.Menu(win)
	# 3.0.1 Config menu
	cfgmenu = tk.Menu(menubar, tearoff=0)
	cfgmenu.add_command(label=const.CHAR_MN_CFG_LOAD, command=openCfgFile)
	cfgmenu.add_command(label=const.CHAR_MN_CFG_SAVE, command=saveSettings)
	cfgmenu.add_command(label=const.CHAR_MN_CFG_SAVEAS, command=saveCfgFileAs)
	menubar.add_cascade(label=const.CHAR_MN_CFG, menu=cfgmenu)
	# 3.0.2 Help
	# menubar.add_command(label=const.CHAR_MN_HELP)
	# 3.0.3 Exit
	menubar.add_command(label=const.CHAR_MN_EXIT, command=win.quit)
	win['menu'] = menubar

	# 3.2 Login Settings
	lf_login = ttk.LabelFrame(win, text=const.CHAR_LF_LOGIN)
	lf_login.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
	# 3.2.1 Login Type
	ttk.Label(lf_login, text=const.CHAR_LB_LOGIN_TYPE).grid(row=0, column=0, sticky=tk.E)
	tk.Radiobutton(lf_login, text=const.CHAR_LS_LOGIN_TYPES[0], value=const.LOGIN_TYPE_NOLOGIN, variable=var_login_type, command=loginSettingsShow).grid(row=0, column=1)
	if glb.mode == 0 or glb.mode == 1:
		tk.Radiobutton(lf_login, text=const.CHAR_LS_LOGIN_TYPES[1], value=const.LOGIN_TYPE_AUTO, variable=var_login_type, command=loginSettingsShow).grid(row=0, column=2)
	elif glb.mode == 2:
		tk.Radiobutton(lf_login, text=const.CHAR_LS_LOGIN_TYPES[3], value=const.LOGIN_TYPE_AUTO, variable=var_login_type, command=loginSettingsShow).grid(row=0, column=2)
	if glb.mode == 0:
		tk.Radiobutton(lf_login, text=const.CHAR_LS_LOGIN_TYPES[2], value=const.LOGIN_TYPE_MANUAL, variable=var_login_type, command=loginSettingsShow).grid(row=0, column=3)
	# 3.2.2 Login Url
	lb_login_url = None
	et_login_url = None
	luCheck = win.register(lgurlCheck)
	# 3.2.3 Login Form/Login Data
	lb_login_form = None
	et_login_form = None
	# 3.2.4 Login Form Index
	lb_login_form_idx = None
	cb_login_form_idx = None
	var_login_form_idx.set(1)

	# 3.3 Scrapy Setttings
	lf_scrapy = ttk.LabelFrame(win, text=const.CHAR_LF_SCRAPY)
	lf_scrapy.grid(row=1, column=0, padx=10, pady=10)
	# 3.3.0 Start
	bt_start = tk.Button(lf_scrapy, text=const.CHAR_BT_START, bg="grey", fg="white", width=18, command=lambda : start(True))
	bt_start.grid(row=0, column=0, columnspan=5, sticky=tk.W)
	# 3.3.1 Url Get From...
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_ORI).grid(row=1, column=0, sticky=tk.E)
	tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_ORIS[const.REF_ORI_LOCAL], value=const.REF_ORI_LOCAL, variable=var_ref_ori, command=tabRefTypeSettings).grid(row=1, column=1, sticky=tk.W)
	tk.Radiobutton(lf_scrapy, text=const.CHAR_LS_REF_ORIS[const.REF_ORI_PROJECT], value=const.REF_ORI_PROJECT, variable=var_ref_ori, command=tabRefTypeSettings).grid(row=1, column=2, sticky=tk.W)
	# 3.3.2 Url Type
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_TYPE).grid(row=2, column=0, sticky=tk.E)
	rb_ref_types = []
	# 3.3.3 Aim Url
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_URL).grid(row=3, column=0, sticky=tk.E)
	rfCheck = win.register(refurlCheck)
	et_ref_url = ttk.Entry(lf_scrapy, textvariable=var_ref_url, width=50, validate='all', validatecommand=(rfCheck, "%P"))
	et_ref_url.grid(row=3, column=1, columnspan=4, sticky=tk.W)
	bt_ref_url = None
	# 3.3.4 Scrapy Depth
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_DEEP).grid(row=4, column=0, sticky=tk.E)
	sb_ref_deep = tk.Spinbox(lf_scrapy, from_=0, to=5, textvariable=var_ref_deep, width=12)
	sb_ref_deep.grid(row=4, column=1, sticky=tk.W)
	# 3.3.5 Thread Num
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_THREAD).grid(row=4, column=2, sticky=tk.E)
	tk.Spinbox(lf_scrapy, from_=1, to=20, textvariable=var_ref_thread, width=12).grid(row=4, column=3, sticky=tk.W)
	# 3.3.6	Scrapy Loading Page Wait
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_LOAD).grid(row=5, column=0, sticky=tk.E)
	sb_ref_load = tk.Spinbox(lf_scrapy, from_=0, to=3600, textvariable=var_ref_load, width=12)
	sb_ref_load.grid(row=5, column=1, sticky=tk.W)
	# 3.3.7 Scrapy Interval
	ttk.Label(lf_scrapy, text=const.CHAR_LB_REF_BREAK).grid(row=5, column=2, sticky=tk.E)
	sb_ref_break = tk.Spinbox(lf_scrapy, from_=0, to=86400, textvariable=var_ref_break, width=12)
	sb_ref_break.grid(row=5, column=3, sticky=tk.W)
	# 3.3.8 Resource Type
	ttk.Label(lf_scrapy, text=const.CHAR_LB_SPIDER_TYPE).grid(row=6, column=0, sticky=tk.E)
	for idx in range(0, len(const.CHAR_LS_SPIDER_TYPES)):
		tk.Checkbutton(lf_scrapy, text=const.CHAR_LS_SPIDER_TYPES[idx], variable=var_spider_types[idx+1], command=advSettings).grid(row=6, column=idx + 1, sticky=tk.W)
	# 3.3.9 Filter href
	ttk.Label(lf_scrapy, text=const.CHAR_LB_HREF_DOMS).grid(row=7, column=0, sticky=tk.W)
	lb_href_dom_info = ttk.Label(lf_scrapy, text='')
	lb_href_dom_info.grid(row=7, column=1, sticky=tk.W)
	ttk.Button(lf_scrapy, text=const.CHAR_BT_HREF_DOMS, width=4, command=lambda : advSettings(1)).grid(row=7, column=3, sticky=tk.E)

	# 3.4 Resource Settings
	# 3.4.1 Image Settings
	lf_adv_img = None
	# 3.4.1.1 Format Filter
	cb_img_fmt_custom = None
	et_img_fmt_custom = None
	# 3.4.1.2 Savepath
	et_save_base_img = None
	# 3.4.1.3 Content Filter

	# 3.4.2 Source Code Settings
	lf_adv_html = None
	# 3.4.2.1 Export Format
	cb_export_type_html = None
	# 3.4.2.2 Savepath
	et_save_base_html = None
	# 3.4.2.3 Content Filter

	# 3.4.3 Text Settings
	lf_adv_txt = None
	# 3.4.3.1 Export Format
	cb_export_type_txt = None
	# 3.4.3.2 Savepath
	et_save_base_txt = None
	# 3.4.3.3 Content Filter

	loginSettingsShow()
	tabRefTypeSettings()
	advSettings()
	enterOtherFmt()

	win.mainloop()
except KeyError:
	print("可能是配置文件被人为修改致格式错误")