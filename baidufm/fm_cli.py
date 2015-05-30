#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: fm_cli.py
Author: tdoly
"""

import curses
import random
import locale
import logging
import threading
import fm_utils
import time
from logs import fm_log
from fm_footer import Footer
from fm_player import choose_player
from c_image import image_to_display

logger = logging.getLogger('baidufm')


# 显示中文不乱码
locale.setlocale(locale.LC_ALL, "")
code = locale.getpreferredencoding()


class BaiduFmCli(object):

    def __init__(self, api, auto_play=True):
        self.api = api
        self.channels = api.get_fm_channel_list()
        self.login_channel = [
            (u'私人频道', 'private'),
            (u'红星频道', 'lovesongs'),
        ]
        self.auto_play = auto_play
        self.pause_lock = False
        self.footer = Footer()
        self.event = threading.Event()
        self.monitor = None
        self.player = None
        self.stdscr = None

        self.head_win = None
        self.body_win = None
        self.footer_win = None
        self.login_win = None

        self.channel_id = None
        self.song_links = None
        self.song_name = None
        self.artist_name = None
        self.lrc_link = None
        self.lrc_dict = None
        self.song_time = 0
        self.execute_time = 0
        self.song_id = 0
        self.is_collect = 0

        self.playing = -1
        self.selection = 0
        self.start_pos = 0
        self.max_x = 0
        self.max_y = 0
        self.body_max_x = 0
        self.body_max_y = 0

    def setup(self, stdscr):
        fm_log(logger, 'init baidufm fm cli')
        self.stdscr = stdscr

        # init color
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_RED, curses.COLOR_BLACK)

        curses.start_color()
        for i in range(0, curses.COLORS):
            if i < 10:
                continue
            curses.init_pair(i + 1, curses.COLOR_BLACK, i)

        self.player = choose_player()(self.footer, self.event)

        self.stdscr.nodelay(0)
        self.setup_and_draw_screen()
        self.run()

    def setup_and_draw_screen(self):
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        self.head_win = curses.newwin(1, self.max_x, 0, 0)
        self.body_win = curses.newwin(self.max_y - 2, self.max_x, 1, 0)
        self.footer_win = curses.newwin(1, self.max_x, self.max_y - 1, 0)
        self.login_win = curses.newwin(self.max_y - 2, self.max_x, 1, 0)

        self.init_head()
        self.init_body()
        self.init_footer()

        self.footer.set_screen(self.footer_win)
        self.body_win.keypad(1)
        curses.doupdate()

    def init_head(self):
        title = "BaiduFM"
        try:
            user_counts = self.api.get_fm_user_counts()
            user_name = ' / ' + (user_counts['user_name'] or "Visitor")
            total_listen = "Listen: %s" % user_counts['counts']['total_listen']
            like_songs = "Like: %s" % user_counts['counts']['like_songs']
            dislike_songs = "Dislike: %s" % user_counts['counts']['dislike_songs']
            if user_counts['user_name'] and self.login_channel:
                self.login_channel.extend(self.channels)
                self.channels, self.login_channel = self.login_channel, None
        except Exception as e:
            fm_log(logger, "INIT HEAD: %s", str(e.args))
            return

        len_x = len(title)
        self.head_win.addstr(0, 0, title, curses.color_pair(1))
        self.head_win.addstr(0, len_x, user_name, curses.color_pair(2))
        len_x += len(user_name) + 2
        self.head_win.addstr(0, len_x, total_listen, curses.color_pair(3))
        len_x += len(total_listen) + 2
        self.head_win.addstr(0, len_x, like_songs, curses.color_pair(4))
        len_x += len(like_songs) + 2
        self.head_win.addstr(0, len_x, dislike_songs, curses.color_pair(5))
        self.head_win.noutrefresh()

    def init_body(self):
        self.body_max_y, self.body_max_x = self.body_win.getmaxyx()
        self.body_win.noutrefresh()
        self.refresh_body()

    def init_footer(self):
        self.footer_win.noutrefresh()

    def login(self):
        username = self.api.is_login()
        if username:
            if isinstance(username, unicode):
                username = username.encode('utf-8')
            self.footer.write('%s 已登录.' % username)
            return

        curses.echo()
        self.login_win.erase()
        self.login_win.addstr(0, 2, "Username: ", curses.color_pair(1))
        self.login_win.addstr(1, 2, " " * 43, curses.A_UNDERLINE)
        username = self.login_win.getstr(1, 2)
        password = ''
        if len(username) > 0:
            self.login_win.addstr(3, 2, "Password: ", curses.color_pair(1))
            self.login_win.addstr(4, 2, " " * 43, curses.A_UNDERLINE)
            password = self.login_win.getstr(4, 2)
            fm_log(logger, "USERNAME: %s, PWD: %s", username, '*****')
        if username and password:
            try:
                result = self.api.login(username, password, '')
                login_count = 0
                if result:
                    while True:
                        login_count += 1
                        try:
                            image_to_display(self.login_win, result, 8)
                        except:
                            pass
                        self.login_win.addstr(6, 2, "Captcha(%s): " % result, curses.color_pair(1))
                        self.login_win.addstr(7, 2, " " * 43, curses.A_UNDERLINE)
                        captcha = self.login_win.getstr(7, 2)
                        result = self.api.login(username, password, captcha)
                        if not result or login_count > 3:
                            break
                if not result:
                    if isinstance(username, unicode):
                        username = username.encode('utf-8')
                    self.footer.write('%s 登录成功.' % username)
            except Exception as e:
                fm_log(logger, "Login error. %s", str(e.args))

        self.refresh_body()

    def refresh_body(self):
        self.login_win.erase()
        self.body_win.erase()
        self.body_win.move(1, 1)
        max_display = self.body_max_y - 1
        for line_num in range(max_display - 1):
            i = line_num + self.start_pos
            if i < len(self.channels):
                self.__display_body_line(line_num, self.channels[i])
        self.body_win.refresh()

    def __display_body_line(self, line_num, channel):
        col = curses.color_pair(1)
        prefix = "  %s %s"
        channel_name = channel[0].encode('utf-8')
        if self.song_name and self.artist_name:
            song_info = " 《%s》- %s" % (self.song_name, self.artist_name)
        else:
            song_info = " "

        # 选择播放的渠道
        if line_num + self.start_pos == self.selection and self.selection == self.playing:
            col = curses.color_pair(2)
            channel_name = prefix % ('>', channel_name) + song_info
            if self.is_collect:
                self.body_win.addstr(line_num + 1, len(channel_name) + 2, "❤", curses.color_pair(10))
        # 选择的渠道
        elif line_num + self.start_pos == self.selection:
            col = curses.color_pair(2)
            channel_name = prefix % ('>', channel_name)
        # 播放的渠道
        elif line_num + self.start_pos == self.playing:
            col = curses.color_pair(4)
            channel_name = prefix % (' ', channel_name) + song_info
            if self.is_collect:
                self.body_win.addstr(line_num + 1, len(channel_name) + 2, "❤", curses.color_pair(10))
        else:
            channel_name = prefix % (' ', channel_name)

        self.body_win.addstr(line_num + 1, 1, channel_name, col)

    def run(self):

        if self.auto_play:
            num = random.randint(0, len(self.channels))
            self.set_channel(num)
            self.play_selection()
            self.refresh_body()

        while True:
            try:
                c = self.body_win.getch()
                ret = self.keypress(c)
                if ret == -1:
                    break
            except KeyboardInterrupt:
                break

    def set_channel(self, number):
        if number < 0:
            number = len(self.channels) - 1
        elif number >= len(self.channels):
            number = 0

        self.selection = number
        max_displayed_items = self.body_max_y - 2

        if self.selection - self.start_pos >= max_displayed_items:
            self.start_pos = self.selection - max_displayed_items + 1
        elif self.selection < self.start_pos:
            self.start_pos = self.selection

    def play_selection(self):
        self.playing = self.selection
        channel_name = self.channels[self.selection][0].strip()
        self.channel_id = self.channels[self.selection][1].strip()
        song_ids = self.api.get_fm_play_list(self.channel_id)
        self.footer.write('Playing ' + channel_name)
        self.song_links = self.api.get_song_link(song_ids)
        self.play()
        if not self.monitor:
            self.monitor = threading.Thread(target=self.monitor_thread, args=())
            self.monitor.setDaemon(True)
            self.monitor.start()

    def play(self):
        fm_log(logger, "now channel is: %s", self.channels[self.playing][0].encode('utf-8'))
        if not self.song_links:
            song_ids = self.api.get_next_play_list(self.channel_id, self.song_id)
            self.song_links = self.api.get_song_link(song_ids)
        try:
            link = self.song_links.pop()
        except:
            self.play_selection()
        try:
            fm_log(logger, "len(song_links): %d, link info: %s", len(self.song_links), link)
            song_link = link['linkinfo']['128']['songLink']
            self.song_time = link['linkinfo']['128']['time']
            self.song_id = link['songId']
            self.song_name = link['songName']
            self.artist_name = link['artistName']
            if isinstance(self.song_name, unicode):
                self.song_name = self.song_name.encode('utf-8')
            if isinstance(self.artist_name, unicode):
                self.artist_name = self.artist_name.encode('utf-8')
            self.lrc_link = link['lrcLink']
        except Exception as e:
            fm_log(logger, "play_selection not 128: %s", e.args)
            self.play()
            return

        try:
            if self.player.is_playing():
                self.player.close()
            self.player.play(song_link)
            self.lrc_dict = self.api.get_lrc(self.lrc_link)
            self.is_collect = self.api.iscollect(self.song_id)
            if self.execute_time == 0:
                s_time = threading.Thread(target=self.song_time_thread, args=())
                s_time.setDaemon(True)
                s_time.start()
            else:
                self.execute_time = 1

        except OSError:
            self.footer.write('Are you sure MPlayer is installed?')

    def monitor_thread(self):
        while True:
            self.event.wait()
            self.play()
            self.refresh_body()
            self.setup_and_draw_screen()

    def song_time_thread(self):
        while True:
            self.lrc_show()
            time.sleep(1)
            if self.pause_lock:
                continue

            total_time = fm_utils.sec_to_m(self.song_time)
            now_time = fm_utils.sec_to_m(self.execute_time)
            self.execute_time += 1
            time_str = now_time + ' / ' + total_time
            self.head_win.addstr(0, self.max_x - len(time_str) - 1, time_str, curses.color_pair(2))
            self.head_win.refresh()

    def lrc_show(self):
        if not self.lrc_dict:
            return
        seconds = self.lrc_dict.keys()
        seconds.sort()

        lrc_text = ''
        for second in seconds:
            if second > self.execute_time:
                break
            lrc_text = self.lrc_dict[second]
        self.footer.write(lrc_text)

    def keypress(self, char):
        page_change = 5

        if char == curses.KEY_EXIT or char == ord('q'):
            self.player.close()
            return -1

        if char in (curses.KEY_ENTER, ord('\n'), ord('\r')):
            self.play_selection()
            self.refresh_body()
            self.setup_and_draw_screen()
            return

        # 下一首歌
        if char == ord('n'):
            self.play()
            self.refresh_body()
            return

        if char == curses.KEY_DOWN or char == ord('j'):
            self.set_channel(self.selection + 1)
            self.refresh_body()
            return

        if char == curses.KEY_UP or char == ord('k'):
            self.set_channel(self.selection - 1)
            self.refresh_body()
            return

        if char == ord('+'):
            self.player.volume_up()
            self.refresh_body()
            return

        if char == ord('-'):
            self.player.volume_down()
            self.refresh_body()
            return

        if char == ord('p') or char == ord(' '):
            if self.pause_lock:
                self.pause_lock = False
            else:
                self.pause_lock = True
            self.player.pause()
            self.refresh_body()
            return

        if char == curses.KEY_PPAGE or char == ord('b'):
            self.set_channel(self.selection - page_change)
            self.refresh_body()
            return

        if char == curses.KEY_NPAGE or char == ord('f'):
            self.set_channel(self.selection + page_change)
            self.refresh_body()
            return

        if char == ord('G'):
            self.set_channel(len(self.channels)-1)
            self.refresh_body()
            return

        if char == ord('g'):
            self.set_channel(0)
            self.refresh_body()
            return

        if char == ord('m'):
            self.player.mute()
            self.refresh_body()
            return

        if char == ord('r'):
            self.set_channel(random.randint(0, len(self.channels)))
            self.play_selection()
            self.refresh_body()
            return

        # 收藏歌曲
        if char == ord('c'):
            # 如果已收藏，则取消收藏
            if self.is_collect:
                collect = self.api.del_collect(self.song_id)
                msg = collect and "删除收藏成功" or "删除收藏失败"
            else:
                collect = self.api.collect(self.song_id)
                msg = collect and "收藏成功" or "收藏失败"
            self.is_collect = self.api.iscollect(self.song_id)
            self.footer.write("%s %s" % (self.song_name, msg))
            self.refresh_body()
            self.setup_and_draw_screen()
            return

        # 加入垃圾箱
        if char == ord('d'):
            result = self.api.dislike(self.song_id)
            msg = result and "成功加入垃圾箱"or "加入垃圾箱失败"
            self.footer.write("%s %s" % (self.song_name, msg))
            self.play()
            self.refresh_body()
            self.setup_and_draw_screen()
            return

        # 登陆
        if char == ord('l'):
            self.login()
            self.refresh_body()
            self.setup_and_draw_screen()
            return

        if char == ord('#') or char == curses.KEY_RESIZE:
            self.refresh_body()
            self.setup_and_draw_screen()
            return