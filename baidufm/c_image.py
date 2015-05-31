#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: c_image.py
Author: tdoly
"""


import os
import curses
import ctypes
import consts
from PIL import Image
from os.path import join, dirname, getmtime, exists, expanduser


def call_c():
    """
    Call the C program for converting RGB to Ansi colors
    """
    if not exists(consts.HOST_PATH):
        os.mkdir(consts.HOST_PATH)
    library = expanduser(consts.HOST_PATH + '/image.so')
    sauce = join(dirname(__file__), 'image.c')
    if not exists(library) or getmtime(sauce) > getmtime(library):
        build = "cc -fPIC -shared -o %s %s" % (library, sauce)
        os.system(build + " >/dev/null 2>&1")
    image_c = ctypes.cdll.LoadLibrary(library)
    image_c.init()
    return image_c.rgb_to_ansi

rgb2short = call_c()


def pixel_print(std_scr, row, start, ansicolor):
    """
    Print a pixel with given Ansi color
    """
    std_scr.addstr(row, start, ' ', curses.color_pair(ansicolor))


def image_to_display(std_scr, path, login_win_row=0, start=None, length=None):
    """
    Display an image
    """
    login_max_y, login_max_x = std_scr.getmaxyx()
    rows, columns = os.popen('stty size', 'r').read().split()
    if not start:
        start = 2
    if not length:
        length = int(columns) - 2 * start
    i = Image.open(path)
    i = i.convert('RGBA')
    w, h = i.size
    i.load()
    width = min(w, length, login_max_x-1)
    height = int(float(h) * (float(width) / float(w)))
    height //= 2
    i = i.resize((width, height), Image.ANTIALIAS)
    height = min(height, 90, login_max_y-1)
    for y in xrange(height):
        for x in xrange(width):
            p = i.getpixel((x, y))
            r, g, b = p[:3]
            pixel_print(std_scr, login_win_row+y, start+x, rgb2short(r, g, b))