#!/usr/bin/env python

#if 0 /*
# -----------------------------------------------------------------------
# timeshift.py - module to handle timeshifting - encoding and viewing
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/04/22 19:34:12  dischi
# mplayer and tvtime are now plugins
#
# Revision 1.3  2003/04/20 12:43:34  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.2  2003/03/27 03:43:50  rshortt
# Moved as much information as I could into freevo_config.py.  Also fixed a
# couple bugs, chanup and chandown were backwards, the channel wasn't getting
# set when you start to watch tv, and the RESET command for the timeshifter
# was in lower case.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import fcntl, sys, os, struct
import threading
import config
import util
import childapp
import signal
import time
import tv
import rc

from plugins.mplayer import MPlayer_Thread

DEBUG = 1

# Module variable that contains an initialized V4L1TV() object
_singleton = None
TRUE  = 1
FALSE = 0

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = Timeshifter()
        
    return _singleton



class Timeshifter:
    def __init__(self):
        self.encoderthread = Encoder_Thread()
        self.mplayerthread = MPlayer_Thread()
        self.encoderthread.start()
        self.mplayerthread.start()
        self.tuner_chidx = 0
        self.mode = ''
        self.cf_norm, self.cf_input, self.cf_clist, self.cf_device = config.TV_SETTINGS.split()

    def TunerSetChannel(self, tuner_channel):
        for pos in range(len(config.TV_CHANNELS)):
            channel = config.TV_CHANNELS[pos]
            if channel[2] == tuner_channel:
                self.tuner_chidx = pos
                ch_opts = { 'channel'   : tuner_channel,
                            'norm'      : self.cf_norm,
                            'freqtable' : self.cf_clist }
                chan_cmd = config.TV_CHANNEL_PROG % ch_opts
                if DEBUG: print 'TS: chan_cmd="%s"' % chan_cmd
                os.system(chan_cmd)
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

    def StartEncoder(self):
	self.encoderthread.app.write( 'SPAWN %s\n' % config.TIMESHIFT_ENCODE_CMD )
        # Wait some time to ensure the file is created and some initial data contained.
        # Otherwise Mplayer will stop immediately
        time.sleep(1)
        self.mplayerthread.mode = 'play'
        self.mplayerthread.mode_flag.set()

    def StopEncoder(self):
        self.encoderthread.app.write( "JOIN\n")
        self.mplayerthread.mode = 'pause'
        self.mplayerthread.mode_flag.set()


    def eventhandler(self,event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if (event == rc.MENU or event == rc.STOP or event == rc.EXIT or
            event == rc.SELECT or event == rc.PLAY_END):
            self.Play('stop')
            rc.app(tv)
            tv.refresh()
            return TRUE
        elif event == rc.CHUP or event == rc.CHDOWN:
            if event == rc.CHUP:
                self.TunerNextChannel()
            else:
                self.TunerPrevChannel()
            new_channel = self.TunerGetChannel()
            self.mplayerthread.app.write('pause\n')
            self.TunerSetChannel(new_channel)
            # self.encoderthread.app.write('RESET\n')
            self.mplayerthread.app.write('seek 0 type=2\n')
            return TRUE
        elif event == rc.LEFT:
            self.StartEncoder()
            return TRUE
        elif event == rc.RIGHT:
            self.StopEncoder()
            return TRUE
        elif event == rc.PAUSE or event == rc.PLAY:
            self.mplayerthread.app.write('pause\n')
            # TODO: Check whether timeshifter has an overrun, in that case unpause
            return TRUE
        elif event == rc.FFWD:
            self.mplayerthread.app.write('seek 10\n')
            return TRUE
        elif event == rc.REW:
            self.mplayerthread.app.write('seek -10\n')
            return TRUE
        return TRUE

    def Play(self, mode, tuner_channel=None, channel_change=0):
        if mode == 'tv':
            if tuner_channel != None:            
                try:
                    self.TunerSetChannel(tuner_channel)
                except ValueError:
                    pass
                tuner_channel = self.TunerGetChannel()

            cf_norm, cf_input, cf_clist, cf_device = config.TV_SETTINGS.split()
            
            w, h = config.TV_VIEW_SIZE
            tscmd = 'timeshift://%s' % self.encoderthread.timeshiftfile

            # Build the MPlayer command
            args = (config.MPLAYER_NICE, config.MPLAYER_CMD, config.MPLAYER_VO_DEV,
                    config.MPLAYER_VO_DEV_OPTS, tscmd, config.MPLAYER_ARGS_TVVIEW)
            mpl = '--prio=%s %s -vo %s%s -fs %s %s -slave' % args
            self.mplayerthread.command = mpl

            self.encoderthread.mode = mode
            self.encoderthread.mode_flag.set()
            rc.app(self)
            # Wait for the Task to be up and running
            time.sleep(1)
            # Then, immediately start encoding
            self.StartEncoder( )
        elif mode == 'stop':
            self.StopEncoder()
            self.encoderthread.mode = mode
            self.mplayerthread.mode = mode
            self.mplayerthread.mode_flag.set()
            self.encoderthread.mode_flag.set()        

class TimeshifterApp(childapp.ChildApp):
    """
    class controlling the in and output from timeshift master
    """

    def __init__(self, app):
        childapp.ChildApp.__init__(self, app)


    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        childapp.ChildApp.kill(self, signal.SIGINT)


    def stdout_cb(self, str):
        print str

    def stderr_cb(self, str):
        print str

class Encoder_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

        self.mode      = 'idle'
        self.mode_flag = threading.Event()
        cf_norm, cf_input, cf_clist, self.capturedev = config.TV_SETTINGS.split()
        self.audiodev = config.AUDIO_INPUT_DEVICE
        self.timeshiftfile = config.TIMESHIFT_BUFFER
        self.timeshiftsize = 1024*1024*config.TIMESHIFT_BUFFER_SIZE
        self.command = './timeshifter %s %d' % (self.timeshiftfile, self.timeshiftsize)
        self.app       = None

    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'tv':
                self.app = TimeshifterApp(self.command)
                while self.mode == 'tv' and self.app.isAlive():
                    time.sleep(0.1)
                self.app.kill()
                self.mode = 'idle'
        print "App Killed.\n"

if __name__ == '__main__':
  t = Timeshifter()
  t.Play('tv')

