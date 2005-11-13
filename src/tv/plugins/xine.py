# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# xine.py - xine tv plugin
#
# Notes:
#     To test timeshifting with this plugin you must configure some items in
#     Freevo and also ~/.xine/config.
#
#     In your local_conf.py you needi:
#         TV_TIMESHIFT_ENABLE = 1
#         TV_TIMESHIFT_DIR = '/dir/to/save/timeshift/file/'
#
#     In ~/.xine/config you need to configure the #save plugin with the same
#     directory you used for TV_TIMESHIFT_DIR:
#         # directory for saving streams
#         # string, default: 
#         media.capture.save_dir:/dir/to/save/timeshift/file
#
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
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
import os
import copy
import logging
import mbus

# freevo core imports
from freevo import mcomm

# freevo ui imports
import config
import plugin

from event import *
from application import ChildApp

# get logging object
log = logging.getLogger('tv')

class PluginInterface(plugin.Plugin):
    """
    Xine plugin for tv. The plugin is beta and only works with dvb.

    Your channel list must contain the identifier from the xine
    channels.conf as frequence
    """
    def __init__(self):
        # detect xine and it's version
        config.detect('xine')

        try:
            config.XINE_COMMAND
        except:
            self.reason = '\'XINE_COMMAND\' not defined'
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
            if config.FBXINE_VERSION < '0.99.1' and \
                   config.FBXINE_VERSION < '0.9.23':
                self.reason = "'fbxine' version too old"
                return

        elif config.XINE_COMMAND.find('df_xine') >= 0:
            type = 'df'

        else:
            type = 'X'
            if config.XINE_VERSION < '0.99.1' and \
                   config.XINE_VERSION < '0.9.23':
                self.reason = "'xine' version too old"
                return

        plugin.Plugin.__init__(self)

        # register xine as the object to play
        plugin.register(Xine(type), plugin.TV)



class Xine(ChildApp):
    """
    the main class to control xine
    """
    def __init__(self, type):
        ChildApp.__init__(self, 'xine', 'video', True, False, True)
        self.name = 'xine'
        self.xine_type = type
        self.id = None

        self.timeshift = getattr(config, 'TV_TIMESHIFT_ENABLE', 0)
        self.timeshift_dir = getattr(config, 'TV_TIMESHIFT_DIR', 
                                     config.TV_RECORD_DIR)
        self.timeshift_file = 'xine_ts.mpeg'

        self.server = None
        mcomm.register_entity_notification(self.__entity_update)


    def __entity_update(self, entity):
        if not entity.present and entity == self.server:
            log.info('recordserver lost')
            self.server = None
            return

        if entity.present and \
               entity.matches(mcomm.get_address('recordserver')):
            log.info('recordserver found')
            self.server = entity


    def rate(self, channel, device, uri):
        """
        FIXME: remove this function, every player can play everything
        through the recordserver
        """
        return 2

    
    def play(self, channel):
        """
        Play with xine
        """
        if not self.server:
            log.error('FIXME: no server found')
            return
        
        self.item = channel
        self.server.call('watch.start', self.__receive_url, channel)
        return None
    

    def __receive_url(self, result):
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return

        self.id, url = result.arguments
        # create command
        command = config.XINE_COMMAND.split(' ') + \
                  [ '--stdctl', '-V', config.XINE_VO_DEV, '-A',
                    config.XINE_AO_DEV ] + config.XINE_ARGS_DEF.split(' ')

        if config.XINE_COMMAND.startswith(config.CONF.xine) and \
               config.XINE_USE_LIRC:
            command.append('--no-lirc')

        if config.XINE_COMMAND.startswith(config.CONF.fbxine) and \
               config.FBXINE_USE_LIRC:
            command.append('--no-lirc')

        if self.timeshift:
            tsfile = os.path.join(self.timeshift_dir, self.timeshift_file)
            if os.path.exists(tsfile):
                os.remove(tsfile)

            # we don't need to specify #demux when using a .mpeg in #save
            command.append('%s#save:%s' % (url, self.timeshift_file))
        else:
            command.append('%s#demux:mpeg_pes' % url)

        self.show()

        # start child
        log.info('Xine.play(): Starting cmd=%s' % command)
        self.child_start(command, config.MPLAYER_NICE, 'quit\n')

        log.info('live recording started')


    def __stop_done(self, result):
        if isinstance(result, mbus.types.MError):
            log.error(str(result))
            return
        if not result.appStatus:
            log.error(str(result.appDescription))
            return
        return

    
    def eventhandler(self, event):
        """
        Eventhandler for xine control.
        """
        if event == PLAY_END:
            # stop recordserver live recording
            if not self.server:
                log.error('FIXME: unable to stop without server')
            else:
                if not self.id:
                    log.error('FIXME: unable to stop without id')
                else:
                    self.server.call('watch.stop', self.__stop_done, self.id)
                self.id = None
                
        ChildApp.eventhandler(self, event)

        if not self.has_child():
            return True

        if event == PLAY_END:
            return True

        if event == STOP:
            self.stop()
            return True

        if event == TOGGLE_OSD:
            self.child_stdin('PartMenu\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.child_stdin('ToggleInterleave\n')
            return True

        if self.timeshift:
            if event == PAUSE or event == PLAY:
                self.child_stdin('pause\n')
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

                cmd = '%s%s\n' % (action, pos)
                log.debug('seek command: %s' % cmd)

                self.child_stdin(cmd)
                return True


        # nothing found
        return False
