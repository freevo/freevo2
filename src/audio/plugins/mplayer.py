#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - the Freevo MPlayer plugin for audio
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/21 18:40:33  dischi
# use plugin name structure to find the real player
#
# Revision 1.1  2003/04/21 13:26:12  dischi
# mplayer is now a plugin
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

import time, os
import string
import threading, signal

import config     # Configuration handler. reads config file.
import util       # Various utilities
import childapp   # Handle child applications
import rc         # The RemoteControl class.

# RegExp
import re
import plugin

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0

# contains an initialized MPlayer() object
mplayer = None


class PluginInterface(plugin.Plugin):
    """
    Mplayer plugin for the audio player. Use mplayer to play all audio
    files.
    """
    def __init__(self):
        global mplayer
        # create the mplayer object
        plugin.Plugin.__init__(self)
        mplayer = util.SynchronizedObject(MPlayer())

        # register it as the object to play audio
        plugin.register(mplayer, plugin.AUDIO_PLAYER)


class MPlayer:
    """
    the main class to control mplayer
    """
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.mode = None
        self.app_mode = 'audio'

        
    def get_demuxer(self, filename):
        DEMUXER_MP3 = 17
        DEMUXER_OGG = 18
        rest, extension     = os.path.splitext(filename)
        if string.lower(extension) == '.mp3':
            return "-demuxer " + str(DEMUXER_MP3)
        if string.lower(extension) == '.ogg':
            return "-demuxer " + str(DEMUXER_OGG)
        else:
            return ''


    def play(self, item, playerGUI):
        """
        play a audioitem with mplayer
        """
        filename = item.filename
        self.playerGUI = playerGUI
        
        # Is the file streamed over the network?
        if filename.find('://') != -1:
            # Yes, trust the given mode
            network_play = 1
        else:
            network_play = 0

        if not os.path.isfile(filename) and not network_play:
            return '%s\nnot found!' % os.path.basename(filename)
            
        # Build the MPlayer command
        mpl = '--prio=%s %s -slave %s' % (config.MPLAYER_NICE,
                                          config.MPLAYER_CMD,
                                          config.MPLAYER_ARGS_DEF)

        if not network_play:
            demux = ' %s ' % self.get_demuxer(filename)
        else:
            # Don't include demuxer for network files
            demux = ''

        extra_opts = item.mplayer_options
        command = '%s -vo null -ao %s %s %s "%s"' % (mpl, config.MPLAYER_AO_DEV,
                                                     demux, extra_opts, filename)
                
        if plugin.getbyname('MIXER'):
            plugin.getbyname('MIXER').reset()

        self.item = item
        self.thread.item = item

        if not self.thread.item.valid:
            # Invalid file, show an error and survive.
            return 'Invalid audio file'

        self.thread.play_mode = self.mode

        if DEBUG:
            print 'MPlayer.play(): Starting thread, cmd=%s' % command
            
        self.thread.mode    = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        return None
    

    def stop(self):
        """
        Stop mplayer and set thread to idle
        """
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        self.thread.item = None
        while self.thread.mode == 'stop':
            time.sleep(0.3)


    def is_playing(self):
        return self.thread.mode != 'idle'

    def refresh(self):
        self.playerGUI.refresh()
        
    def eventhandler(self, event):
        """
        eventhandler for mplayer control. If an event is not bound in this
        function it will be passed over to the items eventhandler
        """

        if event == 'AUDIO_PLAY_END':
            event = rc.PLAY_END
            
        if event in ( rc.EXIT, rc.PLAY_END, rc.USER_END ):
            self.playerGUI.stop()
            return self.item.eventhandler(event)

        # try to find the event in RC_MPLAYER_CMDS 
        e = config.RC_MPLAYER_AUDIO_CMDS.get(event, None)
        if e:
            e = config.RC_MPLAYER_AUDIO_CMDS[event][0]
            if callable(e):
                e(self)
            else:
                self.thread.app.write('%s\n' % e)
            return TRUE

        elif event == rc.PAUSE or event == rc.PLAY:
            self.thread.app.write('pause\n')
            return TRUE

        elif event == rc.FFWD:
            self.thread.app.write('seek 10\n')
            return TRUE

        elif event == rc.RIGHT:
            self.thread.app.write('seek 60\n')
            return TRUE

        elif event == rc.REW:
            self.thread.app.write('seek -10\n')
            return TRUE

        elif event == rc.LEFT:
            self.thread.app.write('seek -60\n')
            return TRUE

        else:
            # everything else: give event to the items eventhandler
            return self.item.eventhandler(event)
            
            
# ======================================================================

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

        self.item = item
        self.elapsed = 0
        childapp.ChildApp.__init__(self, app)
        self.RE_TIME = re.compile("^A: +([0-9]+)").match
              
    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)
        if config.MPLAYER_DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()

    def stdout_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stdout.write(line + '\n')
            except ValueError:
                pass # File closed
                     
        if line.startswith("A:"):         # get current time
            m = self.RE_TIME(line) # Convert decimal 
            if m:
                self.item.elapsed = int(m.group(1))
                if self.item.elapsed != self.elapsed:
                    mplayer.refresh()
                self.elapsed = self.item.elapsed

    def stderr_cb(self, line):
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
        self.item      = None

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command, self.item)

                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                self.app.kill()

                if self.mode == 'play':
                    rc.post_event('AUDIO_PLAY_END')

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'
