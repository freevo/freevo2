#if 0 /*
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
# This plugin can also be used for VCD playback with menus. Install
# xine-vcdnav and set XINE_USE_VCDNAV = 1
#
# WARNING:
# xine-vcdnav has some problems. Some VCDs won't play at all, some one
# in some drives. It also can take up to 10 secs until the video
# starts. When nothing happens and you press STOP, it can also take up
# to 10 secs until xine dies (better: xine will be killed). This could
# also crash Freevo (python segfault). 
#
#
# Todo:        
#
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.21  2003/11/21 17:56:50  dischi
# Plugins now 'rate' if and how good they can play an item. Based on that
# a good player will be choosen.
#
# Revision 1.20  2003/11/09 12:01:00  dischi
# add subtitle selection and osd info support for xine (needs current xine-ui cvs
#
# Revision 1.19  2003/11/01 19:54:18  dischi
# port to new xine-lib
#
# Revision 1.18  2003/10/21 21:17:42  gsbarbieri
# Some more i18n improvements.
#
# Revision 1.17  2003/09/19 22:09:16  dischi
# use new childapp thread function
#
# Revision 1.16  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.15  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.14  2003/09/01 16:41:37  dischi
# send PLAY_START event
#
# Revision 1.13  2003/08/30 18:52:53  dischi
# Aubin, don't do that :-)
# Make a nice ItemPlugin do set the color values. Take a look at
# bookmarker.py how.
#
# Revision 1.12  2003/08/28 03:46:13  outlyer
# Support for Chapter-by-chapter navigation in DVDs using the CH+ and CH- keys.
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
#endif


import time, os
import signal
import popen2, re

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

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
            print _( 'ERROR' ) + ': ' + \
                  _("'XINE_COMMAND' not defined, plugin 'xine' deactivated")
            print _( 'please check the xine section in freevo_config.py' )
            return

        if config.XINE_COMMAND.find('fbxine') >= 0:
            type = 'fb'
        else:
            type = 'X'

        xine_version = 0
        xine_cvs     = 0
        
        child = popen2.Popen3('%s --version' % config.XINE_COMMAND, 1, 100)
        while(1):
            data = child.fromchild.readline()
            if not data:
                break
            m = re.match('^.* v?([0-9])\.([0-9]+)\.([0-9]*).*', data)
            if m:
                if data.find('cvs') >= 0:
                    xine_cvs = 1
                xine_version =int('%02d%02d%02d' % (int(m.group(1)), int(m.group(2)),
                                                    int(m.group(3))))

        child.wait()

        if xine_cvs:
            xine_version += 1
            
        if xine_version < 922:
            if type == 'fb':
                print _( 'ERROR' ) + ': ' + \
                      _( "'fbxine' version too old, plugin 'xine' deactivated" )
                print _( 'You need software %s' ) % 'xine-ui > 0.9.21'
                return
            print _( 'WARNING' ) + ': ' + \
                  _( "'xine' version too old, plugin in fallback mode" )
            print _( "You need %s to use all features of the '%s' plugin" ) % \
                  ( 'xine-ui > 0.9.21', 'xine' )
            
        # create the xine object
        xine = util.SynchronizedObject(Xine(type, xine_version))

        # register it as the object to play
        plugin.register(xine, plugin.VIDEO_PLAYER, True)

        for i in config.SUFFIX_VIDEO_XINE_FILES:
            if not i in config.SUFFIX_VIDEO_FILES:
                config.SUFFIX_VIDEO_FILES.append(i)


class Xine:
    """
    the main class to control xine
    """
    
    def __init__(self, type, version):
        self.name = 'xine'

        # start the thread
        self.thread = childapp.ChildThread()
        self.thread.stop_osd = True

        self.mode         = None
        self.app_mode     = ''
        self.xine_type    = type
        self.xine_version = version

        command = config.XINE_COMMAND
        if self.xine_version > 921:
            if self.xine_type == 'X':
                command = '%s --no-splash' % config.XINE_COMMAND
            command = '%s --stdctl' % command
            if rc.PYLIRC:
                command = '%s --no-lirc' % command

        self.command = '%s -V %s -A %s' % (command, config.XINE_VO_DEV, config.XINE_AO_DEV)


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.mode == 'dvd':
            return 2
        if item.mode == 'vcd':
            if self.xine_version > 922:
                if not item.filename or item.filename == '0':
                    return 2
                return 0
            else:
                return 0
        if os.path.splitext(item.filename)[1][1:].lower() in \
               config.SUFFIX_VIDEO_XINE_FILES:
            return 2
        return 0
    
    
    def play(self, options, item):
        """
        play a dvd with xine
        """

        self.app_mode = item.mode       # dvd or vcd keymap
        self.item     = item

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        command = self.command

        if item.deinterlace or \
           (hasattr(config, 'XINE_ALWAYS_DEINTERLACE') and config.XINE_ALWAYS_DEINTERLACE):
            if (config.XINE_VO_DEV == 'vidix' or self.xine_type == 'fb') and \
                   self.xine_version > 921:
                command = '%s --post tvtime' % command
            else:
                command = '%s -D' % command

        command = command.split(' ')

        self.max_audio = 0
        self.current_audio = -1

        self.max_subtitle = 0
        self.current_subtitle = -1

        if item.mode == 'dvd':
            for track in item.info['tracks']:
                self.max_audio = max(self.max_audio, len(track['audio']))

            for track in item.info['tracks']:
                self.max_subtitle = max(self.max_subtitle, len(track['subtitles']))

        if item.mode == 'dvd':
            # dvd:///dev/dvd/2
            if not item.filename or item.filename == '0':
                track = ''
            else:
                track = item.filename
            command.append('dvd://%s/%s' % (item.media.devicename, track))

        elif item.mode == 'vcd':
            # vcd:///dev/cdrom -- NO track support (?)
            command.append('vcd://%s' % item.media.devicename)

        elif item.mime_type == 'cue':
            command.append('vcd://%s' % item.filename)

        else:
            command.append(item.url)
            
        _debug_('Xine.play(): Starting thread, cmd=%s' % command)

        rc.app(self)
        self.thread.start(childapp.ChildApp, command)
        return None
    

    def stop(self):
        """
        Stop xine and set thread to idle
        """
        self.thread.stop('quit\n')
        rc.app(None)
            

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for xine control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        # fallback for older versions of xine
        if self.xine_version < 922:
            return True
        
        if event == PAUSE or event == PLAY:
            self.thread.app.write('pause\n')
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
            self.thread.app.write('%s%s\n' % (action, pos))
            return True

        # DVD NAVIGATION
        if event == DVDNAV_LEFT:
            self.thread.app.write('EventLeft\n')
            return True
            
        if event == DVDNAV_RIGHT:
            self.thread.app.write('EventRight\n')
            return True
            
        if event == DVDNAV_UP:
            self.thread.app.write('EventUp\n')
            return True
            
        if event == DVDNAV_DOWN:
            self.thread.app.write('EventDown\n')
            return True
            
        if event == DVDNAV_SELECT:
            self.thread.app.write('EventSelect\n')
            return True
            
        if event == DVDNAV_TITLEMENU:
            self.thread.app.write('TitleMenu\n')
            return True
            
        if event == DVDNAV_MENU:
            self.thread.app.write('Menu\n')
            return True

        if event == NEXT:
            self.thread.app.write('EventNext\n')
            return True

        if event == PREV:
            self.thread.app.write('EventPrior\n')
            return True

        if event == TOGGLE_OSD:
            self.thread.app.write('OSDStreamInfos\n')
            return True


        # VCD NAVIGATION
        if event in INPUT_ALL_NUMBERS:
            self.thread.app.write('Number%s\n' % event.arg)
            time.sleep(0.1)
            self.thread.app.write('EventSelect\n')
            return True
        
        if event == MENU:
            self.thread.app.write('TitleMenu\n')
            return True


        if event == VIDEO_NEXT_AUDIOLANG and self.max_audio:
            if self.current_audio < self.max_audio - 1:
                self.thread.app.write('AudioChannelNext\n')
                self.current_audio += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.thread.app.write('AudioChannelDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_audio):
                    self.thread.app.write('AudioChannelPrior\n')
                    time.sleep(0.1)
                self.current_audio = -1
            return True
            
        if event == VIDEO_NEXT_SUBTITLE and self.max_subtitle:
            if self.current_subtitle < self.max_subtitle - 1:
                self.thread.app.write('SpuNext\n')
                self.current_subtitle += 1
                # wait until the stream is changed
                time.sleep(0.1)
            else:
                # bad hack to warp around
                if self.xine_type == 'fb':
                    self.thread.app.write('SpuDefault\n')
                    time.sleep(0.1)
                for i in range(self.max_subtitle):
                    self.thread.app.write('SpuPrior\n')
                    time.sleep(0.1)
                self.current_subtitle = -1
            return True
            
        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)
