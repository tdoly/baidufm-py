#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: consts.py
Author: tdoly
"""

import os

DEBUG = False

# URL
HOST = 'http://fm.baidu.com'

FM_API = 'http://fm.baidu.com/dev/api/'

# login
URL_LOGIN = 'https://passport.baidu.com/v2/api/?login'
URL_TOKEN = 'https://passport.baidu.com/v2/api/?getapi&tpl=mn&apiver=v3&class=login&tt=%s' \
            '&logintype=dialogLogin'
URL_PHOENIX = 'http://passport.baidu.com/phoenix/account/osavailable?callback=baidufm.phoenix._setIconsStatus'
URL_LOGIN_HISTORY = 'https://passport.baidu.com/v2/api/?loginhistory&token=%s&tpl=box&apiver=v3&tt=%s'
URL_LOGIN_CHECK = 'https://passport.baidu.com/v2/api/?logincheck&' \
                  'token=%s&tpl=box&apiver=v3&tt=%s&username=%s&isphone=false'
URL_PUBLIC_KEY = 'https://passport.baidu.com/v2/getpublickey?token=%s&tpl=box&apiver=v3&tt=%s'
URL_CAPTCHA = 'https://passport.baidu.com/cgi-bin/genimage?%s'

# FM url(GET)
FM_USER_INFO = 'http://fm.baidu.com/data/user/info?_=%s'
FM_NEXT_PLAY_LIST = 'http://fm.baidu.com/data4/'

# POST
FM_SONG_INFO = 'http://fm.baidu.com/data/music/songinfo'
FM_SONG_LINK = 'http://fm.baidu.com/data/music/songlink'
FM_COLLECT = 'http://fm.baidu.com/data/user/collect'
FM_DELETE_COLLECT = 'http://fm.baidu.com/data/user/deletecollectsong'
FM_IS_COLLECT = 'http://fm.baidu.com/data/user/iscollect'

# GET
FM_DISLIKE = 'http://fm.baidu.com/data/user/dislike?item_id=%s&_=%s'

# FILE PATH
USER_HOME = os.path.expanduser("~")
HOST_PATH = os.path.join(USER_HOME, '.baidufm')

# request headers
HEADERS = {
    "Referer": "http://fm.baidu.com/",
    "Origin": "http://fm.baidu.com/",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:37.0) Gecko/20100101 Firefox/37.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-cn,en-us;q=0.7,en;q=0.3",
    "Connection": "keep-alive",
    "Host": "fm.baidu.com",
}