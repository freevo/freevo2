#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer module for video
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Perhaps we should move the filetype specific stuff (like the one for vob)
# into the config files...
#
# i.e.
#
# MP_CUSTOM = {
#     '.vob' = '-ac hwac3 ...',
#     '.rm'  = '-forceidx',
#     ...
#     }
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.36  2003/10/21 21:17:42  gsbarbieri
# Some more i18n improvements.
#
# Revision 1.35  2003/10/20 13:36:42  outlyer
# Remove double-quit
#
# Revision 1.34  2003/10/19 09:51:41  dischi
# move from str command to list, resort some stuff
#
# Revision 1.33  2003/10/17 21:30:02  rshortt
# We need self.osdfont set before calling childapp's init.  This was crashing
# for me on network play.
#
# Revision 1.32  2003/10/14 16:58:48  dischi
# fix mode detection, MPLAYER_ARGS never worked
#
# Revision 1.31  2003/10/08 02:04:04  outlyer
# BUGFIX: For some reason, I was seeing a lot of 'killing with signal 9' in
# my log files when I played certain video files. Adding the 'double' quit here
# seems to cause it to quit cleanly, and immediately instead of an annoying
# two seconds later.
#
# Revision 1.30  2003/10/04 14:38:10  dischi
# Try to auto-correct av sync problems. Set MPLAYER_SET_AUDIO_DELAY to
# enable it. You need mmpython > 0.2 to make it work.
#
# Revision 1.29  2003/10/02 10:24:33  dischi
# bmovl update
#
# Revision 1.28  2003/10/01 22:30:10  dischi
# some bmovl fixes, you must use software scale with expand to make it work
#
# Revision 1.27  2003/10/01 20:39:34  dischi
# bmovl support
#
# Revision 1.24  2003/09/20 17:03:20  dischi
# draw status while connecting and caching for network files
#
# Revision 1.23  2003/09/19 22:09:15  dischi
# use new childapp thread function
#
# Revision 1.22  2003/09/18 17:09:54  gsbarbieri
# Faster version detection + handle for CVS versions.
#
# Revision 1.21  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.20  2003/09/03 17:54:38  dischi
# Put logfiles into LOGDIR not $FREEVO_STARTDIR because this variable
# doesn't exist anymore.
#
# Revision 1.19  2003/09/02 19:10:22  dischi
# Basic mplayer version detection. Convert -vop to -vf if cvs or 1.0pre1
# is used
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

import osd
from osd import OSD
osd = osd.get_singleton()

import skin
import pygame

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the video player.

    With this plugin Freevo can play all video files defined in
    SUFFIX_VIDEO_FILES. This is the default video player for Freevo.
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
        plugin.register(mplayer, plugin.VIDEO_PLAYER)


class OSDbmovl(OSD):
    """
    an OSD class for bmovl
    """
    def __init__(self, width, height):
        self.width  = width
        self.height = height
        self.depth  = 32
        self.screen = pygame.Surface((width, height), SRCALPHA)

        # clear surface
        self.screen.fill((0,0,0,0))

        self.bmovl  = os.open('/tmp/bmovl', os.O_WRONLY)


    def close(self):
        os.close(self.bmovl)

        
    def show(self):
        os.write(self.bmovl, 'SHOW\n')
        

    def hide(self):
        os.write(self.bmovl, 'HIDE\n')
        

    def clearscreen(self, color=None):
        self.screen.fill((0,0,0,0))
        os.write(self.bmovl, 'CLEAR %s %s %s %s' % (self.width, self.height, 0, 0))

        
    def update(self, rect):
        _debug_('update bmovl')
        update = self.screen.subsurface(rect)
        os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
                 (update.get_width(), update.get_height(), rect[0], rect[1], 0, 0))
        os.write(self.bmovl, pygame.image.tostring(update, 'RGBA'))


        
class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self, version):
        self.thread = childapp.ChildThread()
        self.thread.stop_osd = True

        self.mode = None
        self.filename = None
        self.app_mode = 'video'
        self.version = version
        self.seek = 0
        self.seek_timer = threading.Timer(0, self.reset_seek)

        
    def play(self, filename, options, item, mode = None):
        """
        play a videoitem with mplayer
        """

        self.parameter = (filename, options, item, mode)
        
        if not mode:
            mode = item.mode

        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0
           
        self.filename = filename

        self.mode = mode   # setting global var to mode.

        _debug_('MPlayer.play(): mode=%s, filename=%s' % (mode, filename))

        if mode == 'file' and not os.path.isfile(filename) and not network_play:
            # This event allows the videoitem which contains subitems to
            # try to play the next subitem
            return '%s\nnot found' % os.path.basename(filename)
       

        # Build the MPlayer command
        mpl = '--prio=%s %s %s -slave -ao %s' % (config.MPLAYER_NICE,
                                                 config.MPLAYER_CMD,
                                                 config.MPLAYER_ARGS_DEF,
                                                 config.MPLAYER_AO_DEV)

        additional_args = ''

        if mode == 'file':
            try:
                mode = os.path.splitext(filename)[1]
                mode = mode[1:]
            except:
                pass

        elif mode == 'vcd':
            # Filename is VCD title
            filename = 'vcd://%s' % filename  

        elif mode == 'dvd':
            # Filename is DVD title
            filename = 'dvd://%s' % filename  

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

        else:
            print "Don't know what do play!"
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            return 'Unknown media: %s' % os.path.basename(filename)

        if not config.MPLAYER_ARGS.has_key(mode):
            mode = 'default'

        # Mplayer command and standard arguments
        mpl += (' -v -vo ' + config.MPLAYER_VO_DEV + config.MPLAYER_VO_DEV_OPTS + \
                ' ' + config.MPLAYER_ARGS[mode])

        mpl = mpl.split(' ') + [ filename ] + additional_args.split(' ')

        if options:
            mpl += options.split(' ')

        # use software scaler?
        if '-nosws' in mpl:
            mpl.remove('-nosws')
        elif not '-framedrop' in mpl:
            mpl += config.MPLAYER_SOFTWARE_SCALER.split(' ')
            
        if os.path.exists('/tmp/bmovl') and config.MPLAYER_SOFTWARE_SCALER:
            mpl += ('-vf', 'bmovl=1:0:/tmp/bmovl')

        if config.MPLAYER_SET_AUDIO_DELAY and item.info.has_key('delay') and \
               item.info['delay'] > 0:
            mpl += ('-mc', str(int(item.info['delay'])+1), '-delay',
                    str(item.info['delay']))

        command = mpl

        while '' in command:
            command.remove('')

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

        command=self.vop_append(command)

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.file        = item
        self.osd_visible = False
        self.item        = item
        self.bmovl       = None

        rc.app(self)

        self.thread.start(MPlayerApp, (command, self, item, network_play))
        _debug_('MPlayer.play(): Starting thread, cmd=%s' % command)

        return None
    

    def show_osd(self):
        """
        bmovl: init bmovl osd and show it
        """
        _debug_('show osd')

        height = config.OVERSCAN_Y + 60
        if not skin.get_singleton().settings.images.has_key('background'):
            _debug_('no background')
            return
        
        bg = self.bmovl.loadbitmap(skin.get_singleton().settings.images['background'])
        bg = pygame.transform.scale(bg, (self.bmovl.width, self.bmovl.height))

        self.bmovl.screen.blit(bg, (0,0))

        # bar at the top:
        self.bmovl.drawbox(0, height-1, osd.width, height-1, width=1, color=0x000000)

        clock       = time.strftime('%a %I:%M %P')
        clock_font  = skin.get_singleton().GetFont('clock')
        clock_width = clock_font.font.stringsize(clock)
        
        self.bmovl.drawstringframed(clock, self.bmovl.width-config.OVERSCAN_X-10-clock_width,
                                    config.OVERSCAN_Y+10, clock_width, -1,
                                    clock_font.font, clock_font.color)

        self.bmovl.update((0, 0, self.bmovl.width, height))

        # bar at the bottom
        height += 40
        x0      = config.OVERSCAN_X+10
        y0      = self.bmovl.height + 5 - height
        width   = self.bmovl.width - 2 * config.OVERSCAN_X
        
        self.bmovl.drawbox(0, self.bmovl.height + 1 - height, self.bmovl.width,
                           self.bmovl.height + 1 - height, width=1, color=0x000000)

        if self.item.image:
            image = pygame.transform.scale(self.bmovl.loadbitmap(self.item.image), (65, 90))
            self.bmovl.screen.blit(image, (x0, y0))
            x0    += image.get_width() + 10
            width -= image.get_width() + 10
            
        title   = self.item.name
        tagline = self.item.getattr('tagline')

        if self.item.tv_show:
            show    = config.TV_SHOW_REGEXP_SPLIT(self.item.name)
            title   = show[0] + " " + show[1] + "x" + show[2]
            tagline = show[3]
        
        title_font   = skin.get_singleton().GetFont('title')
        tagline_font = skin.get_singleton().GetFont('info tagline')

        pos = self.bmovl.drawstringframed(title, x0, y0, width, -1, title_font.font,
                                          title_font.color)
        if tagline:
            self.bmovl.drawstringframed(tagline, x0, pos[1][3]+5, width, -1,
                                        tagline_font.font, tagline_font.color)
            
        self.bmovl.update((0, self.bmovl.height-height, self.bmovl.width, height))

        # and show it
        self.bmovl.show()


    def hide_osd(self):
        """
        bmovl: hide osd
        """
        _debug_('hide')
        self.thread.app.refresh = None
        self.bmovl.clearscreen()
        self.bmovl.hide()
        
        
    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.stop('quit\n')
        rc.app(None)
        if self.bmovl:
            self.bmovl.close()
            self.bmovl = None


    def eventhandler(self, event, menuw=None):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

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
            self.play(self.parameter[0], self.parameter[1], self.parameter[2],
                      self.parameter[3])
            return True
        
        if event in ( PLAY_END, USER_END ):
            self.stop()
            return self.item.eventhandler(event)

        if event == TOGGLE_OSD and self.bmovl:
            if self.osd_visible:
                self.thread.app.write('osd 1\n')
                self.hide_osd()
            else:
                self.show_osd()
                self.thread.app.write('osd 3\n')
            self.osd_visible = not self.osd_visible
            return True

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

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, (app, mplayer, item, network_play)):
        if config.MPLAYER_DEBUG:
            fname_out = os.path.join(config.LOGDIR, 'mplayer_stdout.log')
            fname_err = os.path.join(config.LOGDIR, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'w')
                self.log_stderr = open(fname_err, 'w')
                print _( 'MPlayer logging to "%s" and "%s"' ) % (fname_out, fname_err)
            except IOError:
                print
                print ( _('ERROR') + ': ' + _('Cannot open "%s" and "%s" for ' \
                                              'MPlayer logging!')
                        ) % (fname_out, fname_err)
                config.MPLAYER_DEBUG = 0
                
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
        self.osdfont      = osd.getfont(config.OSD_DEFAULT_FONTNAME,
                                        config.OSD_DEFAULT_FONTSIZE)

        childapp.ChildApp.__init__(self, app)

        self.exit_type = None

        self.use_bmovl = False
        pos = 0
        if '-vop' in app:
            pos = app.index('-vop')
        if '-vf' in app:
            pos = app.index('-vf')
        if pos and app[pos+1].find('/tmp/bmovl') > 0:
            print 'Found /tmp/bmovl, activating experimental bmovl support'
            self.use_bmovl = True

        
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)
        _debug_('Killing mplayer')

        if config.MPLAYER_DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()


    def stopped(self):
        if self.exit_type == "End of file":
            rc.post_event(PLAY_END)
        elif self.exit_type == "Quit":
            rc.post_event(USER_END)
        else:
            print _( 'ERROR' ) + ': ' + _( 'unknow error while playing file' )
            rc.post_event(PLAY_END)
                        

    def stdout_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stdout.write(line + '\n')
            except ValueError:
                pass # File closed

        if self.network_play:
            if line.find('Opening audio decoder') == 0:
                osd.clearscreen(osd.COL_BLACK)
                osd.update()
            elif (line.find('Resolving ') == 0 or line.find('Connecting to server') == 0 or \
                  line.find('Cache fill:') == 0) and \
                  line.find('Resolving reference to') == -1:
                if line.find('Connecting to server') == 0:
                    line = 'Connecting to server'
                osd.clearscreen(osd.COL_BLACK)
                osd.drawstringframed(line, config.OVERSCAN_X, config.OVERSCAN_Y,
                                     osd.width - 2 * config.OVERSCAN_X, -1, self.osdfont,
                                     osd.COL_WHITE)
                osd.update()

        # experimental for bmovl, may crash
        try:
            if line.find('SwScaler:') ==0 and line.find(' -> ') > 0 and \
                   line[line.find(' -> '):].find('x') > 0 and self.use_bmovl:
                width, height = line[line.find(' -> ')+4:].split('x')
                self.mplayer.bmovl = OSDbmovl(int(width), int(height))
                self.use_bmovl = False
            if line.find('Expand: ') == 0 and self.use_bmovl:
                width, height = line[7:line.find(',')].split('x')
                self.mplayer.bmovl = OSDbmovl(int(width), int(height))
                self.use_bmovl = False
        except:
            pass
        
        if line.find("A:") == 0:
            m = self.RE_TIME(line) # Convert decimal
            if hasattr(m,'group'):
                self.item.elapsed = int(m.group(1))+1
                    
        elif line.find("Exiting...") == 0:
            m = self.RE_EXIT(line)
            if m:
                self.exit_type = m.group(1)

        # this is the first start of the movie, parse infos
        elif not self.item.elapsed:
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
        if config.MPLAYER_DEBUG:
            try:
                self.log_stderr.write(line + '\n')
            except ValueError:
                pass # File closed
