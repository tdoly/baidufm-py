#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: baidufm.py
Author: tdoly
"""

import curses
from fm_cli import BaiduFmCli
from fm_api import BaiduFmAPI


def main():
    baidu_api = BaiduFmAPI('', '')
    baidu_cli = BaiduFmCli(baidu_api)
    curses.wrapper(baidu_cli.setup)


if __name__ == '__main__':
    main()
