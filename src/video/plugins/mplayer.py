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
osd = osd.get_singleton()
import skin
import pygame

# contains an initialized MPlayer() object
mplayer = None

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the video player.

    With this plugin Freevo can play all video files defined in
    SUFFIX_VIDEO_FILES. This is the default video player for Freevo.
    """
    def __init__(self):
        global mplayer

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
        mpl += (' ' + config.MPLAYER_ARGS[mode] + ' ' + additional_args + \
                ' -v -vo ' + config.MPLAYER_VO_DEV + config.MPLAYER_VO_DEV_OPTS)

        if options:
            mpl += (' ' + options)

        # use software scaler?
        if mpl.find(' -nosws ') > 0:
            mpl = (mpl[:mpl.find(' -nosws ')] + mpl[mpl.find(' -nosws ')+7:])
        elif mpl.find(' -framedrop ') == -1 and mpl.find(' -framedrop ') == -1:
            mpl += (' ' + config.MPLAYER_SOFTWARE_SCALER )
            
        if os.path.exists('/tmp/bmovl') and config.MPLAYER_SOFTWARE_SCALER:
            mpl += ' -vf bmovl=1:0:/tmp/bmovl'

        command = mpl + ' "' + filename + '"'

        if config.MPLAYER_AUTOCROP and command.find('crop=') == -1:
            (x1, y1, x2, y2) = (1000, 1000, 0, 0)
            child = popen2.Popen3(self.vop_append('%s -ao null -vo null ' \
                                                  '-ss 60 -frames 20 -vop cropdetect' % \
                                                  command), 1, 100)
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
                command = '%s -vop crop=%s:%s:%s:%s' % (command, x2-x1, y2-y1, x1, y1)
            
            child.wait()


        command=self.vop_append(command)

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.file = item

        self.bmovl = None
        rc.app(self)

        self.thread.start(MPlayerApp, (command, item, network_play))

        self.item  = item

        _debug_('MPlayer.play(): Starting thread, cmd=%s' % command)

        # bmovl support?
        if os.path.exists('/tmp/bmovl') and config.MPLAYER_SOFTWARE_SCALER:
            # show warning until this code is stable
            print 'Found /tmp/bmovl, activating experimental bmovl support'
            # BUG: if mplayer doesn't start because of bad a command line
            # this will cause Freevo to wait forever
            self.bmovl = os.open('/tmp/bmovl', os.O_WRONLY)
            self.osd_visible = False
        return None
    

    def update_osd(self):
        """
        bmovl: update elapsed time and current time
        """
        s = self.osd_bg.convert()
        length = self.item.elapsed

        txt = '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60, length % 60)
        length = self.item.getattr('length')

        if length:
            txt = '%s / %s' % (txt, length)

        osd.drawstringframed(txt, 10, 10, osd.width / 2, -1, self.osd_font.font,
                             self.osd_font.color, layer=s)

        clock = time.strftime('%a %I:%M %P')
        osd.drawstringframed(clock, s.get_width()-10-self.osd_font.font.stringsize(clock),
                             10, osd.width / 2, -1, self.osd_font.font,
                             self.osd_font.color, layer=s)

        bottom_space = (osd.height - self.thread.app.height) / 2
        if bottom_space > s.get_height():
            _debug_('enough space to draw on screen via osd.py')
            osd.screen.blit(s, (0, osd.height-s.get_height()))
            osd.update()
        else:
            _debug_('write on mplayer via bmovl (%s)' % bottom_space)
            os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
                     (s.get_width(), s.get_height(), 0,
                      self.thread.app.height-s.get_height(), 0, 0))
            os.write(self.bmovl, pygame.image.tostring(s, 'RGBA'))

    
    def show_osd(self):
        """
        bmovl: init bmovl osd and show it
        """
        _debug_('show osd')

        if not self.item.elapsed:
            _debug_('not ready')
            return
        
        height = config.OVERSCAN_Y + 100
        if not skin.get_singleton().settings.images.has_key('background'):
            _debug_('no background')
            return
        
        bg = osd.loadbitmap(skin.get_singleton().settings.images['background'])
        bg = pygame.transform.scale(bg, (osd.width, osd.height))

        font = skin.get_singleton().GetFont('title')
        font_tagline = skin.get_singleton().GetFont('info tagline')
        
        topbar = bg.subsurface((0,0,osd.width,height)).convert()
        osd.drawbox(0, height-1, osd.width, height-1, width=1, color=0x000000, layer=topbar)

        title   = self.item.name
        tagline = self.item.getattr('tagline')

        if self.item.tv_show:
            show    = config.TV_SHOW_REGEXP_SPLIT(self.item.name)
            title   = show[0] + " " + show[1] + "x" + show[2]
            tagline = show[3]
        
        pos = osd.drawstringframed(title, 10, 10, osd.width-config.OVERSCAN_X-130,
                                   -1, font.font, font.color, layer=topbar)
        if tagline:
            osd.drawstringframed(tagline, 10, pos[1][3]+5,
                                 osd.width-config.OVERSCAN_X-130, -1,
                                 font_tagline.font, font_tagline.color, layer=topbar)

        if self.item.image:
            image = pygame.transform.scale(osd.loadbitmap(self.item.image), (65, 90))
            topbar.blit(image, (osd.width-config.OVERSCAN_X-100, config.OVERSCAN_Y+5))

        if self.thread.app.height < osd.height:
            topspace = (osd.height - self.thread.app.height) / 2
            osd.screen.blit(topbar, (0,0))
            topbar = topbar.subsurface(0, topspace, topbar.get_width(),
                                       topbar.get_height()-topspace)
            
        os.write(self.bmovl, 'RGBA32 %d %d %d %d %d %d\n' % \
                 (topbar.get_width(), topbar.get_height(), 0, 0, 0, 1))
        os.write(self.bmovl, pygame.image.tostring(topbar, 'RGBA'))

        height -= 50
        self.osd_bg   = bg.subsurface((0,osd.height-height,osd.width,height)).convert()
        osd.drawbox(0, 0, osd.width, 0, width=1, color=0x000000, layer=self.osd_bg)
        self.osd_font = skin.get_singleton().GetFont('clock')

        self.update_osd()
        self.thread.app.refresh = self.update_osd
        os.write(self.bmovl, 'SHOW\n')


    def hide_osd(self):
        """
        bmovl: hide osd
        """
        _debug_('hide')
        self.thread.app.refresh = None
        os.write(self.bmovl, 'HIDE\n')
        osd.clearscreen(osd.COL_BLACK)
        osd.update()
        
        
    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.stop('quit\n')
        rc.app(None)
        if self.bmovl:
            os.close(self.bmovl)
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
                self.hide_osd()
            else:
                self.show_osd()
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
        ret = ''
        vop = ''
        next_is_vop = False
    
        for arg in command.split(' '):
            if next_is_vop:
                vop += ',%s' % arg
                next_is_vop = False
            elif (arg == '-vop' or arg == '-vf'):
                next_is_vop=True
            else:
                ret += '%s ' % arg

        if vop:
            if self.version >= 1:
                return '%s -vf %s' % (ret,vop[1:])
            return '%s -vop %s' % (ret,vop[1:])
        return ret



# ======================================================================

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, (app, item, network_play)):
        if config.MPLAYER_DEBUG:
            fname_out = os.path.join(config.LOGDIR, 'mplayer_stdout.log')
            fname_err = os.path.join(config.LOGDIR, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'w')
                self.log_stderr = open(fname_err, 'w')
                print 'MPlayer logging to "%s" and "%s"' % (fname_out, fname_err)
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'MPlayer logging!') % (fname_out, fname_err))
                config.MPLAYER_DEBUG = 0
                
        # DVD items also store mplayer_audio_broken to check if you can
        # start them with -alang or not
        if hasattr(item, 'mplayer_audio_broken') or item.mode != 'dvd':
            self.check_audio = 0
        else:
            self.check_audio = 1

        self.network_play = network_play
        self.RE_TIME = re.compile("^A: *([0-9]+)").match
        self.RE_START = re.compile("^Starting playback\.\.\.").match
        self.RE_EXIT = re.compile("^Exiting\.\.\. \((.*)\)$").match
        self.item = item
        childapp.ChildApp.__init__(self, app)
        self.exit_type = None
        self.osdfont = osd.getfont(config.OSD_DEFAULT_FONTNAME, config.OSD_DEFAULT_FONTSIZE)
        self.refresh = None
        self.width   = 0
        self.height  = 0
        
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
            print 'error while playing file'
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
                   line[line.find(' -> '):].find('x') > 0 and not self.width:
                self.width, self.height = line[line.find(' -> ')+4:].split('x')
                self.width  = int(self.width)
                self.height = int(self.height)
            if line.find('Expand: ') == 0:
                self.width, self.height = line[7:line.find(',')].split('x')
                self.width  = int(self.width)
                self.height = int(self.height)
        except:
            pass
        
        if line.find("A:") == 0:
            m = self.RE_TIME(line) # Convert decimal
            if hasattr(m,'group'):
                t = self.item.elapsed
                self.item.elapsed = int(m.group(1))+1
                if t != self.item.elapsed and self.refresh:
                    self.refresh()
                    
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
