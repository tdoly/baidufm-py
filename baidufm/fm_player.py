#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File: fm_player.py
Author: tdoly
"""

import subprocess
import threading
import os
import logging
from logs import fm_log

logger = logging.getLogger('baidufm')


class Player(object):
    """ Media player class. Playing is handled by mplayer """

    def __init__(self, output_stream, event):
        self.process = None
        self.output_stream = output_stream
        self.event = event

    def __del__(self):
        if self.is_playing():
            self.close()

    def update_status(self):
        out_str = ('Title', 'Artist', 'Album', 'Year', 'Comment', 'Genre', 'Volume')
        try:
            self.event.clear()  # set threading.Event() False
            out = self.process.stdout
            while True:
                subsystem_out = out.readline().decode("utf-8")
                if subsystem_out == '':
                    break
                subsystem_out = subsystem_out.strip()
                fm_log(logger, "User input: %s", subsystem_out)
                for s in out_str:
                    if s in subsystem_out and ":" in subsystem_out:
                        show_msg = subsystem_out.split(":")[1]
                        self.output_stream.write(show_msg)
        except Exception as e:
            fm_log(logger, "Error in update_status thread. Msg: %s", str(e.args))
        self.event.set()  # set threading.Event() True

    def is_playing(self):
        return bool(self.process)

    def play(self, stream_url):
        """ use a multimedia player to play a stream """
        self.close()
        opts = self._build_start_opts(stream_url) or ''
        self.process = subprocess.Popen(
            opts,
            shell=False,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        fm_log(logger, "CREATE process PID: %d", self.process.pid)
        t = threading.Thread(target=self.update_status, args=())
        t.setDaemon(True)
        t.start()
        fm_log(logger, "Player started")

    def _send_command(self, command):
        """ send keystroke command to player """
        if self.process is None:
            return
        try:
            fm_log(logger, "Command: %s", command.strip())
            self.process.stdin.write(command.encode("utf-8"))
        except Exception as e:
            fm_log(logger, "Error when sending: %s, msg: %s", command, str(e.args))

    def close(self):
        """ exit (and kill mplayer instance) """

        # First close the subprocess
        self._stop()

        # Here is fallback solution and cleanup
        if self.process is not None:
            os.kill(self.process.pid, 9)
            fm_log(logger, "KILL process PID: %d", self.process.pid)
            self.process.wait()
        self.process = None

    def _build_start_opts(self, stream_url):
        pass

    def mute(self):
        pass

    def pause(self):
        pass

    def _stop(self):
        pass

    def volume_up(self):
        pass

    def volume_down(self):
        pass


class MpPlayer(Player):
    """Implementation of Player object for MPlayer"""

    PLAYER_CMD = "mplayer"

    def _build_start_opts(self, stream_url):
        """ Builds the options to pass to subprocess."""
        opts = [self.PLAYER_CMD, "-quiet", stream_url]
        return opts

    def mute(self):
        """ mute mplayer """
        self._send_command("m")

    def pause(self):
        """ pause streaming (if possible) """
        self._send_command("p")

    def _stop(self):
        """ exit (and kill mplayer instance) """
        self._send_command("q")

    def volume_up(self):
        """ increase mplayer's volume """
        self._send_command("*")

    def volume_down(self):
        """ decrease mplayer's volume """
        self._send_command("/")


class VlcPlayer(Player):
    """Implementation of Player for VLC"""

    PLAYER_CMD = "cvlc"

    muted = False

    def _build_start_opts(self, stream_url):
        """ Builds the options to pass to subprocess."""
        opts = [self.PLAYER_CMD, "-Irc", "--quiet", stream_url]
        return opts

    def mute(self):
        """ mute mplayer """

        if not self.muted:
            self._send_command("volume 0n")
            self.muted = True
        else:
            self._send_command("volume 256n")
            self.muted = False

    def pause(self):
        """ pause streaming (if possible) """
        self._send_command("stopn")

    def _stop(self):
        """ exit (and kill mplayer instance) """
        self._send_command("shutdownn")

    def volume_up(self):
        """ increase mplayer's volume """
        self._send_command("volupn")

    def volume_down(self):
        """ decrease mplayer's volume """
        self._send_command("voldownn")


def choose_player():
    """
    Probes the multimedia players which are available on the host
    system.
    """
    fm_log(logger, "Probing available multimedia players...")
    implemented_players = Player.__subclasses__()
    players = [player.PLAYER_CMD for player in implemented_players]
    fm_log(logger, "Implemented players: %s", ", ".join(players))

    for player in implemented_players:
        try:
            p = subprocess.Popen(
                [player.PLAYER_CMD, "--help"],
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            p.terminate()
            fm_log(logger, "%s supported.", str(player))
            return player
        except OSError:
            fm_log(logger, "%s not supported.", str(player))


def test():
    from fm_footer import Footer

    stream_url = 'http://yinyueshiting.baidufm.com/data2/music/35637510/52882018720064.m4a?xcode=95cdaaeca8069b7adfb67a194a8fb30314e495f9649b5904'
    log = Footer()
    player = choose_player()(log, threading.Event())
    player.play(stream_url)


if __name__ == "__main__":
    test()