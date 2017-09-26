# -*- coding: UTF-8 -*-
import const

# 登录类型
const.LOGIN_TYPE_NOLOGIN = 0
const.LOGIN_TYPE_AUTO = 1
const.LOGIN_TYPE_MANUAL = 2

# url获取方式
const.REF_ORI_LOCAL = 0
const.REF_ORI_PROJECT = 1

# 爬取类型
const.REF_TYPE_FILE = 0
const.REF_TYPE_HTTP = 1
const.REF_TYPE_DIR = 2

# 爬取资源类型
const.SPIDER_TYPE_HREF = 0
const.SPIDER_TYPE_IMG = 1
const.SPIDER_TYPE_HTML = 2
const.SPIDER_TYPE_TXT = 3

# 筛选条件类型
const.FILTER_TYPE_TXT = 1
const.FILTER_TYPE_REG = 2
const.FILTER_TYPE_CSS = 3

# 导出文件类型
const.EXPORT_TYPE_HTML = 1
const.EXPORT_TYPE_TXT = 2
const.EXPORT_TYPE_EXCEL = 3

# 窗口文字
const.CHAR_WIN_TITLE = "MySPIDER"
const.CHAR_MN_CFG = "配置参数"
const.CHAR_MN_HELP = "帮助提示"
const.CHAR_MN_EXIT = "退出系统"
const.CHAR_MN_CFG_LOAD = "载入"
const.CHAR_MN_CFG_SAVE = "保存"
const.CHAR_MN_CFG_SAVEAS = "另存为"
const.CHAR_LF_LOGIN = "登录设置"
const.CHAR_LB_LOGIN_TYPE = "登录模式 : "
const.CHAR_LS_LOGIN_TYPES = ["无登录", "智能识别表单", "填写POST数据", "有登录"]
const.CHAR_LB_LOGIN_URL = "登录网址 : "
const.CHAR_LB_LOGIN_FORM = "登录信息 : "
const.CHAR_LB_LOGIN_FORM_IDX = "表单序号 : "
const.CHAR_LF_SCRAPY = "爬行设置"
const.CHAR_LB_REF_ORI = "地址获取方式 : "
const.CHAR_LS_REF_ORIS = ["本地文件(夹)指定", "项目结构指定"]
const.CHAR_LB_REF_TYPE = "地址模式 : "
const.CHAR_LS_REF_TYPES = [["本地文件", "本地文件夹"], ["本地文件", "网址(http/https)"]]
const.CHAR_LB_REF_URL = "目标地址 : "
const.CHAR_BT_START = "开始爬取"
const.CHAR_BT_CONTINUE = "继续爬取"
const.CHAR_LB_REF_DEEP = "爬取深度 : "
const.CHAR_LB_REF_THREAD = "并发爬取 : "
const.CHAR_LB_REF_LOAD = "页面加载等待 : "
const.CHAR_LB_REF_BREAK = "爬取间隔 : "
const.CHAR_LB_SPIDER_TYPE = "目标资源 : "
const.CHAR_LS_SPIDER_TYPES = ["图片", "源码", "文本"]
const.CHAR_LF_IMAGE = "图片设置"
const.CHAR_LB_IMG_FMT = "图片格式 : "
const.CHAR_LS_IMG_FMTS = {1:"bmp", 2:"gif", 3:"jpg", 4:"png"}
const.CHAR_CB_IMG_CUSTOM = "其它"
const.CHAR_LB_SAVEBASE = "保存位置 : "
const.CHAR_BT_PATH = "浏览"
const.CHAR_LB_DOM_ITEM = "内容筛选条件 : "
const.CHAR_LB_HREF_DOM_ITEM = "链接内容筛选条件 : "
const.CHAR_LB_HREF_DOMS = "目标链接内容 : "
const.CHAR_BT_HREF_DOMS = "配置"
const.CHAR_BT_DOM_ADDITEM = "+"
const.CHAR_BT_DOM_RMVITEM = "-"
const.CHAR_LF_HTML = "源码设置"
const.CHAR_LB_EXPORT_TYPE = "保存格式 : "
const.CHAR_LS_EXPORT_TYPES_HTML = {const.EXPORT_TYPE_HTML:"HTML", const.EXPORT_TYPE_TXT:"TXT"}
const.CHAR_LF_TXT = "文本设置"
const.CHAR_LS_EXPORT_TYPES_TXT = {const.EXPORT_TYPE_TXT:"TXT", const.EXPORT_TYPE_EXCEL:"EXCEL"}
const.CHAR_LS_DOM_ITEM_TYPES = ["选择", "过滤"]
const.CHAR_LS_DOM_ITEM_WAYS = ["包含文本", "正则表达式", "CSS选择器"]
const.CHAR_LF_HREF = "链接设置"