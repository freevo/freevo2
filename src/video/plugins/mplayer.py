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
# Revision 1.12  2003/08/23 10:07:18  dischi
# restore the context
#
# Revision 1.11  2003/08/22 17:51:29  dischi
# Some changes to make freevo work when installed into the system
#
# Revision 1.10  2003/08/20 19:01:16  dischi
# added dga support and STOP_OSD_WHEN_PLAYING to shutdown down osd
#
# Revision 1.9  2003/08/06 19:32:40  dischi
# removed freevo_xwin support. Most users have problems with it and it works without it
#
# Revision 1.8  2003/08/05 17:25:58  dischi
# fixed event name
#
# Revision 1.7  2003/08/02 16:21:40  dischi
# add MPLAYER_AUTOCROP
#
# Revision 1.6  2003/07/27 17:12:37  dischi
# exception handling
#
# Revision 1.5  2003/07/11 19:47:08  dischi
# close file after parsing
#
# Revision 1.4  2003/07/06 20:21:10  outlyer
# Removed more debug statements and extraneous log messages.
#
# Revision 1.3  2003/07/01 21:47:35  outlyer
# Made a check to see if file exists before unlinking.
#
# Revision 1.2  2003/07/01 20:35:58  outlyer
# Replaced the os.system('rm ...') calls with os.unlink()
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
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.

from event import *
import plugin

# RegExp
import re

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()

# contains an initialized MPlayer() object
mplayer = None

class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the video player. Use mplayer to play all video
    files.
    """
    def __init__(self):
        global mplayer
        # create the mplayer object
        plugin.Plugin.__init__(self)
        mplayer = util.SynchronizedObject(MPlayer())

        # register it as the object to play audio
        plugin.register(mplayer, plugin.VIDEO_PLAYER)


def vop_append(command):
    """
    Change a mplayer command to support more than one -vop
    parameter. This function will grep all -vop parameter from
    the command and add it at the end as one vop argument
    """
    ret = ''
    vop = ''
    next_is_vop = FALSE
    
    for arg in command.split(' '):
        if next_is_vop:
            vop += ',%s' % arg
            next_is_vop = FALSE
        elif arg == '-vop':
            next_is_vop=TRUE
        else:
            ret += '%s ' % arg

    if vop:
        return '%s -vop %s' % (ret,vop[1:])
    return ret


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
        self.filename = None
        self.app_mode = 'video'
        self.seek = 0
        self.seek_timer = threading.Timer(0, self.reset_seek)
                         
    def play(self, filename, options, item, mode = None):
        """
        play a audioitem with mplayer
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

        if DEBUG:
            print 'MPlayer.play(): mode=%s, filename=%s' % (mode, filename)

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

        elif mode == 'dvdnav':
            additional_args = '-alang %s' % config.DVD_LANG_PREF

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
            
        command = mpl + ' "' + filename + '"'

        if config.MPLAYER_AUTOCROP and command.find('crop=') == -1:
            (x1, y1, x2, y2) = (1000, 1000, 0, 0)
            child = popen2.Popen3(vop_append('%s -ao null -vo null ' \
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


        command=vop_append(command)

        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.file = item
        self.thread.play_mode = self.mode
        self.thread.item  = item
        self.item  = item
         
        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
        rc.app(self)

        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.app.write('quit\n')
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        self.thread.item = None
        rc.app(None)
        while self.thread.mode == 'stop':
            time.sleep(0.3)
            

    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if event == VIDEO_MANUAL_SEEK:
            self.seek = 0
            rc.set_context('input')
            return TRUE
        
        if event.context == 'input':
            if event in INPUT_ALL_NUMBERS:
                self.reset_seek_timeout()
                self.seek = self.seek * 10 + int(event);
                return TRUE
            
            elif event == INPUT_ENTER:
                self.seek_timer.cancel()
                self.seek *= 60
                self.thread.app.write('seek ' + str(self.seek) + ' 2\n')
                if DEBUG: print "seek "+str(self.seek)+" 2\n"
                self.seek = 0
                rc.set_context('video')
                return TRUE

            elif event == INPUT_EXIT:
                if DEBUG: print 'seek stopped'
                self.seek_timer.cancel()
                self.seek = 0
                rc.set_context('video')
                return TRUE

        if event == STOP:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 6\n')
                return TRUE
            else:
                self.stop()
                return self.item.eventhandler(event)

        if event == 'AUDIO_ERROR_START_AGAIN':
            self.stop()
            self.play(self.parameter[0], self.parameter[1], self.parameter[2],
                      self.parameter[3])
            return TRUE
        
        if event == STORE_BOOKMARK:
            # Bookmark the current time into a file
            
            bookmarkfile = util.get_bookmarkfile(self.filename)
            
            handle = open(bookmarkfile,'a+') 
            handle.write(str(self.item.elapsed))
            handle.write('\n')
            handle.close()
            return TRUE

        if event in ( STOP, PLAY_END, USER_END, DVD_PROTECTED ):
            self.stop()
            return self.item.eventhandler(event)

        try:
            if event == VIDEO_SEND_MPLAYER_CMD:
                self.thread.app.write('%s\n' % event.arg)
                return TRUE

            if event == MENU:
                if self.mode == 'dvdnav':
                    self.thread.app.write('dvdnav 5\n')
                    return TRUE

            if event == TOGGLE_OSD:
                self.thread.app.write('osd\n')
                return TRUE

            if event == PAUSE or event == PLAY:
                self.thread.app.write('pause\n')
                return TRUE

            if event == SEEK:
                self.thread.app.write('seek %s\n' % event.arg)
                return TRUE
        except:
            print 'Exception while sending command to mplayer:'
            traceback.print_exc()
            return TRUE
        
        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)

    
    def reset_seek(self):
        if DEBUG: print 'seek timeout'
        self.seek = 0
        rc.set_context('video')
        
    def reset_seek_timeout(self):
        self.seek_timer.cancel()
        self.seek_timer = threading.Timer(config.MPLAYER_SEEK_TIMEOUT, self.reset_seek)
        self.seek_timer.start()
        

# ======================================================================

class MPlayerParser:
    """
    class to parse the mplayer output and store some information
    in the videoitem
    """
    
    def __init__(self, item):
        self.item = item
        self.RE_EXIT = re.compile("^Exiting\.\.\. \((.*)\)$").match
        self.RE_START = re.compile("^Starting playback\.\.\.").match

        # DVD items also store mplayer_audio_broken to check if you can
        # start them with -alang or not
        if hasattr(item, 'mplayer_audio_broken') or item.mode != 'dvd':
            self.check_audio = 0
        else:
            self.check_audio = 1
            
        
    def parse(self, line):
        if self.check_audio:
            if line.find('MPEG: No audio stream found -> no sound') == 0:
                # OK, audio is broken, restart without -alang
                self.check_audio = 2
                self.item.mplayer_audio_broken = TRUE
                rc.post_event(Event('AUDIO_ERROR_START_AGAIN'))
                
        if self.RE_START(line):
            if self.check_audio == 1:
                # audio seems to be ok
                self.item.mplayer_audio_broken = FALSE
            self.check_audio = 0
                
    def end_type(self, str):
        m = self.RE_EXIT(str)
        if m: return m.group(1)
        

class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, app, item):
        if config.MPLAYER_DEBUG:
            startdir = os.environ['FREEVO_STARTDIR']
            fname_out = os.path.join(startdir, 'mplayer_stdout.log')
            fname_err = os.path.join(startdir, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'a')
                self.log_stderr = open(fname_err, 'a')
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'MPlayer logging!') % (fname_out, fname_err))
                print 'Please set MPLAYER_DEBUG=0 in local_conf.py, or '
                print 'start Freevo from a directory that is writeable!'
                print
            else:
                print 'MPlayer logging to "%s" and "%s"' % (fname_out, fname_err)

        self.RE_TIME = re.compile("^A: *([0-9]+)").match
        self.item = item
        self.parser = MPlayerParser(item)
        childapp.ChildApp.__init__(self, app)
        self.exit_type = None
        
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)

        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing mplayer'

        if config.MPLAYER_DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()

    def stdout_cb(self, line):

        if config.MPLAYER_DEBUG:
            try:
                self.log_stdout.write(line + '\n')
            except ValueError:
                pass # File closed
                     
        if line.find("A:") == 0:
            m = self.RE_TIME(line) # Convert decimal
            if hasattr(m,'group'):
                self.item.elapsed = int(m.group(1))+1

        elif line.find("Exiting...") == 0:
            self.exit_type = self.parser.end_type(line)

        # this is the first start of the movie, parse infos
        elif not self.item.elapsed:
            self.parser.parse(line)


    def stderr_cb(self, line):
        if line.find('The DVD is protected') != -1:
            print
            print 'WARNING: You are trying to play a protected (CSS) DVD!'
            print 'DVD protection is normally enabled, please see the docs'
            print 'for more information.'
            print
            rc.post_event(DVD_PROTECTED)
            
        if config.MPLAYER_DEBUG:
            try:
                self.log_stderr.write(line + '\n')
            except ValueError:
                pass # File closed
                     

# ======================================================================

class MPlayer_Thread(threading.Thread):
    """
    Thread to wait for a mplayer command to play
    """

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.play_mode = ''
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.item  = None

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                if config.STOP_OSD_WHEN_PLAYING:
                    osd.stopdisplay()			
               
                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    if self.app.exit_type == "End of file":
                        rc.post_event(PLAY_END)
                    elif self.app.exit_type == "Quit":
                        rc.post_event(USER_END)
                    else:
                        print 'error while playing file'
                        rc.post_event(PLAY_END)
                        
                # Ok, we can use the OSD again.
                if config.STOP_OSD_WHEN_PLAYING:
                    osd.restartdisplay()
                    osd.update()
                
                self.mode = 'idle'
                
            else:
                self.mode = 'idle'


