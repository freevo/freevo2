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
# Revision 1.27  2003/03/17 18:54:44  outlyer
# Some changes for the bookmarks
#     o videoitem.py - Added bookmark menu, bookmark "parser" and menu generation,
#             haven't figured out how to pass the timecode to mplayer though. I tried
#             setting mplayer_options, but self.play seems to just ignore them. I don't
#             know how to pass anything to self.play either. ARGH.
#     o mplayer.py - commented out two extraneous prints.
#
# Revision 1.26  2003/03/17 16:34:33  outlyer
# Added preliminary movie bookmarks (i.e. places to jump to on next play)
# Currently only writing the bookmarks does anything; I'm going to have to
# add a menu of bookmarks to the menu afterwards.
#
# Note that the get_bookmarkfile thing should be replaced with something less
# flaky than the path+filename of the movie, but this is good for a initial
# go.
#
# Revision 1.25  2003/03/17 15:47:16  outlyer
# Merged patch from Angel <angel@knight-industries.com> for "Jump to"
# functionality.
#
# Revision 1.24  2003/03/02 14:58:23  dischi
# Removed osd.clearscreen and if we have the NEW_SKIN deactivate
# skin.popupbox, refresh, etc. Use menuw.show and menuw.hide to do this.
#
# Revision 1.23  2003/02/24 21:13:18  dischi
# Moved RC_MPLAYER_CMDS higher in the eventhandler
#
# Revision 1.22  2003/02/24 04:21:40  krister
# Mathieu Weber's bugfix for multipart movies
#
# Revision 1.21  2003/02/22 07:13:19  krister
# Set all sub threads to daemons so that they die automatically if the main thread dies.
#
# Revision 1.20  2003/02/19 17:20:21  outlyer
# Added 'rc.func' to video; probably should add one to the image viewer
# too so we don't draw over it. Just remember if you set it, you have to
# set it back so the idletool restarts.
#
# Revision 1.19  2003/02/11 06:10:03  krister
# Display an error if the DVD is protected and cannot be played.
#
# Revision 1.18  2003/02/11 04:37:29  krister
# Added an empty local_conf.py template for new users. It is now an error if freevo_config.py is found in /etc/freevo etc. Changed DVD protection to use a flag. MPlayer stores debug logs in FREEVO_STARTDIR, and stops with an error if they cannot be written.
#
# Revision 1.17  2003/02/06 09:52:26  krister
# Changed the runtime handling to use runapp to start programs with the supplied dlls
#
# Revision 1.16  2003/02/04 13:11:00  dischi
# remove the AC3 config stuff and reformat some lines to 80 chars/line
#
# Revision 1.15  2003/01/29 17:20:25  outlyer
# According to the mplayer documentation, -forceidx is required for RealPlayer
# files...
#
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
# Revision 1.14  2003/01/22 01:49:30  krister
# Fixed typo.
#
# Revision 1.13  2003/01/18 15:51:07  dischi
# Add the function vop_append to support more than one -vop argument for
# mplayer (from different mplayer_options sources). All -vop args will
# be appended at the end of the command as one argument.
#
# Revision 1.12  2003/01/11 10:55:57  dischi
# Call refresh with reload=1 when the menu was disabled during playback
#
# Revision 1.11  2002/12/30 15:07:42  dischi
# Small but important changes to the remote control. There is a new variable
# RC_MPLAYER_CMDS to specify mplayer commands for a remote. You can also set
# the variable REMOTE to a file in rc_clients to contain settings for a
# remote. The only one right now is realmagic, feel free to add more.
# RC_MPLAYER_CMDS uses the slave commands from mplayer, src/video/mplayer.py
# now uses -slave and not the key bindings.
#
# Revision 1.10  2002/12/29 19:24:26  dischi
# Integrated two small fixes from Jens Axboe to support overscan for DXR3
# and to set MPLAYER_VO_OPTS
#
# Revision 1.9  2002/12/22 12:23:30  dischi
# Added deinterlacing in the config menu
#
# Revision 1.8  2002/12/21 17:26:52  dischi
# Added dfbmga support. This includes configure option, some special
# settings for mplayer and extra overscan variables
#
# Revision 1.7  2002/12/18 05:00:31  krister
# DVD language config re-added.
#
# Revision 1.6  2002/12/11 20:46:43  dischi
# mplayer can check the mov by itself now (0.90-rc1)
#
# Revision 1.5  2002/12/03 20:01:53  dischi
# improved dvdnav support
#
# Revision 1.4  2002/12/01 20:53:03  dischi
# Added better support for mov files. This _only_ works with the mplayer
# CVS for now
#
# Revision 1.3  2002/11/26 22:02:10  dischi
# Added key to enable/disable subtitles. This works only with mplayer pre10
# (maybe pre9). Keyboard: l (for language) or remote SUBTITLE
#
# Revision 1.2  2002/11/26 20:58:44  dischi
# o Fixed bug that not only the first character of mplayer_options is used
# o added the configure stuff again (without play from stopped position
#   because the mplayer -ss option is _very_ broken)
# o Various fixes in DVD playpack
#
# Revision 1.1  2002/11/24 13:58:45  dischi
# code cleanup
#
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


import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import mixer      # Controls the volumes for playback and recording
import osd        # The OSD class, used to communicate with the OSD daemon
import rc         # The RemoteControl class.
import fnmatch

if not config.NEW_SKIN:
    import menu
    import skin

    menuwidget = menu.get_singleton()
    skin       = skin.get_singleton()


# RegExp
import re

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# Setting up the default objects:
osd        = osd.get_singleton()
rc         = rc.get_singleton()
mixer      = mixer.get_singleton()

# Module variable that contains an initialized MPlayer() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPlayer()
        
    return _singleton


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

                         
    def play(self, filename, options, item, mode = None):
        """
        play a audioitem with mplayer
        """

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
            if not config.NEW_SKIN:
                skin.PopupBox('%s\nnot found!' % os.path.basename(filename))
                time.sleep(2.0) 
                menuwidget.refresh()

            # XXX We should really use return more.
            return 0
       

        # Build the MPlayer command
        mpl = '--prio=%s %s %s -slave -ao %s' % (config.MPLAYER_NICE,
                                                 config.MPLAYER_CMD,
                                                 config.MPLAYER_ARGS_DEF,
                                                 config.MPLAYER_AO_DEV)

	# Forceidx is required for RealAudio/Video files
	if (os.path.splitext(filename)[1] == '.rm'):
	    mpl += ' -forceidx'

        if mode == 'file':
            default_args = config.MPLAYER_ARGS_MPG
        elif mode == 'dvdnav':
            default_args = config.MPLAYER_ARGS_DVDNAV
            default_args += ' -alang %s' % config.DVD_LANG_PREF
        elif mode == 'vcd':
            # Filename is VCD chapter
            default_args = config.MPLAYER_ARGS_VCD % filename  
        elif mode == 'dvd':
            # Filename is DVD title
            default_args = config.MPLAYER_ARGS_DVD % filename  
            default_args += ' -alang %s' % config.DVD_LANG_PREF
            if config.DVD_SUBTITLE_PREF:
                # Only use if defined since it will always turn on subtitles
                # if defined
                default_args += ' -slang %s' % config.DVD_SUBTITLE_PREF
        else:
            print "Don't know what do play!"
            print "What is:      " + str(filename)
            print "What is mode: " + mode
            print "What is:      " + mpl
            return

        # Mplayer command and standard arguments
        mpl += (' ' + default_args + ' -v -vo ' + config.MPLAYER_VO_DEV + \
                config.MPLAYER_VO_DEV_OPTS)
            
        # XXX Some testcode by Krister:
        if (os.path.isfile('./freevo_xwin') and osd.sdl_driver == 'x11' and 
            config.MPLAYER_USE_WID):
            if DEBUG: print 'Got freevo_xwin and x11'
            os.system('rm -f /tmp/freevo.wid')
            os.system('./runapp ./freevo_xwin  0 0 %s %s > /tmp/freevo.wid &' %
                      (osd.width, osd.height))
            time.sleep(1)
            if os.path.isfile('/tmp/freevo.wid'):
                if DEBUG: print 'Got freevo.wid'
                try:
                    wid = int(open('/tmp/freevo.wid').read().strip(), 16)
                    mpl += ' -wid 0x%08x -xy %s -monitoraspect 4:3' % \
                           (wid, osd.width)
                    if DEBUG: print 'Got WID = 0x%08x' % wid
                except:
                    pass


        if mode == 'file':
            command = mpl + ' "' + filename + '"'
        else:
            command = mpl

        if options:
            print options
            command += ' ' + options

        command=vop_append(command)
        
        self.file = item

        # XXX A better place for the major part of this code would be
        # XXX mixer.py
        if config.CONTROL_ALL_AUDIO:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            if config.MAJOR_AUDIO_CTRL == 'VOL':
                mixer.setPcmVolume(config.MAX_VOLUME)
            elif config.MAJOR_AUDIO_CTRL == 'PCM':
                mixer.setMainVolume(config.MAX_VOLUME)
                
        mixer.setIgainVolume(0) # SB Live input from TV Card.
        # This should _really_ be set to zero when playing other audio.

        self.thread.play_mode = self.mode
        self.thread.item  = item
        self.item  = item
        
        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'

        self.thread.command = command
        self.thread.mode_flag.set()
        rc.app = self.eventhandler
        rc.func = 'video'


    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        rc.app = None
        rc.func = None
        while self.thread.mode == 'stop':
            time.sleep(0.3)
            

    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if (event == rc.STOP or event == rc.SELECT) and not self.seek:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 6\n')
                return TRUE
            else:
                self.stop()
                self.thread.item = None
                rc.app = None
                return self.item.eventhandler(event)

        if event == rc.REC:
            # Bookmark the current time into a file
            
            bookmarkfile = util.get_bookmarkfile(self.filename)
            
            handle = open(bookmarkfile,'a+') # Should be appending so we could
                                             # have multiple bookmarks later, with
                                             # a menu or something. 
            handle.write(str(self.item.elapsed))
            handle.write('\n')
            handle.close()
            print "Added bookmark at position " + str(self.item.elapsed)
            return self.item.eventhandler(event)

        if event == rc.EXIT:
            self.stop()
            self.thread.item = None
            rc.app = None
            menuwidget.refresh(reload=1)
            return self.item.eventhandler(event)
        
        if event == rc.PLAY_END or event == rc.USER_END:
            self.stop()
            rc.app = None
            print self.item
            return self.item.eventhandler(event)

        if event == rc.DVD_PROTECTED:
            self.stop()
            rc.app = None

            if not config.NEW_SKIN:
                skin.PopupBox('The DVD is protected, see the docs for more info!')
                osd.update()
                time.sleep(5.0)

            # Forward the event as if it was a regular end of item
            event = rc.PLAY_END
            return self.item.eventhandler(event)

        # try to find the event in RC_MPLAYER_CMDS 
        e = config.RC_MPLAYER_CMDS.get(event, None)
        if e:
            self.thread.app.write('%s\n' % config.RC_MPLAYER_CMDS[event][0])
            return TRUE

        if event == rc.MENU:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 5\n')
                return TRUE

        if event == rc.DISPLAY:
            self.thread.app.write('osd\n')
            return TRUE

        if event == rc.PAUSE or event == rc.PLAY:
            self.thread.app.write('pause\n')
            return TRUE

        if event == rc.FFWD:
            self.thread.app.write('seek 10\n')
            return TRUE

        if event == rc.UP:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 1\n')
                return TRUE

        if event == rc.REW:
            self.thread.app.write('seek -10\n')
            return TRUE

        if event == rc.DOWN:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 2\n')
                return TRUE

        if event == rc.LEFT:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 3\n')
            else:
                self.thread.app.write('seek -60\n')
            return TRUE

        if event == rc.RIGHT:
            if self.mode == 'dvdnav':
                self.thread.app.write('dvdnav 4\n')
            else:
                self.thread.app.write('seek 60\n')
            return TRUE
        
        if event == rc.SELECT:
            self.seek_timer.cancel()
            self.seek *= 60
            self.thread.app.write('seek ' + str(self.seek) + ' 2\n')
            self.seek = 0
            return TRUE
        
        if event == rc.K0:
            self.reset_seek_timeout()
            self.seek *= 10;
            return TRUE
        
        if event == rc.K1:
            self.reset_seek_timeout()
            self.seek += self.seek * 10 + 1
            return TRUE
            
        elif event == rc.K2:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 2
                return TRUE
        
        elif event == rc.K3:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 3
                return TRUE
                
        elif event == rc.K4:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 4
                return TRUE
                
        elif event == rc.K5:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 5
                return TRUE
                
        elif event == rc.K6:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 6
                return TRUE
                
        elif event == rc.K7:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 7
                return TRUE
                
        elif event == rc.K8:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 8
                return TRUE
                
        elif event == rc.K9:
                self.reset_seek_timeout()
                self.seek += self.seek * 10 + 9
                return TRUE

        # nothing found? Try the eventhandler of the object who called us
        return self.item.eventhandler(event)
    
    def reset_seek(self):
        self.seek = 0
        
    def reset_seek_timeout(self):
        self.seek_timer.cancel()
        self.seek_timer = threading.Timer(config.MPLAYER_SEEK_TIMEOUT, self.reset_seek)
        self.seek_timer.start()
        
    seek = 0
    seek_timer = threading.Timer(0, reset_seek)

# ======================================================================

class MPlayerParser:
    """
    class to parse the mplayer output and store some information
    in the videoitem
    """
    
    def __init__(self, item):
        self.item = item
        self.RE_AUDIO = re.compile("^\[open\] audio stream: [0-9] audio format:"+\
                                   "(.*)aid: ([0-9]*)").match
        self.RE_SUBTITLE = re.compile("^\[open\] subtitle.*: ([0-9]) language: "+\
                                      "([a-z][a-z])").match
        self.RE_CHAPTER = re.compile("^There are ([0-9]*) chapters in this DVD title.").match
        self.RE_EXIT = re.compile("^Exiting\.\.\. \((.*)\)$").match

    def parse(self, line):
        m = self.RE_AUDIO(line)
        if m: self.item.available_audio_tracks += [ (m.group(2), m.group(1)) ]

        m = self.RE_SUBTITLE(line)
        if m: self.item.available_subtitles += [ (m.group(1), m.group(2)) ]

        m = self.RE_CHAPTER(line)
        if m: self.item.available_chapters = int(m.group(1))

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

        self.RE_TIME = re.compile("^A: +([0-9]+)").match
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
        util.killall('freevo_xwin')
        os.system('rm -f /tmp/freevo.wid')

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
            rc.post_event(rc.DVD_PROTECTED)
            
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

                # The DXR3 device cannot be shared between our SDL session
                # and MPlayer.
                if (osd.sdl_driver == 'dxr3' or \
                    config.CONF.display == 'dfbmga'):
                    print "Stopping Display for Video Playback"
                    osd.stopdisplay()
                
                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    if self.app.exit_type == "End of file":
                        rc.post_event(rc.PLAY_END)
                    elif self.app.exit_type == "Quit":
                        rc.post_event(rc.USER_END)

                # Ok, we can use the OSD again.
                if osd.sdl_driver == 'dxr3' or config.CONF.display == 'dfbmga':
                    osd.restartdisplay()
		    osd.update()
		    print "Display back online"

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'


