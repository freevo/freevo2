#if 0 /*
# -----------------------------------------------------------------------
# timeshift.py - TV Plugin for timeshifted viewing
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
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

import config

import time, os
import threading
import signal

import util    # Various utilities
import osd     # The OSD class, used to communicate with the OSD daemon
import event as em
import rc
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide

import plugin
import v4l2	# Video4Linux2 Python Interface
import pyshift	# Timeshift Interface

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

(v_norm, v_input, v_clist, v_dev) = config.TV_SETTINGS.split()
# v_norm = string.upper(v_norm)

TIMESHIFT_INPUT = v_dev 		# File to read from
TIMESHIFT_CHUNKSIZE = 65536 		# Amount to read repeatedly (in Bytes)

# Create the OSD object
osd = osd.get_singleton()

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with mplayer.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)

        # create the mplayer object and register it
        plugin.register(MPlayer(), plugin.TV)


class MPlayer:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self):
        self.thread = MPlayer_Thread()
        self.thread.setDaemon(1)
        self.thread.start()
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        self.videodev = None
        self.app_mode = 'tv'


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
        
        (chan_id, chan_name, tuner_id,) = config.TV_CHANNELS[self.tuner_chidx]

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
            # rc.set_context('tv')

            tuner_channel = self.TunerGetChannel()

            cf_norm, cf_input, cf_clist, cf_device = config.TV_SETTINGS.split()            
            w, h = config.TV_VIEW_SIZE
            self.videodev = v4l2.Videodev(cf_device)
            self.videodev.setchanlist(cf_clist)
            self.videodev.setchannel(tuner_channel)
            # TODO: Set Resolution, get file from config
            tvcmd = ('timeshift://%s' % config.TIMESHIFT_BUFFER )
            
            # Build the MPlayer command
            args = (config.MPLAYER_NICE, config.MPLAYER_CMD, config.MPLAYER_VO_DEV,
                    config.MPLAYER_VO_DEV_OPTS, tvcmd)

            if config.MPLAYER_ARGS.has_key('timeshift'):
                args += (config.MPLAYER_ARGS['timeshift'],)

            mpl = '--prio=%s %s -vo %s%s -fs %s -slave -nocache' % args

        else:
            print 'Mode "%s" is not implemented' % mode  # XXX ui.message()
            return

        command = mpl
        self.mode = mode


        # XXX Mixer manipulation code.
        # TV is on line in
        # VCR is mic in
        # btaudio (different dsp device) will be added later
        mixer = plugin.getbyname('MIXER')
        
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
        
        self.prev_app = rc.app()
        rc.app(self)

        if osd.focused_app():
            osd.focused_app().hide()

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

        
        
    def Stop(self):
        mixer = plugin.getbyname('MIXER')
        mixer.setLineinVolume(0)
        mixer.setMicVolume(0)
        mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.mode = 'stop'
        self.thread.mode_flag.set()

        rc.app(self.prev_app)
        if osd.focused_app():
            osd.focused_app().show()

        while self.thread.mode == 'stop':
            time.sleep(0.05)
        print 'stopped %s app' % self.mode
        if os.path.exists('/tmp/freevo.wid'): os.unlink('/tmp/freevo.wid')


    def eventhandler(self, event):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        # if event == em.STOP or event == em.PLAY_END:
        if event == em.STOP:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return TRUE
        
        if event == em.PAUSE:
            self.thread.app.write('pause\n')
            return TRUE

        if event == em.SEEK:
            self.thread.app.write('seek %s\n' % event.arg)
            return TRUE

        elif event == em.TV_CHANNEL_UP or event == em.TV_CHANNEL_DOWN:
            if self.mode == 'vcr':
                return
            
            # Go to the prev/next channel in the list
            if event == em.TV_CHANNEL_UP:
                self.TunerNextChannel()
            else:
                self.TunerPrevChannel()
            
            #pause mplayer
            # self.thread.app.write('pause\n')

            new_channel = self.TunerGetChannel()
            print "setting channel %s" % new_channel
            self.videodev.setchannel(new_channel)

            # TODO: Set MPlayer to start of timeshift
            self.thread.app.write('seek 999999 0\n')
            # self.thread.app.write('seek 0 2\n')
            # self.thread.app.write('seek 100 1\n')

            # self.thread.app.write('pause\n')


            # Display a channel changed message
#            tuner_id, chan_name, prog_info = self.TunerGetChannelInfo()
#            now = time.strftime('%H:%M')
#            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
#            cmd = 'show_osd_msg "%s" 4000\n' % msg
#            self.thread.app.write(cmd)
            return TRUE
            
        elif event == em.TOGGLE_OSD:
            return FALSE
        
            # Display the channel info message
            # XXX Experimental, disabled for now
            tuner_id, chan_name, prog_info = self.TunerGetChannelInfo()
            now = time.strftime('%H:%M')
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'show_osd_msg "%s" 4000\n' % msg
            print 'msg = "%s" %s chars' % (msg, len(msg))
            self.thread.app.write(cmd)
            
        return FALSE
    

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
        self.timeshift = None #pyshift.pyshift_init('/tmp/timeshift.mpg',67108864) 
        self.tsinput   = None

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
               
                self.tsinput = os.popen(config.TIMESHIFT_ENCODE_CMD,'r')
                self.timeshift = pyshift.pyshift_init(config.TIMESHIFT_BUFFER,
                                       config.TIMESHIFT_BUFFER_SIZE * 1024*1024)
                self.app = MPlayerApp(self.command)
                
                while self.mode == 'play' and self.app.isAlive():
                    pyshift.pyshift_write(self.timeshift,self.tsinput.read(TIMESHIFT_CHUNKSIZE))
                    # XXX: What is Audioinfo used for in TV Code?
                    if self.audioinfo: 
                        if not self.audioinfo.pause:
                            self.audioinfo.draw()

                self.app.kill()
                # Shutdown Timeshifting and close devices
                pyshift.pyshift_close(self.timeshift)
                self.tsinput.close()
	        # Remove the buffer file
	        if os.path.exists('%s' % config.TIMESHIFT_BUFFER):
                    os.unlink('%s' % config.TIMESHIFT_BUFFER)

                # Ok, we can use the OSD again.
                if config.STOP_OSD_WHEN_PLAYING:
                    osd.restartdisplay()
                    osd.update()

                if self.mode == 'play':
                    if DEBUG: print 'posting play_end'
                    rc.post_event(em.PLAY_END)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'

