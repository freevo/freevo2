# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer.py - Application framework with mplayer has background process
# -----------------------------------------------------------------------------
# $Id$
#
# The intention of this file is to reuse code for mplayer control between the
# different modules video, audio and tv.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

__all__ = [ 'Application', 'Plugin' ]

# python imports
import re

# freevo imports
import config
import plugin
from event import *

# application imports
import childapp
import base

class Application(childapp.Application):
    """
    Basic application for controlling mplayer inside Freevo.
    """
    def __init__(self, type, has_video):
        """
        init the mplayer object
        """
        self.__elapsed = 0
        self.__stop_reason = ''
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
        self.name = 'mplayer'
        self.plugins = []
        self.plugin_key = 'mplayer_' + type
        childapp.Application.__init__(self, 'mplayer', type, has_video)


    def play(self, cmd):
        """
        Run the given mplayer command.
        """
        self.plugins = plugin.get(self.plugin_key)

        for p in self.plugins:
            cmd = p.play(cmd, self)

        cmd = self.correct_filter_chain(cmd)
        # reset some internal values
        self.__elapsed = 0
        self.__stop_reason = ''
        self.child_start(cmd, prio=config.MPLAYER_NICE, stop_cmd='quit\n')


    def correct_filter_chain(self, command):
        """
        Change a mplayer command to support more than one -vf
        parameter. This function will grep all -vf parameter from
        the command and add it at the end as one vf argument
        """
        ret = []
        vf = ''
        next_is_vf = False
        for arg in command:
            if next_is_vf:
                vf += ',%s' % arg
                next_is_vf = False
            elif (arg == '-vop' or arg == '-vf'):
                next_is_vf=True
            else:
                ret.append(arg)
        if vf:
            return ret + [ '-vf-add', vf[1:] ]
        return ret


    def stop(self):
        """
        Stop mplayer
        """
        for p in self.plugins:
            p.stop()
        self.plugins = []
        self.child_stop()


    def is_playing(self):
        """
        Return True if mplayer is playing right now.
        """
        return self.child_running()


    def send_command(self, cmd):
        """
        Send a command to mplayer.
        """
        return self.child_stdin(cmd)


    def elapsed(self, sec):
        """
        Callback for elapsed time changes.
        """
        pass


    def message(self, line):
        """
        A message line from mplayer.
        """
        pass


    def child_stdout(self, line):
        """
        A line from stdout of mplayer.
        """
        if line.find("A:") == 0:
            m = self.RE_TIME(line)
            if hasattr(m,'group') and self.__elapsed != int(m.group(1))+1:
                self.__elapsed = int(m.group(1))+1
                for p in self.plugins:
                    p.elapsed(sec)
                self.elapsed(self.__elapsed)

        # startup messages
        elif not self.__elapsed:
            for p in self.plugins:
                p.message(sec)
            self.message(line)

        return True


    def child_stderr(self, line):
        """
        A line from stdout of mplayer.
        """
        if line.startswith('Failed to open') and not self.__elapsed:
            self.__stop_reason = line
        else:
            for p in self.plugins:
                p.message(sec)
            self.message(line)
        return True


    def child_finished(self, exit_code):
        """
        Callback when the child is finished. Override this method to react
        when the child is finished.
        """
        childapp.Application.child_finished(self, exit_code)
        event = Event(PLAY_END, self.__stop_reason)
        event.set_handler(self.eventhandler)
        event.post()


    def eventhandler(self, event):
        """
        Eventhandler function.
        """
        if event == PLAY_END:
            self.stopped()
            return False

        if not self.has_child():
            return False

        for p in self.plugins:
            p.eventhandler(event)

        return False



class Plugin(plugin.Plugin):
    """
    Plugin for mplayer start and stop.
    """
    def __init__(self, type):
        """
        Init the plugin.
        """
        plugin.Plugin.__init__(self, 'mplayer_' + type)


    def play(self, command, application):
        """
        Callback that will be called when an item is played. The function
        gets the command line list and can change it. It has to return
        a new valid command line. The second parameter is the calling
        application.
        """
        return command


    def stop(self):
        """
        Callback when the playing has stopped.
        """
        pass


    def elapsed(self, sec):
        """
        Callback when the elapsed time changes.
        """
        pass


    def message(self, line):
        """
        Callback for normal mplayer stdout/stderr messages.
        """
        pass


    def eventhandler(self, event, application):
        """
        Eventhandler for events passed to the application.
        """
        return False
