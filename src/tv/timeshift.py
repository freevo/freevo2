#!/usr/bin/python2.2

import fcntl, sys, os, struct
import threading
import config
import util
import childapp
import signal
import time
import tv
import rc
from mplayer import MPlayer_Thread

remote = rc.get_singleton()


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
	self.encoderthread.app.write( 'SPAWN mp1e -m3 -c%s -p%s -r14,100\n' % ('/dev/video0','/dev/dsp2') )
        # Wait some time to ensure the file is created and some initial data contained.
        # Otherwise Mplayer will stop immediately
        time.sleep(1)
        self.mplayerthread.mode = 'play'
        self.mplayerthread.mode_flag.set()

    def StopEncoder(self):
        self.encoderthread.app.write( "JOIN\n")
        self.mplayerthread.mode = 'pause'
        self.mplayerthread.mode_flag.set()


    def EventHandler(self,event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if (event == remote.MENU or event == remote.STOP or event == remote.EXIT or
            event == remote.SELECT or event == remote.PLAY_END):
            self.Play('stop')
            remote.app = tv.eventhandler            
            tv.refresh()
            return TRUE
        elif event == remote.CHUP or event == remote.CHDOWN:
            if event == remote.CHUP:
                self.TunerPrevChannel()
            else:
                self.TunerNextChannel()
            new_channel = self.TunerGetChannel()
            self.mplayerthread.app.write('pause\n')
            #os.spawnlp(os.P_WAIT, 'v4lctl', '--device=%s'%self.encoderthread.capturedev, 'setchannel', new_channel)
            os.spawnlp(os.P_WAIT, 'chchan','%s %s %s' % (new_channel, self.cf_norm, self.cf_clist))
            self.encoderthread.app.write('reset\n')
            self.mplayerthread.app.write('seek 0 type=2\n')
            return TRUE
        elif event == remote.LEFT:
            self.StartEncoder()
            return TRUE
        elif event == remote.RIGHT:
            self.StopEncoder()
            return TRUE
        elif event == remote.PAUSE or event == remote.PLAY:
            self.mplayerthread.app.write('pause\n')
            # TODO: Check whether timeshifter has an overrun, in that case unpause
            return TRUE
        elif event == remote.FFWD:
            self.mplayerthread.app.write('seek 10\n')
            return TRUE
        elif event == remote.REW:
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
            remote.app = self.EventHandler
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
        self.audiodev = '/dev/dsp2'
        self.timeshiftfile = '/media/Recording/buffer/tsmaster.mpg'
        self.timeshiftsize = 1024*1024*32
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

