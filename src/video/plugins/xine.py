# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xine.py - the Freevo XINE module for video
# -----------------------------------------------------------------------------
# $Id$
#
# TODO: remove the time.sleep() code
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

# python imports
import time
import copy
import logging

# freevo imports
import config
import util
import plugin

from application import ChildApp
from event import *

# get logging object
log = logging.getLogger('video')


class PluginInterface(plugin.Plugin):
    """
    Xine plugin for the video player.
    """
    def __init__(self):
        # detect xine and it's version
        config.detect('xine')

        try:
            config.XINE_COMMAND
        except:
            self.reason = '\'XINE_COMMAND\' not defined'
            return

        if config.XINE_VERSION < '0.99.1' and \
               config.XINE_VERSION < '0.9.23':
            self.reason = "'xine' version too old"
            return

        if config.FBXINE_VERSION < '0.99.1' and \
               config.FBXINE_VERSION < '0.9.23':
            self.reason = "'fbxine' version too old"
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
        elif config.XINE_COMMAND.find('df_xine') >= 0:
            type = 'df'
        else:
            type = 'X'

        plugin.Plugin.__init__(self)

        # register xine as the object to play
        plugin.register(Xine(type), plugin.VIDEO_PLAYER, True)



class Xine(ChildApp):
    """
    the main class to control xine
    """
    def __init__(self, type):
        ChildApp.__init__(self, 'xine', 'video', True, False, True)
        self.name = 'xine'
        self.xine_type = type


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url.startswith('dvd://'):
            return 2
        if item.url == 'vcd://':
            return 2
        if item.mimetype in config.VIDEO_XINE_SUFFIX:
            return 2
        if item.network_play:
            return 1
        return 0


    def play(self, options, item):
        """
        play a dvd with xine
        """
        # store item
        self.item = item

        # set event map
        if config.EVENTS.has_key(item.mode):
            self.set_eventmap(item.mode)
        else:
            self.set_eventmap('video')

        # create command
        command = config.XINE_COMMAND.split(' ') + \
                  [ '--stdctl', '-V', config.XINE_VO_DEV, '-A',
                    config.XINE_AO_DEV ] + config.XINE_ARGS_DEF.split(' ')

        if item['deinterlace']:
            command.append('-D')

        if config.XINE_COMMAND.startswith(config.CONF.xine) and \
               config.XINE_USE_LIRC:
            command.append('--no-lirc')

        if config.XINE_COMMAND.startswith(config.CONF.fbxine) and \
               config.FBXINE_USE_LIRC:
            command.append('--no-lirc')

        self.max_audio        = 0
        self.current_audio    = -1
        self.max_subtitle     = 0
        self.current_subtitle = -1

        if item.mode == 'dvd':
            if item.info['tracks']:
                for track in item.info['tracks']:
                    self.max_audio = max(self.max_audio, len(track['audio']))
                    self.max_subtitle = max(self.max_subtitle,
                                            len(track['subtitles']))
            else:
                self.max_audio = len(item.info['audio'])
                self.max_subtitle = len(item.info['subtitles'])

        if item.mode == 'dvd' and hasattr(item, 'filename') and \
               item.filename and item.filename.endswith('.iso'):
            # dvd:///full/path/to/image.iso/
            command.append('dvd://%s/' % item.filename)

        # elif item.mode == 'dvd' and hasattr(??, 'devicename'):
        #     # dvd:///dev/dvd/2
        #     url = 'dvd://%s/%s' % (??.devicename, item.url[6:])
        #     command.append(url.strip('/'))

        elif item.mode == 'dvd': # no devicename? Probably an image on the HD
            command.append(item.url)

        # elif item.mode == 'vcd':
        #     # vcd:///dev/cdrom -- NO track support (?)
        #     command.append('vcd://%s' % ??.devicename)

        elif item.mimetype == 'cue':
            command.append('vcd://%s' % item.filename)
            self.set_eventmap('vcd')

        else:
            command.append(item.url)

        # start child
        self.child_start(command, config.MPLAYER_NICE, 'quit\n')
        return None


    def eventhandler(self, event):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        ChildApp.eventhandler(self, event)

        if not self.has_child():
            return self.item.eventhandler(event)

        if event == PLAY_END:
            self.item.eventhandler(event)
            return True

        if event == PAUSE or event == PLAY:
            self.child_stdin('pause\n')
            return True

        if event == STOP:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == SEEK:
            pos = int(event.arg)
            if pos < 0:
                action='SeekRelative-'
                pos = 0 - pos
            else:
                action='SeekRelative+'
            if pos <= 15:
                pos = 15
            elif pos <= 30:
                pos = 30
            else:
                pos = 30
            self.child_stdin('%s%s\n' % (action, pos))
            return True

        if event == TOGGLE_OSD:
            self.child_stdin('OSDStreamInfos\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.child_stdin('ToggleInterleave\n')
            self.item['deinterlace'] = not self.item['deinterlace']
            return True

        if event == NEXT:
            self.child_stdin('EventNext\n')
            return True

        if event == PREV:
            self.child_stdin('EventPrior\n')
            return True

        # DVD NAVIGATION
        if event == DVDNAV_LEFT:
            self.child_stdin('EventLeft\n')
            return True

        if event == DVDNAV_RIGHT:
            self.child_stdin('EventRight\n')
            return True

        if event == DVDNAV_UP:
            self.child_stdin('EventUp\n')
            return True

        if event == DVDNAV_DOWN:
            self.child_stdin('EventDown\n')
            return True

        if event == DVDNAV_SELECT:
            self.child_stdin('EventSelect\n')
            return True

        if event == DVDNAV_TITLEMENU:
            self.child_stdin('TitleMenu\n')
            return True

        if event == DVDNAV_MENU:
            self.child_stdin('Menu\n')
            return True

        # VCD NAVIGATION
        if event in INPUT_ALL_NUMBERS:
            self.child_stdin('Number%s\n' % event.arg)
            time.sleep(0.1)
            self.child_stdin('EventSelect\n')
            return True

        if event == MENU:
            self.child_stdin('TitleMenu\n')
            return True


        # DVD/VCD language settings
        if event == VIDEO_NEXT_AUDIOLANG and self.max_audio:
            if self.current_audio < self.max_audio - 1:
                self.child_stdin('AudioChannelNext\n')
                self.current_audio += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.child_stdin('AudioChannelDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_audio):
                    self.child_stdin('AudioChannelPrior\n')
                    time.sleep(0.1)
                self.current_audio = -1
            return True

        if event == VIDEO_NEXT_SUBTITLE and self.max_subtitle:
            if self.current_subtitle < self.max_subtitle - 1:
                self.child_stdin('SpuNext\n')
                self.current_subtitle += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.child_stdin('SpuDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_subtitle):
                    self.child_stdin('SpuPrior\n')
                    time.sleep(0.1)
                self.current_subtitle = -1
            return True

        if event == VIDEO_NEXT_ANGLE:
            self.child_stdin('EventAngleNext\n')
            time.sleep(0.1)
            return True

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)
