#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.46  2003/12/07 19:40:30  dischi
# convert OVERSCAN variable names
#
# Revision 1.45  2003/12/06 16:25:45  dischi
# support for type=url and <playlist> and <player>
#
# Revision 1.44  2003/11/29 18:37:30  dischi
# build config.VIDEO_SUFFIX in config on startup
#
# Revision 1.43  2003/11/28 20:08:59  dischi
# renamed some config variables
#
# Revision 1.42  2003/11/28 19:26:37  dischi
# renamed some config variables
#
# Revision 1.41  2003/11/22 15:57:47  dischi
# cleanup
#
# Revision 1.40  2003/11/21 18:04:27  dischi
# remove debug
#
# Revision 1.39  2003/11/21 17:56:50  dischi
# Plugins now 'rate' if and how good they can play an item. Based on that
# a good player will be choosen.
#
# Revision 1.38  2003/11/04 17:53:23  dischi
# Removed the unstable bmovl part from mplayer.py and made it a plugin.
# Even if we are in a code freeze, this is a major cleanup to put the
# unstable stuff in a plugin to prevent mplayer from crashing because of
# bmovl.
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
import threading, signal
import traceback, popen2

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

from event import *
import plugin

# RegExp
import re

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the video player.

    With this plugin Freevo can play all video files defined in
    VIDEO_MPLAYER_SUFFIX. This is the default video player for Freevo.
    """
    def __init__(self):
        mplayer_version = 0
        # create the mplayer object
        plugin.Plugin.__init__(self)

        child = popen2.Popen3( "%s -v" % config.MPLAYER_CMD, 1, 100)
        data = child.fromchild.readline() # Just need the first line
        if data:
            data = re.search( "^MPlayer (?P<version>\S+)", data )
            if data:                
                _debug_("MPlayer version is: %s" % data.group( "version" ))
                data = data.group( "version" )
                if data[ 0 ] == "1":
                    mplayer_version = 1.0
                elif data[ 0 ] == "0":
                    mplayer_version = 0.9
                elif data[ 0 : 7 ] == "dev-CVS":
                    mplayer_version = 9999
                _debug_("MPlayer version set to: %s" % mplayer_version)
                    
        child.wait()
        mplayer = util.SynchronizedObject(MPlayer(mplayer_version))

        # register it as the object to play audio
        plugin.register(mplayer, plugin.VIDEO_PLAYER, True)


class MPlayer:
    """
    the main class to control mplayer
    """
    def __init__(self, version):
        self.name = 'mplayer'
        self.thread = childapp.ChildThread()
        self.thread.stop_osd = True

        self.mode = None
        self.app_mode = 'video'
        self.version = version
        self.seek = 0
        self.seek_timer = threading.Timer(0, self.reset_seek)


    def rate(self, item):
        """
        How good can this player play the file:
        2 = good
        1 = possible, but not good
        0 = unplayable
        """
        if item.mode == 'dvd' or item.mode == 'vcd':
            if not item.filename or item.filename == '0':
                return 1
            return 2
        if os.path.splitext(item.filename)[1][1:].lower() in \
               config.VIDEO_MPLAYER_SUFFIX:
            return 2
        if item.mode == 'url':
            return 1
        return 0
    
    
    def play(self, options, item):
        """
        play a videoitem with mplayer
        """
        self.parameter = (options, item)
        
        mode         = item.mode
        network_play = item.network_play
        url          = item.url
        self.item    = item

        if mode == 'file' and not network_play:
            url = item.url[6:]

        if url == 'dvd://':
            url += '1'
            
        if url == 'vcd://':
            c_len = 0
            for i in range(len(item.info.tracks)):
                if item.info.tracks[i].length > c_len:
                    c_len = item.info.tracks[i].length
                    url = item.url + str(i+1)
            
        _debug_('MPlayer.play(): mode=%s, url=%s' % (mode, url))

        if mode == 'file' and not os.path.isfile(url) and not network_play:
            # This event allows the videoitem which contains subitems to
            # try to play the next subitem
            return '%s\nnot found' % os.path.basename(url)
       

        # Build the MPlayer command
        mpl = '--prio=%s %s %s -slave -ao %s' % (config.MPLAYER_NICE,
                                                 config.MPLAYER_CMD,
                                                 config.MPLAYER_ARGS_DEF,
                                                 config.MPLAYER_AO_DEV)

        additional_args = ''

        if mode == 'dvd':
            if config.DVD_LANG_PREF:
                # There are some bad mastered DVDs out there. E.g. the specials on
                # the German Babylon 5 Season 2 disc claim they have more than one
                # audio track, even more then on en. But only the second en works,
                # mplayer needs to be started without -alang to find the track
                if hasattr(item, 'mplayer_audio_broken') and item.mplayer_audio_broken:
                    print '*** dvd audio broken, try without alang ***'
                else:
                    additional_args = '-alang %s' % config.DVD_LANG_PREF

            if config.DVD_SUBTITLE_PREF:
                # Only use if defined since it will always turn on subtitles
                # if defined
                additional_args += ' -slang %s' % config.DVD_SUBTITLE_PREF

            additional_args += ' -dvd-device %s' % item.media.devicename

        if item.media:
            additional_args += ' -cdrom-device %s ' % item.media.devicename

        if item.selected_subtitle == -1:
            additional_args += ' -noautosub'

        elif item.selected_subtitle and item.mode == 'file':
            additional_args += ' -vobsubid %s' % item.selected_subtitle

        elif item.selected_subtitle:
            additional_args += ' -sid %s' % item.selected_subtitle
            
        if item.selected_audio:
            additional_args += ' -aid %s' % item.selected_audio

        if item.deinterlace:
            additional_args += ' -vop pp=fd'

        mode = item.mime_type
        if not config.MPLAYER_ARGS.has_key(mode):
            mode = 'default'

        # Mplayer command and standard arguments
        mpl += (' -v -vo ' + config.MPLAYER_VO_DEV + config.MPLAYER_VO_DEV_OPTS + \
                ' ' + config.MPLAYER_ARGS[mode])

        # make the options a list
        mpl = mpl.split(' ') + additional_args.split(' ')

        if hasattr(item, 'is_playlist') and item.is_playlist:
            mpl.append('-playlist')

        # add the file to play
        mpl.append(url)

        if options:
            mpl += options.split(' ')

        # use software scaler?
        if '-nosws' in mpl:
            mpl.remove('-nosws')

        elif not '-framedrop' in mpl:
            mpl += config.MPLAYER_SOFTWARE_SCALER.split(' ')

        # correct avi delay based on mmpython settings
        if config.MPLAYER_SET_AUDIO_DELAY and item.info.has_key('delay') and \
               item.info['delay'] > 0:
            mpl += ('-mc', str(int(item.info['delay'])+1), '-delay',
                    '-' + str(item.info['delay']))

        command = mpl

        while '' in command:
            command.remove('')

        # autocrop
        if config.MPLAYER_AUTOCROP and str(' ').join(command).find('crop=') == -1:
            _debug_('starting autocrop')
            (x1, y1, x2, y2) = (1000, 1000, 0, 0)
            crop_cmd = command[1:] + ['-ao', 'null', '-vo', 'null', '-ss', '60',
                                      '-frames', '20', '-vop', 'cropdetect' ]
            child = popen2.Popen3(self.vop_append(crop_cmd), 1, 100)
            exp = re.compile('^.*-vop crop=([0-9]*):([0-9]*):([0-9]*):([0-9]*).*')
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
                command = command + [ '-vop' , 'crop=%s:%s:%s:%s' % (x2-x1, y2-y1, x1, y1) ]
            
            child.wait()

        self.plugins = plugin.get('mplayer_video')

        for p in self.plugins:
            command = p.play(command, self)

        command=self.vop_append(command)

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        rc.app(self)

        self.thread.start(MPlayerApp, (command, self, item, network_play))

        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.stop('quit\n')
        rc.app(None)
        for p in self.plugins:
            command = p.stop()


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        for p in self.plugins:
            if p.eventhandler(event):
                return True

        if event == VIDEO_MANUAL_SEEK:
            self.seek = 0
            rc.set_context('input')
            return True
        
        if event.context == 'input':
            if event in INPUT_ALL_NUMBERS:
                self.reset_seek_timeout()
                self.seek = self.seek * 10 + int(event);
                return True
            
            elif event == INPUT_ENTER:
                self.seek_timer.cancel()
                self.seek *= 60
                self.thread.app.write('seek ' + str(self.seek) + ' 2\n')
                _debug_("seek "+str(self.seek)+" 2\n")
                self.seek = 0
                rc.set_context('video')
                return True

            elif event == INPUT_EXIT:
                _debug_('seek stopped')
                self.seek_timer.cancel()
                self.seek = 0
                rc.set_context('video')
                return True

        if event == STOP:
            self.stop()
            return self.item.eventhandler(event)

        if event == 'AUDIO_ERROR_START_AGAIN':
            self.stop()
            self.play(self.parameter[0], self.parameter[1])
            return True
        
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        try:
            if event == VIDEO_SEND_MPLAYER_CMD:
                self.thread.app.write('%s\n' % event.arg)
                return True

            if event == TOGGLE_OSD:
                self.thread.app.write('osd\n')
                return True

            if event == PAUSE or event == PLAY:
                self.thread.app.write('pause\n')
                return True

            if event == SEEK:
                self.thread.app.write('seek %s\n' % event.arg)
                return True
        except:
            print 'Exception while sending command to mplayer:'
            traceback.print_exc()
            return True
        
        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)

    
    def reset_seek(self):
        _debug_('seek timeout')
        self.seek = 0
        rc.set_context('video')

        
    def reset_seek_timeout(self):
        self.seek_timer.cancel()
        self.seek_timer = threading.Timer(config.MPLAYER_SEEK_TIMEOUT, self.reset_seek)
        self.seek_timer.start()

        
    def vop_append(self, command):
        """
        Change a mplayer command to support more than one -vop
        parameter. This function will grep all -vop parameter from
        the command and add it at the end as one vop argument
        """
        ret = []
        vop = ''
        next_is_vop = False
    
        for arg in command:
            if next_is_vop:
                vop += ',%s' % arg
                next_is_vop = False
            elif (arg == '-vop' or arg == '-vf'):
                next_is_vop=True
            else:
                ret += [ arg ]

        if vop:
            if self.version >= 1:
                return ret + [ '-vf', vop[1:] ]
            return ret + [ '-vop', vop[1:] ]
        return ret



# ======================================================================

import osd

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, (app, mplayer, item, network_play)):
        # DVD items also store mplayer_audio_broken to check if you can
        # start them with -alang or not
        if hasattr(item, 'mplayer_audio_broken') or item.mode != 'dvd':
            self.check_audio = 0
        else:
            self.check_audio = 1

        self.network_play = network_play
        self.RE_TIME      = re.compile("^A: *([0-9]+)").match
        self.RE_START     = re.compile("^Starting playback\.\.\.").match
        self.RE_EXIT      = re.compile("^Exiting\.\.\. \((.*)\)$").match
        self.item         = item
        self.mplayer      = mplayer
        self.exit_type    = None
        self.osd          = osd.get_singleton()
        self.osdfont      = self.osd.getfont(config.OSD_DEFAULT_FONTNAME,
                                             config.OSD_DEFAULT_FONTSIZE)

        # check for mplayer plugins
        self.stdout_plugins  = []
        self.elapsed_plugins = []
        for p in plugin.get('mplayer_video'):
            if hasattr(p, 'stdout'):
                self.stdout_plugins.append(p)
            if hasattr(p, 'elapsed'):
                self.elapsed_plugins.append(p)

        # init the child (== start the threads)
        childapp.ChildApp.__init__(self, app)


                
    def stopped(self):
        if self.exit_type == "End of file":
            rc.post_event(PLAY_END)
        elif self.exit_type == "Quit":
            rc.post_event(USER_END)
        else:
            print _( 'ERROR' ) + ': ' + _( 'unknow error while playing file' )
            rc.post_event(PLAY_END)
                        

    def stdout_cb(self, line):
        """
        parse the stdout of the mplayer process
        """
        # show connection status for network play
        if self.network_play:
            if line.find('Opening audio decoder') == 0:
                self.osd.clearscreen(self.osd.COL_BLACK)
                self.osd.update()
            elif (line.find('Resolving ') == 0 or line.find('Connecting to server') == 0 or \
                  line.find('Cache fill:') == 0) and \
                  line.find('Resolving reference to') == -1:
                if line.find('Connecting to server') == 0:
                    line = 'Connecting to server'
                self.osd.clearscreen(self.osd.COL_BLACK)
                self.osd.drawstringframed(line, config.OSD_OVERSCAN_X+10, config.OSD_OVERSCAN_Y+10,
                                          self.osd.width - 2 * (config.OSD_OVERSCAN_X+10), -1,
                                          self.osdfont, self.osd.COL_WHITE)
                self.osd.update()


        # current elapsed time
        if line.find("A:") == 0:
            m = self.RE_TIME(line)
            if hasattr(m,'group'):
                self.item.elapsed = int(m.group(1))+1
                for p in self.elapsed_plugins:
                    p.elapsed(self.item.elapsed)


        # exit status
        elif line.find("Exiting...") == 0:
            m = self.RE_EXIT(line)
            if m:
                self.exit_type = m.group(1)


        # this is the first start of the movie, parse infos
        elif not self.item.elapsed:
            for p in self.stdout_plugins:
                p.stdout(line)
                
            if self.check_audio:
                if line.find('MPEG: No audio stream found -> no sound') == 0:
                    # OK, audio is broken, restart without -alang
                    self.check_audio = 2
                    self.item.mplayer_audio_broken = True
                    rc.post_event(Event('AUDIO_ERROR_START_AGAIN'))
                
                if self.RE_START(line):
                    if self.check_audio == 1:
                        # audio seems to be ok
                        self.item.mplayer_audio_broken = False
                    self.check_audio = 0



    def stderr_cb(self, line):
        """
        parse the stderr of the mplayer process
        """
        for p in self.stdout_plugins:
            p.stdout(line)
