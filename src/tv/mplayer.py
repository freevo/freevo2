#if 0 /*
# -----------------------------------------------------------------------
# mplayer.py - Temporary implementation of a TV function using MPlayer
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2003/02/22 07:13:19  krister
# Set all sub threads to daemons so that they die automatically if the main thread dies.
#
# Revision 1.6  2003/02/11 04:37:29  krister
# Added an empty local_conf.py template for new users. It is now an error if freevo_config.py is found in /etc/freevo etc. Changed DVD protection to use a flag. MPlayer stores debug logs in FREEVO_STARTDIR, and stops with an error if they cannot be written.
#
# Revision 1.5  2003/02/06 09:52:26  krister
# Changed the runtime handling to use runapp to start programs with the supplied dlls
#
# Revision 1.4  2003/01/22 01:48:26  krister
# Use slave mode to change channels.
#
# Revision 1.3  2002/12/29 19:24:25  dischi
# Integrated two small fixes from Jens Axboe to support overscan for DXR3
# and to set MPLAYER_VO_OPTS
#
# Revision 1.2  2002/12/16 08:02:19  dischi
# dxr3 patch
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


# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading
import signal

import util    # Various utilities
import menu    # The menu widget class
import skin    # The skin class
import mixer   # The mixer class
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import tv      # The TV module
import childapp # Handle child applications
import epg_xmltv as epg # The Electronic Program Guide


# Create the remote control object
rc = rc.get_singleton()


# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the MenuWidget object
menuwidget = menu.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()


# Module variable that contains an initialized V4L1TV() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MPlayer()
        
    return _singleton


class MPlayer:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                self.tuner_chidx = pos
                return
        print 'ERROR: Cannot find tuner channel "%s" in the TV channel listing' % tuner_channel
        self.tuner_chidx = 0


    def TunerGetChannelInfo(self):
        '''Get program info for the current channel'''
        
        tuner_id = config.TV_CHANNELS[self.tuner_chidx][2]
        chan_name = config.TV_CHANNELS[self.tuner_chidx][1]
        chan_id = config.TV_CHANNELS[self.tuner_chidx][0]

        channels = epg.get_guide().GetPrograms(start=time.time(),
                                               stop=time.time(), chanids=[chan_id])

        if channels and channels[0] and channels[0].programs:
            start_s = time.strftime('%H:%M', time.localtime(channels[0].programs[0].start))
            stop_s = time.strftime('%H:%M', time.localtime(channels[0].programs[0].stop))
            ts = '(%s-%s)' % (start_s, stop_s)
            prog_info = '%s %s' % (ts, channels[0].programs[0].title)
        else:
            prog_info = 'No info'
            
        return tuner_id, chan_name, prog_info


    def TunerGetChannel(self):
        return config.TV_CHANNELS[self.tuner_chidx][2]


    def TunerNextChannel(self):
        self.tuner_chidx = (self.tuner_chidx+1) % len(config.TV_CHANNELS)


    def TunerPrevChannel(self):
        self.tuner_chidx = (self.tuner_chidx-1) % len(config.TV_CHANNELS)

        
    def Play(self, mode, tuner_channel=None, channel_change=0):

        if tuner_channel != None:
            
            try:
                self.TunerSetChannel(tuner_channel)
            except ValueError:
                pass

        if mode == 'tv':
            tuner_channel = self.TunerGetChannel()

            cf_norm, cf_input, cf_clist, cf_device = config.TV_SETTINGS.split()

            # Convert to MPlayer TV setting strings
            norm = 'norm=%s' % cf_norm.upper()
            tmp = { 'television':0, 'composite1':1, 'composite2':2,
                    's-video':3}[cf_input.lower()]
            input = 'input=%s' % tmp
            chanlist = 'chanlist=%s' % cf_clist
            device= 'device=%s' % cf_device
            
            w, h = config.TV_VIEW_SIZE
            outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT

            tvcmd = ('-tv on:driver=v4l:%s:%s:%s:channel=%s:'
                     '%s:width=%s:height=%s:%s' %
                     (device, input, norm, tuner_channel, chanlist, w, h, outfmt))
            
            # Build the MPlayer command
            args = (config.MPLAYER_NICE, config.MPLAYER_CMD, config.MPLAYER_VO_DEV,
                    config.MPLAYER_VO_DEV_OPTS, tvcmd, config.MPLAYER_ARGS_TVVIEW)
            mpl = '--prio=%s %s -vo %s%s -fs %s %s -slave' % args

        elif mode == 'vcr':
            cf_norm, cf_input, tmp, cf_device = config.VCR_SETTINGS.split()

            # Convert to MPlayer TV setting strings
            norm = 'norm=%s' % cf_norm.upper()
            tmp = { 'television':0, 'composite1':1, 'composite2':2,
                    's-video':3}[cf_input.lower()]
            input = 'input=%s' % tmp
            device= 'device=%s' % cf_device

            w, h = config.TV_VIEW_SIZE
            outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT
            
            tvcmd = ('-tv on:driver=v4l:%s:%s:%s:channel=2:'
                     'chanlist=us-cable:width=%s:height=%s:%s' %
                     (device, input, norm, w, h, outfmt))

            args = (config.MPLAYER_CMD, config.MPLAYER_VO_DEV,
                    config.MPLAYER_VO_DEV_OPTS, tvcmd,
                    config.MPLAYER_ARGS_TVVIEW)
            mpl = '%s -vo %s%s -fs %s %s' % args

        else:
            print 'Mode "%s" is not implemented' % mode  # XXX ui.message()
            rc.app = None
            menuwidget.refresh()
            return

        # Support for X11, getting the keyboard events
        if (os.path.isfile('./freevo_xwin') and osd.sdl_driver == 'x11' and
            config.MPLAYER_USE_WID):
            if DEBUG: print 'Got freevo_xwin and x11'
            os.system('rm -f /tmp/freevo.wid')
            os.system('./runapp ./freevo_xwin  0 0 %s %s > /tmp/freevo.wid &' %
                      (osd.width, osd.height))

            # Wait until freevo_xwin signals us, but have a timeout so we
            # don't hang here if something goes wrong!
            delay_ms = 50
            timeout_ms = 5000
            while 1:
                if os.path.isfile('/tmp/freevo.wid'):
                    # Check if the whole line has been written yet
                    val = open('/tmp/freevo.wid').read()
                    if len(val) > 5 and val[-1] == '\n':
                        break
                time.sleep(delay_ms / 1000.0)
                timeout_ms -= delay_ms
                if timeout_ms < 0.0:
                    print 'Could not start freevo_xwin!'  # XXX ui.message()
                    return

            if DEBUG: print 'Got freevo.wid'
            try:
                wid = int(open('/tmp/freevo.wid').read().strip(), 16)
                mpl += ' -wid 0x%08x -xy %s -monitoraspect 4:3' % (wid, osd.width)
                if DEBUG: print 'Got WID = 0x%08x' % wid
            except:
                print 'Cannot access freevo_xwin data!'   # XXX ui.message()
                pass

        command = mpl
                
        self.mode = mode

        # XXX Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # clear the screen for mplayer
        osd.clearscreen(color=osd.COL_BLACK)
        osd.update()
        
        # Start up the TV task
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        rc.app = self.EventHandler

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mode == 'vcr':
            mixer.setMicVolume(config.VCR_IN_VOLUME)
        else:
            mixer.setLineinVolume(config.TV_IN_VOLUME)
            mixer.setIgainVolume(config.TV_IN_VOLUME)
            
        if config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        if DEBUG: print '%s: started %s app' % (time.time(), self.mode)

        skin.hold = TRUE  # Prevent the skin from drawing stuff while TV is on
        
        
    def Stop(self):
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)
        mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
        while self.thread.mode == 'stop':
            time.sleep(0.05)
        print 'stopped %s app' % self.mode
        os.system('rm -f /tmp/freevo.wid')


    def EventHandler(self, event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if (event == rc.MENU or event == rc.STOP or event == rc.EXIT or
            event == rc.SELECT or event == rc.PLAY_END):
            self.Stop()
            skin.hold = FALSE  # Allow drawing again
            rc.app = tv.eventhandler
            tv.refresh()

        elif event == rc.CHUP or event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            
            # Go to the prev/next channel in the list
            if event == rc.CHUP:
                self.TunerPrevChannel()
            else:
                self.TunerNextChannel()

            new_channel = self.TunerGetChannel()
            self.thread.app.write('tv_set_channel %s\n' % new_channel)

            # Display a channel changed message
            # XXX Experimental, disabled for now
            #tuner_id, chan_name, prog_info = self.TunerGetChannelInfo()
            #now = time.strftime('%H:%M')
            #msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            #cmd = 'show_osd_msg "%s" 4000\n' % msg
            #self.thread.app.write(cmd)
            
        elif event == rc.DISPLAY:
            return
        
            # Display the channel info message
            # XXX Experimental, disabled for now
            tuner_id, chan_name, prog_info = self.TunerGetChannelInfo()
            now = time.strftime('%H:%M')
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'show_osd_msg "%s" 4000\n' % msg
            print 'msg = "%s" %s chars' % (msg, len(msg))
            self.thread.app.write(cmd)
            
        elif event == rc.VOLUP:
            mixer.incIgainVolume()

        elif event == rc.VOLDOWN:
            mixer.decIgainVolume()

        elif event == rc.MUTE:
            if self.__muted:
                self.__muted = 0
            else:
                self.__muted = 1
            self.MuteOnOff(mute=self.__muted)
            

    def MuteOnOff(self, mute=0):
        if mute:
            self.__igainvol = mixer.getIgainVolume()
            mixer.setIgainVolume(0)
        else:
            mixer.setIgainVolume(self.__igainvol)
        
            

# ======================================================================
class MPlayerApp(childapp.ChildApp):
    """
    class controlling the in and output from the mplayer process
    """

    def __init__(self, app):
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

        childapp.ChildApp.__init__(self, app)
        

    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        self.write('quit')
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
                     

    def stderr_cb(self, line):
        if config.MPLAYER_DEBUG:
            try:
                self.log_stderr.write(line + '\n')
            except ValueError:
                pass # File closed


# ======================================================================
class MPlayer_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        self.command   = ''
        self.app       = None
        self.audioinfo = None              # Added to enable update of GUI

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'play':
                # The DXR3 device cannot be shared between our SDL session
                # and MPlayer.
                if (osd.sdl_driver == 'dxr3'):
                    if DEBUG:
                        print "Stopping Display for Video Playback on DXR3"
                    osd.stopdisplay()			
                if DEBUG:
                    print 'MPlayer_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = MPlayerApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    if self.audioinfo: 
                        if not self.audioinfo.pause:
                            self.audioinfo.draw()        
                    time.sleep(0.1)

                self.app.kill()

                # Ok, we can use the OSD again.
                if osd.sdl_driver == 'dxr3':
                    osd.restartdisplay()
                    osd.update()
                    print "Display back online"

                if self.mode == 'play':
                    if DEBUG: print 'posting play_end'
                    rc.post_event(rc.PLAY_END)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'

