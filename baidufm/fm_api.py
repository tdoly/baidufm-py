#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: fm_api.py
Author: tdoly
"""

import re
import json
import os
import pickle
import base64
import logging
import requests
import rsa
import consts
import fm_utils
from urllib import urlencode

logger = logging.getLogger("baidufm")
requests.packages.urllib3.disable_warnings()


ERROR_MSG = {
    '-1': '系统错误, 请稍后重试',
    '0': '登录成功',
    '1': '您输入的帐号格式不正确',
    '2': '您输入的帐号不存在',
    '3': '验证码不存在或已过期,请重新输入',
    '4': '您输入的帐号或密码有误',
    '5': '请在弹出的窗口操作,或重新登录',
    '6': '验证码输入错误',
    '16': '您的帐号因安全问题已被限制登录',
    '257': '需要验证码',
    '100005': '系统错误, 请稍后重试',
    '120016': '未知错误 120016',
    '120019': '近期登录次数过多, 请先通过 passport.baidu.com 解除锁定',
    '120021': '登录失败,请在弹出的窗口操作,或重新登录',
    '500010': '登录过于频繁,请24小时后再试',
    '401007': '您的手机号关联了其他帐号，请选择登录'
}


class APIError(Exception):
    pass


class BaiduFmAPI(object):
    def __init__(self, username, password):
        self.session = requests.session()
        self.username = username
        self.password = password
        self.cookies_file = 'cookies'
        self.token_file = 'token'
        self.user = {}
        self.login_data = None
        # 获取初始cookie
        self._request(consts.HOST)
        self.get_fm_user_info()
        self._initiate()

    def _initiate(self):
        if not os.path.exists(consts.HOST_PATH):
            os.makedirs(consts.HOST_PATH)
        if not self._load_cookies():
            self.user['token'] = self._get_token()
            if self.password and self.username:
                self.login()
            else:
                self._save_cookies()
        else:
            self.user['token'] = self._get_token()

    def _save_cookies(self):
        cookies_path = os.path.join(consts.HOST_PATH, self.cookies_file)
        with open(cookies_path, 'w') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.session.cookies), f)

    def _load_cookies(self):
        cookies_path = os.path.join(consts.HOST_PATH, self.cookies_file)
        if os.path.exists(cookies_path):
            with open(cookies_path, 'r') as cookies_file:
                load_cookies = pickle.load(cookies_file)
                cookies = requests.utils.cookiejar_from_dict(load_cookies)
                self.session.cookies = cookies
                if 'BDUSS' in load_cookies:
                    self.user['BDUSS'] = load_cookies['BDUSS']
                if 'BAIDUID' in load_cookies:
                    self.user['BAIDUID'] = load_cookies['BAIDUID']
                return True
        else:
            return False

    def _get_token(self):
        """
        获取token
        :return:
        """
        token = ''
        token_path = os.path.join(consts.HOST_PATH, self.token_file)
        if os.path.exists(token_path):
            with open(token_path, 'r') as token_file:
                token = token_file.readline()
        if not token:
            token_url = consts.URL_TOKEN % fm_utils.timestamp()
            content = self._request(token_url).content.replace('\'', '\"')
            token = json.loads(content)['data']['token']
            with open(token_path, 'w') as f:
                f.write(token)
            logger.info('get token: %s' % token)
        return token

    def _get_public_key(self):
        url = consts.URL_PUBLIC_KEY % (self.user['token'], fm_utils.timestamp())
        content = self._request(url).content
        data = json.loads(content.replace('\'', '"'))
        return data['pubkey'], data['key']

    def _get_captcha(self, code_string):
        if code_string:
            logger.info("requiring captcha")
            url = consts.URL_CAPTCHA % code_string
            jpeg = self._request(url).content
            captcha_path = fm_utils.save_captcha(jpeg)
        else:
            captcha_path = ""
        return captcha_path

    def _login_check(self):
        url_phoenix = consts.URL_PHOENIX
        url_login_history = consts.URL_LOGIN_HISTORY % (
            self.user['token'], fm_utils.timestamp())
        url_login_check = consts.URL_LOGIN_CHECK % (
            self.user['token'], fm_utils.timestamp(), self.username)
        self._request(url_phoenix)
        self._request(url_login_history)
        self._request(url_login_check)

    def login(self, username=None, password=None, verify_code=None):
        if username and password:
            self.username = username
            self.password = password
        if not self.login_data:
            self._login_check()
            pub_key, rsa_key = self._get_public_key()
            key = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
            pwd_rsa = base64.b64encode(rsa.encrypt(self.password, key))

            self.login_data = {
                'staticpage': 'http://fm.baidu.com/player/v2Jump.html',
                'charset': 'UTF-8',
                'token': self.user['token'],
                'tpl': 'box',
                'subpro': None,
                'apiver': 'v3',
                'tt': fm_utils.timestamp(),
                'codestring': None,
                'isPhone': None,
                'safeflg': '0',
                'u': 'http://fm.baidu.com',
                'quick_user': '0',
                'logintype': 'dialogLogin',
                'logLoginType': 'pc_loginDialog',
                'idc': None,
                'loginmerge': 'true',
                'splogin': 'rate',
                'username': self.username,
                'password': pwd_rsa,
                'verifycode': verify_code,
                'mem_pass': 'on',
                'rsakey': rsa_key,
                'crypttype': 12,
                'ppui_logintime': 14929,
                'callback': 'parent.bd__pcbs__irpbf3'
            }
        else:
            self.login_data['verifycode'] = verify_code
        result = self._request(consts.URL_LOGIN, 'post', self.login_data)
        if not result.ok:
            raise APIError('Logging failed.')

        content = result.content
        # 是否需要验证码
        if 'err_no=257' in content or 'err_no=6' in content:
            codestring = re.findall('codeString=(.*?)&', content)[0]
            logger.info('need captcha, codeString=%s', codestring)
            self.login_data['codestring'] = codestring
            captcha_path = self._get_captcha(codestring)
            return captcha_path

        self._check_account_exception(content)

        try:
            self.user['BDUSS'] = self.session.cookies['BDUSS']
        except Exception as e:
            logger.error("Get BDUSS: %s", str(e.args))
        logger.info('user %s Logged in BDUSS: %s' % (self.username, self.user['BDUSS']))
        self._save_cookies()

    def _check_account_exception(self, content):
        err_id = re.findall('err_no=([\d]+)', content)[0]
        if err_id == '0':
            return
        try:
            msg = ERROR_MSG[err_id]
        except Exception as e:
            logger.error("_check_account_exception %s", str(e.args))
            msg = 'unknown err_id=' + err_id
        raise APIError(msg)

    def _params_utf8(self, params):
        for k, v in params.items():
            if isinstance(v, unicode):
                params[k] = v.encode('utf-8')

    def _request(self, url, method=None, extra_params=None):
        params = dict()
        if extra_params:
            params.update(extra_params)

        headers = consts.HEADERS
        if 'fm.baidu.com' in url:
            headers['Host'] = "fm.baidu.com"
        elif 'passport.baidu.com' in url:
            headers['Host'] = "passport.baidu.com"
        else:
            headers['Host'] = ".baidu.com"

        self._params_utf8(params)
        if method and method.lower() == 'post':
            response = self.session.post(url, data=params, verify=True, headers=headers)
        else:
            if '?' in url:
                url = url + urlencode(params)
            else:
                url = url + '?' + urlencode(params)
            response = self.session.get(url, verify=False, headers=headers)
        return response

    def get_fm_user_info(self):
        """
        获取用户信息
        :return:
        """
        url = consts.FM_USER_INFO % fm_utils.timestamp()
        content = self._request(url)
        return content.json()

    def get_fm_user_counts(self):
        """
        获取用户听歌统计和hash_code
        :return:
        """
        hashcode = self.user.get('hashcode', '')
        params = dict()
        params['_'] = fm_utils.timestamp()
        params['tn'] = 'usercounts'
        params['hashcode'] = hashcode
        content = self._request(consts.FM_API, extra_params=params)
        return content.json()

    def get_fm_channel_list(self):
        """
        获取频道信息
        :return:
        """
        if 'hashcode' not in self.user:
            user_count = self.get_fm_user_counts()
            hash_code = user_count['hash_code']
            self.user['hashcode'] = hash_code
        else:
            hash_code = self.user['hashcode']

        params = dict()
        params['_'] = fm_utils.timestamp()
        params['tn'] = 'channellist'
        params['hashcode'] = hash_code
        content = self._request(consts.FM_API, extra_params=params)
        channels = [(c['channel_name'], c['channel_id']) for c in content.json()['channel_list']]
        return channels

    def get_fm_play_list(self, channel_id='public_yuzhong_huayu'):
        """
        根据频道id获取播放列表
        :param channel_id:
        :return:
        """
        params = dict()
        params['_'] = fm_utils.timestamp()
        params['tn'] = 'playlist'
        params['channel_id'] = channel_id
        params['hashcode'] = ''
        content = self._request(consts.FM_API, extra_params=params)
        song_ids = [str(play['id']) for play in content.json()['list']]
        return song_ids

    def get_song_info(self, song_ids):
        """
        根据歌曲IDs获取歌曲信息(歌名，演唱者，歌曲截图...)
        :param song_ids:
        """
        params = dict()
        params['songIds'] = ','.join(song_ids)
        content = self._request(consts.FM_SONG_INFO, 'post', params)
        return content.json()['data']['songList']

    def get_song_link(self, song_ids):
        params = dict()
        params['auto'] = 0
        params['bat'] = 0
        params['bp'] = 0
        params['bwt'] = -1
        params['dur'] = 211000
        params['flag'] = 0
        params['hq'] = 1
        params['pos'] = 0
        params['prerate'] = 128  # 音乐品质(128kbps)
        params['pt'] = 0
        params['rate'] = ''
        params['s2p'] = -1
        params['songIds'] = ','.join(song_ids)
        params['type'] = 'mp3'

        content = self._request(consts.FM_SONG_LINK, 'post', params)
        return content.json()['data']['songList']

    def get_next_play_list(self, channel_id, song_id):
        tt = str(fm_utils.timestamp())
        baidu_uid = self.user['BAIDUID']
        params = dict()
        params['_'] = tt
        url = 'ch_name=%s&item_id=%s&action_no=%d&userid=%d&baiduid=%s' % (channel_id, song_id, 2, 0, baidu_uid)
        api = consts.FM_NEXT_PLAY_LIST + url
        content = self._request(api, extra_params=params)
        song_ids = [str(play['songid']) for play in content.json()['list']]
        return song_ids

    def collect(self, song_id):
        params = dict()
        params['ids'] = song_id
        params['type'] = 'song'
        params['cloud_type'] = 0
        content = self._request(consts.FM_COLLECT, 'post', params)
        data = content.json()
        error_code = data['errorCode'] or 0
        if int(error_code) == 22000:
            return 1
        else:
            return 0

    def del_collect(self, song_id):
        params = dict()
        params['songIds'] = song_id
        params['type'] = 'song'
        content = self._request(consts.FM_DELETE_COLLECT, 'post', params)
        data = content.json()
        error_code = data['errorCode'] or 0
        if int(error_code) == 22000:
            return 1
        else:
            return 0

    def iscollect(self, song_id):
        """
        判断歌曲是否为加❤️，
        :rtype : object
        """
        params = dict()
        params['songIds'] = song_id
        params['type'] = 'type'
        content = self._request(consts.FM_IS_COLLECT, 'post', params)
        try:
            data = int(content.json())
        except:
            data = 0
        return data

    def dislike(self, song_id):
        """
        加入垃圾箱（不喜欢）
        :rtype : object
        """
        url = consts.FM_DISLIKE % (song_id, fm_utils.timestamp())
        content = self._request(url)
        data = content.json()
        error_code = data['errorCode'] or 0
        if int(error_code) == 22000:
            return 1
        else:
            return 0

    def get_lrc(self, lrc_url):
        lrc_dict = dict()
        if "http" not in lrc_url:
            lrc_url = "http://fm.baidu.com/" + lrc_url
        content = self._request(lrc_url).text
        try:
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue

                time_stamps = re.findall(r'\[[^\]]+\]', line)
                value = line
                times = ''.join(time_stamps)
                value = value.replace(times, '').strip()
                for time_s in time_stamps:
                    key = fm_utils.minute_to_s(time_s)
                    if key in lrc_dict:
                        lrc_dict[key] += ' ' + value
                    else:
                        lrc_dict[key] = value
        except Exception as e:
            logger.error("get_lrc: %s", str(e.args))

        return lrc_dict

    def is_login(self):
        """
        判断是否登录
        """
        user = self.get_fm_user_counts()
        username = user.get('user_name', '')
        return username