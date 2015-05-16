#!/usr/bin/env python
# -*- coding: utf-8 -*-


import curses
from baidu.fm_cli import BaiduFmCli
from baidu.fm_api import BaiduFMAPI


def main():
    username = ''
    password = ''
    baidu_api = BaiduFMAPI(username, password)
    baidu_cli = BaiduFmCli(baidu_api)
    curses.wrapper(baidu_cli.setup)


if __name__ == '__main__':
    main()
