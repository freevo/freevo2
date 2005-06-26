# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin and application for video
# -----------------------------------------------------------------------------
# $Id$
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

# python imports
import os
import re
import popen2
import logging

# external imports
import notifier
import mmpython

from kaa.mevas.displays import bmovlcanvas

# freevo imports
import config
import util
import plugin
import gui
import gui.displays
import gui.areas
import gui.windows

from application import mplayer
from event import *

# get logging object
log = logging.getLogger('video')


class PluginInterface(plugin.Plugin):
    """
    MPlayer plugin for the video player. It will create an MPlayer object
    and register it to the plugin interface as video player.
    """
    def __init__(self):
        # init plugin
        plugin.Plugin.__init__(self)

        # register mplayer as the object to play video
        plugin.register(MPlayer(), plugin.VIDEO_PLAYER, True)



class MPlayer(mplayer.Application):
    """
    The main class to control mplayer
    """
    def __init__(self):
        """
        Init the mplayer object
        """
        mplayer.Application.__init__(self, 'video', True)
        self.seek        = 0
        self._timer_id   = None
        self.hide_osd_cb = False
        self.use_bmovl   = True

        self.width  = 0
        self.height = 0
        self.screen = None
        self.area_handler = None


    def rate(self, item):
        """
        Rating about how good the player can play the given item. Possible
        values are 2 (good), 1 (possible) and 0 (unplayable).
        """
        if item.url[:6] in ('dvd://', 'vcd://') and item.url.endswith('/'):
            return 1
        if item.mode in ('dvd', 'vcd'):
            return 2
        if item.mimetype in config.VIDEO_MPLAYER_SUFFIX:
            return 2
        if item.network_play:
            return 1
        return 0


    def play(self, options, item):
        """
        Play a VideoItem with mplayer
        """
        self.options = options
        self.item    = item

        mode         = item.mode
        url          = item.url

        self.item_info    = None
        self.item_length  = -1
        self.item.elapsed = 0

        if mode == 'file':
            url = item.url[6:]
            self.item_info = mmpython.parse(url)
            if hasattr(self.item_info, 'get_length'):
                self.item_length = self.item_info.get_endpos()
                self.dynamic_seek_control = True

        if url.startswith('dvd://') and url[-1] == '/':
            url += '1'

        if url == 'vcd://':
            c_len = 0
            for i in range(len(item.info.tracks)):
                if item.info.tracks[i].length > c_len:
                    c_len = item.info.tracks[i].length
                    url = item.url + str(i+1)

        try:
            log.info('MPlayer.play(): mode=%s, url=%s' % (mode, url))
        except UnicodeError:
            log.info('MPlayer.play(): [non-ASCII data]')

        if mode == 'file' and not os.path.isfile(url):
            # This event allows the videoitem which contains subitems to
            # try to play the next subitem
            return '%s\nnot found' % os.path.basename(url)


        # Build the MPlayer command
        command = [ config.MPLAYER_CMD ] + \
                  config.MPLAYER_ARGS_DEF.split(' ') + \
                  [ '-slave', '-ao'] + \
                  config.MPLAYER_AO_DEV.split(' ')

        additional_args = []

        if mode == 'dvd':
            if config.DVD_LANG_PREF:
                # There are some bad mastered DVDs out there. E.g. the specials
                # on the German Babylon 5 Season 2 disc claim they have more
                # than one audio track, even more then on en. But only the
                # second on works, mplayer needs to be started without -alang
                # to find the track
                if hasattr(item, 'mplayer_audio_broken') and \
                       item.mplayer_audio_broken:
                    log.warning('dvd audio broken, try without alang')
                else:
                    additional_args += [ '-alang', config.DVD_LANG_PREF ]

            if config.DVD_SUBTITLE_PREF:
                # Only use if defined since it will always turn on subtitles
                # if defined
                additional_args += [ '-slang', config.DVD_SUBTITLE_PREF ]

        if hasattr(item.media, 'devicename') and mode != 'file':
            additional_args += [ '-dvd-device', item.media.devicename ]

        elif mode == 'dvd':
            # dvd on harddisc
            additional_args += [ '-dvd-device', item.filename ]
            url = url[:6] + url[url.rfind('/')+1:]

        if item.media and hasattr(item.media,'devicename'):
            additional_args += [ '-cdrom-device', item.media.devicename ]

        if item.selected_subtitle == -1:
            additional_args += [ '-noautosub' ]

        elif item.selected_subtitle and mode == 'file':
            if os.path.isfile(os.path.splitext(item.filename)[0]+'.idx'):
                additional_args += [ '-vobsubid', str(item.selected_subtitle) ]
            else:
                additional_args += [ '-sid', str(item.selected_subtitle) ]

        elif item.selected_subtitle:
            additional_args += [ '-sid', str(item.selected_subtitle) ]

        if item.selected_audio != None:
            additional_args += [ '-aid', str(item.selected_audio) ]

        if item['deinterlace'] and config.MPLAYER_VF_INTERLACED:
            additional_args += [ '-vf-pre',  config.MPLAYER_VF_INTERLACED ]
        elif not item['deinterlace'] and config.MPLAYER_VF_PROGRESSIVE:
            additional_args += [ '-vf-pre',  config.MPLAYER_VF_PROGRESSIVE ]

        mode = item.mimetype
        if not config.MPLAYER_ARGS.has_key(mode):
            mode = 'default'

        # Mplayer command and standard arguments
        command += [ '-v', '-vo', config.MPLAYER_VO_DEV +
                     config.MPLAYER_VO_DEV_OPTS ]

        # mode specific args
        command += config.MPLAYER_ARGS[mode].split(' ')

        # make the options a list
        command += additional_args

        if hasattr(item, 'is_playlist') and item.is_playlist:
            command.append('-playlist')

        if config.MPLAYER_RESAMPLE_AUDIO and self.item_info and \
               hasattr(self.item_info, 'audio') and self.item_info.audio and \
               hasattr(self.item_info.audio[0], 'samplerate') and \
               self.item_info.audio[0].samplerate and \
               self.item_info.audio[0].samplerate < 40000:
            srate = max(41000, min(self.item_info.audio[0].samplerate * 2,
                                   48000))
            log.info('resample audio from %s to %s',
                     self.item_info.audio[0].samplerate, srate)
            command += [ '-srate', str(srate) ]

        # add the file to play
        command.append(url)

        if options:
            command += options

        # Use software scaler? If not, we also deactivate
        # bmovl because resizing doesn't work
        self.use_bmovl = False
        if '-nosws' in command:
            command.remove('-nosws')

        elif not '-framedrop' in command:
            command += config.MPLAYER_SOFTWARE_SCALER.split(' ')
            self.use_bmovl = True

        # correct avi delay based on mmpython settings
        if config.MPLAYER_SET_AUDIO_DELAY and item.info.has_key('delay') and \
               item.info['delay'] > 0:
            command += [ '-mc', str(int(item.info['delay'])+1), '-delay',
                         '-' + str(item.info['delay']) ]

        while '' in command:
            command.remove('')

        # autocrop
        if config.MPLAYER_AUTOCROP and \
               str(' ').join(command).find('crop=') == -1:
            log.info('starting autocrop')
            (x1, y1, x2, y2) = (1000, 1000, 0, 0)
            crop_cmd = command[1:] + ['-ao', 'null', '-vo', 'null', '-ss',
                                      '60', '-frames', '20', '-vf',
                                      'cropdetect' ]
            child = popen2.Popen3(self.correct_filter_chain(crop_cmd), 1, 100)
            crop = '^.*-vf crop=([0-9]*):([0-9]*):([0-9]*):([0-9]*).*'
            exp = re.compile(crop)
            while(1):
                data = child.fromchild.readline()
                if not data:
                    break
                m = exp.match(data)
                if m:
                    x1 = min(x1, int(m.group(3)))
                    y1 = min(y1, int(m.group(4)))
                    x2 = max(x2, int(m.group(1)) + int(m.group(3)))
                    y2 = max(y2, int(m.group(2)) + int(m.group(4)))

            if x1 < 1000 and x2 < 1000:
                command = command + [ '-vf' , 'crop=%s:%s:%s:%s' % \
                                      (x2-x1, y2-y1, x1, y1) ]

            child.wait()

        if item.subtitle_file:
            mp, f = util.resolve_media_mountdir(item.subtitle_file)
            if mp:
                mp.mount()
            command += ['-sub', f]

        if item.audio_file:
            mp, f = util.resolve_media_mountdir(item.audio_file)
            if mp:
                mp.mount()
            command += ['-audiofile', f]

        if self.use_bmovl:
            self.fifoname = bmovlcanvas.create_fifo()
            command += [ '-vf', 'bmovl=1:0:%s' % self.fifoname ]

        self.show()

        mplayer.Application.play(self, command)
        self.osd_visible = False

        return None


    def stop(self):
        if self.screen:
            gui.displays.remove(self.screen)
            self.area_handler = None
            self.screen = None
            self.width  = 0
            self.height = 0
        mplayer.Application.stop(self)


    def hide_osd(self):
        """
        Hide the seek osd. This is a rc callback after pressing seek
        """
        if not self.osd_visible and self.has_child() and self.area_handler:
            self.area_handler.hide()
            gui.displays.get().update()
        self._timer_id = None
        return False


    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """
        if mplayer.Application.eventhandler(self, event):
            return True

        if not self.has_child():
            return self.item.eventhandler(event)

        if event == VIDEO_MANUAL_SEEK:
            gui.windows.WaitBox('Seek disabled, press QUIT').show()
            return True

        if event == STOP:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == 'AUDIO_ERROR_START_AGAIN':
            self.stop()
            self.play(self.options, self.item)
            return True

        if event == PLAY_END:
            self.stop()
            self.item.eventhandler(event)
            return True

        if event == VIDEO_SEND_MPLAYER_CMD:
            self.send_command('%s\n' % event.arg)
            return True

        if event == TOGGLE_OSD:
            if not self.use_bmovl:
                # We don't use bmovl so we use the normal mplayer osd
                self.send_command('osd\n')
                return True

            if not self.area_handler:
                # Bmovl not ready yet
                return True

            self.osd_visible = not self.osd_visible
            if self.osd_visible:
                self.area_handler.display_style['video'] = 1
                self.area_handler.draw(self.item)
                self.area_handler.show()
            else:
                self.area_handler.hide()
                gui.displays.get().update()
                self.area_handler.display_style['video'] = 0
                self.area_handler.draw(self.item)
            return True

        if event == PAUSE or event == PLAY:
            self.send_command('pause\n')
            return True

        if event == SEEK:
            if event.arg > 0 and self.item_length != -1 and \
                   self.dynamic_seek_control:
                # check if the file is growing
                if self.item_info.get_endpos() == self.item_length:
                    # not growing, deactivate this
                    self.item_length = -1

                self.dynamic_seek_control = False

            if event.arg > 0 and self.item_length != -1:
                # safety time for bad mplayer seeking
                seek_safety_time = 20
                if self.item_info['type'] in ('MPEG-PES', 'MPEG-TS'):
                    seek_safety_time = 500

                # check if seek is allowed
                if self.item_length <= self.item.elapsed + event.arg + \
                       seek_safety_time:
                    # get new length
                    self.item_length = self.item_info.get_endpos()

                # check again if seek is allowed
                if self.item_length <= self.item.elapsed + event.arg + \
                       seek_safety_time:
                    log.info('unable to seek %s secs at time %s, length %s' % \
                            (event.arg, self.item.elapsed, self.item_length))
                    return False

            if self.use_bmovl and not self.osd_visible:
                if self._timer_id != None:
                    notifier.removeTimer( self._timer_id )
                    self._timer_id = None
                elif self.area_handler:
                    self.area_handler.show()
                cb = notifier.Callback( self.hide_osd )
                self._timer_id = notifier.addTimer( 2000, cb )

            self.send_command('seek %s\n' % event.arg)
            return True

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)


    def elapsed(self, sec):
        """
        Callback for elapsed time changes.
        """
        self.item.elapsed = sec
        if self.width and self.height and not self.screen:
            log.info('activating bmovl')
            self.screen = gui.displays.set('Bmovl', (self.width, self.height),
                                           self.fifoname)
            areas = ['screen', 'view', 'info', 'progress']
            self.area_handler = gui.areas.Handler('video', areas)
            self.area_handler.hide(False)
            self.area_handler.draw(self.item)
            self.send_command('osd 0\n')

        if self.area_handler:
            self.area_handler.draw(self.item)


    def message(self, line):
        """
        A message line from mplayer.
        """
        try:
            if line.find('SwScaler:') ==0 and line.find(' -> ') > 0 and \
                   line[line.find(' -> '):].find('x') > 0:
                width, height = line[line.find(' -> ')+4:].split('x')
                if self.height < int(height):
                    self.width  = int(width)
                    self.height = int(height)

            if line.find('Expand: ') == 0:
                width, height = line[7:line.find(',')].split('x')
                if self.height < int(height):
                    self.width  = int(width)
                    self.height = int(height)
        except Exception, e:
            log.error(e)
