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
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
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

class Application(childapp.Application):
    """
    Basic application for controlling mplayer inside Freevo.
    """
    def __init__(self, type, has_video):
        """
        init the mplayer object
        """
        childapp.Application.__init__(self, 'mplayer', type, has_video)
        self.name = 'mplayer'
        self.__proc = None
        self.has_video = has_video
        self.plugins = []
        self.plugin_key = 'mplayer_' + type


    def play(self, cmd):
        """
        Run the given mplayer command.
        """
        self.plugins = plugin.get(self.plugin_key)

        for p in self.plugins:
            cmd = p.play(cmd, self)

        # FIXME: do we really need to reset the mixer all the time?
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        cmd = self.correct_filter_chain(cmd)
        self.__proc = Process(cmd, self, self.has_video)


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
        if not self.__proc:
            return
        # proc will send a PLAY_END when it's done. At this point we
        # will call childapp.Application.stop(self)
        self.__proc.stop('quit\n')
        self.__proc = None


    def is_playing(self):
        """
        Return True if mplayer is playing right now.
        """
        return self.__proc and self.__proc.is_alive()


    def has_process(self):
        """
        Return True if the application is still connected to a process
        """
        return self.__proc


    def send_command(self, cmd):
        """
        Send a command to mplayer.
        """
        if self.__proc:
            self.__proc.write(cmd)


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


    def eventhandler(self, event):
        """
        Eventhandler function.
        """
        if event == PLAY_END:
            childapp.Application.stop(self)
            return False

        if not self.has_process():
            return False

        for p in self.plugins:
            if p.eventhandler(event):
                return True

        return False



class Plugin(plugin.Plugin):
    """
    Plugin for mplayer start and stop.
    """
    def __init__(self, type):
        """
        Init the plugin.
        """
        plugin.Plugin.__init__(self)
        self.plugin_name = 'mplayer_' + type


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


class Process(childapp.Process):
    """
    Internal childapp instance for the mplayer process.
    """
    def __init__(self, cmd, handler, has_display):
        self.elapsed = 0
        self.stop_reason = ''
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
        childapp.Process.__init__(self, cmd, handler, config.MPLAYER_NICE,
                                  has_display)


    def stop_event(self):
        """
        Return the stop event send through the eventhandler
        """
        return Event(PLAY_END, self.stop_reason,
                     handler=self.handler.eventhandler)


    def stdout_cb(self, line):
        """
        Handle mplayer stdout lines.
        """
        if line.find("A:") == 0:
            m = self.RE_TIME(line)
            if hasattr(m,'group') and self.elapsed != int(m.group(1))+1:
                self.elapsed = int(m.group(1))+1
                for p in self.handler.plugins:
                    p.elapsed(sec)
                self.handler.elapsed(self.elapsed)

        # startup messages
        elif not self.elapsed:
            for p in self.handler.plugins:
                p.message(sec)
            self.handler.message(line)


    def stderr_cb(self, line):
        """
        Handle mplayer stderr lines.
        """
        if line.startswith('Failed to open') and not self.elapsed:
            self.stop_reason = line
        else:
            for p in self.handler.plugins:
                p.message(sec)
            self.handler.message(line)
