#if 0 /*
# -----------------------------------------------------------------------
# tvtime.py - Temporary implementation of a TV function using tvtime
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/20 11:01:01  dischi
# use mixer plugin, please test
#
# Revision 1.1  2003/04/17 04:44:12  krister
# Added a quick hack to support tvtime. It uses stdin on tvtime for commands, this is not supported in tvtime yet.
#
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

import time, os
import string
import threading
import signal

import util    # Various utilities
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import childapp # Handle child applications
import epg_xmltv as epg # The Electronic Program Guide

import plugin

# Create the remote control object
rc = rc.get_singleton()


# Set to 1 for debug output
DEBUG = config.DEBUG or 3

TRUE = 1
FALSE = 0


# Create the OSD object
osd = osd.get_singleton()

# Module variable that contains an initialized V4L1TV() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = TVTime()
        
    return _singleton


class TVTime:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.thread = TVTime_Thread()
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

            if 0: # XXX Later...
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

            command = 'tvtime'

        else:
            print 'Mode "%s" is not implemented' % mode  # XXX ui.message()
            return

        self.mode = mode

        mixer = plugin.getbyname('MIXER')

        # XXX Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer_vol = mixer.getMainVolume()
            mixer.setMainVolume(0)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer_vol = mixer.getPcmVolume()
            mixer.setPcmVolume(0)

        # Start up the TV task
        self.thread.mode = 'play'
        self.thread.command = command
        self.thread.mode_flag.set()
        
        self.parent_eventhandler = rc.app
        rc.app = self.EventHandler

        if osd.focused_app:
            osd.focused_app.hide()

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # XXX Hm.. This is hardcoded and very unflexible.
        if mixer and mode == 'vcr':
            mixer.setMicVolume(config.VCR_IN_VOLUME)
        elif mixer:
            mixer.setLineinVolume(config.TV_IN_VOLUME)
            mixer.setIgainVolume(config.TV_IN_VOLUME)
            
        if mixer and config.MAJOR_AUDIO_CTRL == 'VOL':
            mixer.setMainVolume(mixer_vol)
        elif mixer and config.MAJOR_AUDIO_CTRL == 'PCM':
            mixer.setPcmVolume(mixer_vol)

        if DEBUG: print '%s: started %s app' % (time.time(), self.mode)
        self.thread.app.setchannel(tuner_channel)

        
        
    def Stop(self):
        mixer = plugin.getbyname('MIXER')
        if mixer:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()

        rc.app = self.parent_eventhandler
        if osd.focused_app:
            osd.focused_app.show()

        while self.thread.mode == 'stop':
            time.sleep(0.05)
        print 'stopped %s app' % self.mode
        #os.system('rm -f /tmp/freevo.wid')


    def EventHandler(self, event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if (event == rc.MENU or event == rc.STOP or event == rc.EXIT or
            event == rc.SELECT or event == rc.PLAY_END):
            self.Stop()
            rc.post_event(rc.PLAY_END)

        elif event == rc.CHUP or event == rc.CHDOWN:
            if self.mode == 'vcr':
                return
            
            # Go to the prev/next channel in the list
            if event == rc.CHUP:
                self.TunerPrevChannel()
            else:
                self.TunerNextChannel()

            new_channel = self.TunerGetChannel()
            #self.thread.fifo.write('tv_set_channel %s\n' % new_channel)
            self.thread.app.setchannel(new_channel)

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
            

        # this should work from within the plugin:
        #elif event == rc.VOLUP:
        #    mixer.incIgainVolume()

        #elif event == rc.VOLDOWN:
        #    mixer.decIgainVolume()

        #elif event == rc.MUTE:
        #    if self.__muted:
        #        self.__muted = 0
        #    else:
        #        self.__muted = 1
        #    self.MuteOnOff(mute=self.__muted)
            

    #def MuteOnOff(self, mute=0):
    #    if mute:
    #        self.__igainvol = mixer.getIgainVolume()
    #        mixer.setIgainVolume(0)
    #    else:
    #        mixer.setIgainVolume(self.__igainvol)
        
            

# ======================================================================
class TVTimeApp(childapp.ChildApp):
    """
    class controlling the in and output from the tvtime process
    """

    def __init__(self, app):
        if config.MPLAYER_DEBUG: # XXX Use MPLAYER_DEBUG for now...
            startdir = os.environ['FREEVO_STARTDIR']
            fname_out = os.path.join(startdir, 'mplayer_stdout.log')
            fname_err = os.path.join(startdir, 'mplayer_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'a')
                self.log_stderr = open(fname_err, 'a')
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'TVTime logging!') % (fname_out, fname_err))
                print 'Please set MPLAYER_DEBUG=0 in local_conf.py, or '
                print 'start Freevo from a directory that is writeable!'
                print
            else:
                print 'TVTime logging to "%s" and "%s"' % (fname_out, fname_err)

        childapp.ChildApp.__init__(self, app)
        

    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure TVTime shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        self.write('quit')
        childapp.ChildApp.kill(self, signal.SIGINT)

        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing tvtime'
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

    def setchannel(self, channelno):
        ch_digits = list(str(channelno))   # XXX Only works for numerical channels!
        for digit in ch_digits:
            cmd = 'CHANNEL_%s\n' % digit
            self.write(cmd)
        self.write('\n')

        
# ======================================================================
class TVTime_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.command  = ''
        self.app = None
        self.fifo = None
        self.audioinfo = None              # Added to enable update of GUI

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'play':
                # The DXR3 device cannot be shared between our SDL session
                # and TVTime.
                if (osd.sdl_driver == 'dxr3'):
                    if DEBUG:
                        print "Stopping Display for Video Playback on DXR3"
                    osd.stopdisplay()			
                if DEBUG:
                    print 'TVTime_Thread.run(): Started, cmd=%s' % self.command
                    
                self.app = TVTimeApp(self.command)
                
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

