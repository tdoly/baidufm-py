#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: fm_footer.py
Author: tdoly
"""


class Footer(object):
    """ Footer class that outputs text to a curses screen """

    msg = None
    curses_screen = None

    def __init__(self):
        self.width = None

    def set_screen(self, curses_screen):
        self.curses_screen = curses_screen
        self.width = curses_screen.getmaxyx()[1] - 5

        if self.msg:
            self.write(self.msg)

    def write(self, msg):
        self.msg = msg.strip().replace("\r", "").replace("\n", "")

        content = self.msg
        if isinstance(self.msg, unicode):
            content = self.msg.encode('utf-8')
        content = content[0: self.width]

        if self.curses_screen:
            self.curses_screen.erase()
            self.curses_screen.addstr(0, (self.width-len(content))/2, content)
            self.curses_screen.refresh()

    def readline(self):
        pass
