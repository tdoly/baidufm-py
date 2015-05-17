#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time


def timestamp():
    return str(int(time.time() * 1000))


def sec_to_m(num):
    """
    >>> sec_to_m(66)
    '01:06'
    """
    template = "%02d:%02d"
    minute = 0
    second = 0
    if num < 59:
        second = num
    elif num > 60:
        minute = num / 60
        second = num % 60
    return template % (minute, second)


def minute_to_s(m):
    """
    >>> minute_to_s('[00:38.36]')
    38
    """
    time_str = m.strip('[|]')
    try:
        m_str, s_str = time_str.split(':')
        second = int(m_str) * 60 + int(float(s_str))
    except ValueError:
        second = 0
    return second


def save_captcha(img):
    img_path = '/tmp/baidu_captcha.jpg'
    with open(img_path, 'w') as f:
        f.write(img)
    return img_path