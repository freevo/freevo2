# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xine.py - the Freevo XINE module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Activate this plugin by putting plugin.activate('video.xine') in your
# local_conf.py. Than xine will be used for DVDs when you SELECT the item.
# When you select a title directly in the menu, this plugin won't be used
# and the default player (mplayer) will be used. You need xine-ui >= 0.9.22
# to use this.
#
# Todo:        
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.44  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.43  2004/06/28 15:53:59  dischi
# angle switching
#
# Revision 1.42  2004/06/19 17:21:52  dischi
# only set app.mode to valid events
#
# Revision 1.41  2004/05/02 08:55:52  dischi
# dvd as .iso support
#
# Revision 1.39  2004/02/06 19:29:06  dischi
# fix/cleanup dvd on hd handling
#
# Revision 1.38  2004/02/03 20:51:12  dischi
# fix/enhance dvd on disc
#
# Revision 1.37  2004/02/02 22:15:53  outlyer
# Support for mirrors of DVDs...
#
# (1) Make one using vobcopy, run 'vobcopy -m'
# (2) Put it in your movie directory and it'll look like a single file, and can
#     be played with XINE with all of the features of the original DVD (chapters,
#     audio tracks, etc) and works with dvdnav.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
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
# ----------------------------------------------------------------------- */


import time, os, re
import copy

import config     # Configuration handler. reads config file.
import childapp   # Handle child applications
import rc         # The RemoteControl class.
import util

from event import *
import plugin


class PluginInterface(plugin.Plugin):
    """
    Xine plugin for the video player.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        try:
            config.XINE_COMMAND
        except:
            print String(_( 'ERROR' )) + ': ' + \
                  String(_("'XINE_COMMAND' not defined, plugin 'xine' deactivated.\n" \
                           'please check the xine section in freevo_config.py' ))
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
        else:
            type = 'X'

        if not hasattr(config, 'XINE_VERSION'):
            config.XINE_VERSION = 0
            for data in util.popen3.stdout('%s --version' % config.XINE_COMMAND):
                m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
                if m:
                    config.XINE_VERSION = int('%02d%02d%02d' % (int(m.group(1)),
                                                                  int(m.group(2)),
                                                                  int(m.group(3))))
                    if data.find('cvs') >= 0:
                        config.XINE_VERSION += 1

            _debug_('detect xine version %s' % config.XINE_VERSION)
            
        if config.XINE_VERSION < 922:
            print String(_( 'ERROR' )) + ': ' + \
                  String(_( "'xine-ui' version too old, plugin 'xine' deactivated" ))
            print String(_( 'You need software %s' )) % 'xine-ui > 0.9.21'
            return
            
        # register xine as the object to play
        plugin.register(Xine(type, config.XINE_VERSION), plugin.VIDEO_PLAYER, True)



class Xine:
    """
    the main class to control xine
    """
    def __init__(self, type, version):
        self.name      = 'xine'

        self.app_mode  = ''
        self.xine_type = type
        self.version   = version
        self.app       = None

        self.command = [ '--prio=%s' % config.MPLAYER_NICE ] + \
                       config.XINE_COMMAND.split(' ') + \
                       [ '--stdctl', '-V', config.XINE_VO_DEV,
                         '-A', config.XINE_AO_DEV ] + \
                       config.XINE_ARGS_DEF.split(' ')


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.url.startswith('dvd://'):
            if hasattr(item, 'filename') and item.filename and \
                   item.filename.endswith('.iso'):
                return 0
            return 2
        if item.url.startswith('vcd://'):
            if self.version > 922 and item.url == 'vcd://':
                return 2
            return 0

        if item.mimetype in config.VIDEO_XINE_SUFFIX:
            return 2
        if item.network_play:
            return 1
        return 0
    
    
    def play(self, options, item):
        """
        play a dvd with xine
        """
        self.item     = item
        if config.EVENTS.has_key(item.mode):
            self.app_mode = item.mode
        else:
             self.app_mode = 'video'

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        command = copy.copy(self.command)

        if item['deinterlace'] and (self.xine_type == 'X' or self.version > 922):
            command.append('-D')

        if not rc.PYLIRC and '--no-lirc' in command:
            command.remove('--no-lirc')

        if self.version < 923:
            for arg in command:
                if arg.startswith('--post'):
                    command.remove(arg)
                    break
                
        self.max_audio        = 0
        self.current_audio    = -1
        self.max_subtitle     = 0
        self.current_subtitle = -1

        if item.mode == 'dvd':
            for track in item.info['tracks']:
                self.max_audio = max(self.max_audio, len(track['audio']))

            for track in item.info['tracks']:
                self.max_subtitle = max(self.max_subtitle, len(track['subtitles']))

        if item.mode == 'dvd' and hasattr(item.media, 'devicename'):
            # dvd:///dev/dvd/2
            command.append('dvd://%s/%s' % (item.media.devicename, item.url[6:]))
        elif item.mode == 'dvd': # no devicename? Probably a mirror image on the HD
            command.append(item.url)

        elif item.mode == 'vcd':
            # vcd:///dev/cdrom -- NO track support (?)
            command.append('vcd://%s' % item.media.devicename)

        elif item.mimetype == 'cue':
            command.append('vcd://%s' % item.filename)
            self.app_mode = 'vcd'
            
        else:
            command.append(item.url)
            
        _debug_('Xine.play(): Starting cmd=%s' % command)

        rc.app(self)
        self.app = childapp.ChildApp2(command)
        return None
    

    def stop(self):
        """
        Stop xine
        """
        if self.app:
            self.app.stop('quit\n')
            rc.app(None)
            

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if not self.app:
            return self.item.eventhandler(event)
            
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        if event == PAUSE or event == PLAY:
            self.app.write('pause\n')
            return True

        if event == STOP:
            self.stop()
            return self.item.eventhandler(event)

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
            self.app.write('%s%s\n' % (action, pos))
            return True

        if event == TOGGLE_OSD:
            self.app.write('OSDStreamInfos\n')
            return True

        if event == VIDEO_TOGGLE_INTERLACE:
            self.app.write('ToggleInterleave\n')
            self.item['deinterlace'] = not self.item['deinterlace']
            return True

        if event == NEXT:
            self.app.write('EventNext\n')
            return True

        if event == PREV:
            self.app.write('EventPrior\n')
            return True

        # DVD NAVIGATION
        if event == DVDNAV_LEFT:
            self.app.write('EventLeft\n')
            return True
            
        if event == DVDNAV_RIGHT:
            self.app.write('EventRight\n')
            return True
            
        if event == DVDNAV_UP:
            self.app.write('EventUp\n')
            return True
            
        if event == DVDNAV_DOWN:
            self.app.write('EventDown\n')
            return True
            
        if event == DVDNAV_SELECT:
            self.app.write('EventSelect\n')
            return True
            
        if event == DVDNAV_TITLEMENU:
            self.app.write('TitleMenu\n')
            return True
            
        if event == DVDNAV_MENU:
            self.app.write('Menu\n')
            return True

        # VCD NAVIGATION
        if event in INPUT_ALL_NUMBERS:
            self.app.write('Number%s\n' % event.arg)
            time.sleep(0.1)
            self.app.write('EventSelect\n')
            return True
        
        if event == MENU:
            self.app.write('TitleMenu\n')
            return True


        # DVD/VCD language settings
        if event == VIDEO_NEXT_AUDIOLANG and self.max_audio:
            if self.current_audio < self.max_audio - 1:
                self.app.write('AudioChannelNext\n')
                self.current_audio += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.app.write('AudioChannelDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_audio):
                    self.app.write('AudioChannelPrior\n')
                    time.sleep(0.1)
                self.current_audio = -1
            return True
            
        if event == VIDEO_NEXT_SUBTITLE and self.max_subtitle:
            if self.current_subtitle < self.max_subtitle - 1:
                self.app.write('SpuNext\n')
                self.current_subtitle += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.app.write('SpuDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_subtitle):
                    self.app.write('SpuPrior\n')
                    time.sleep(0.1)
                self.current_subtitle = -1
            return True
            
        if event == VIDEO_NEXT_ANGLE:
            self.app.write('EventAngleNext\n')
            time.sleep(0.1)
            return True            

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)
