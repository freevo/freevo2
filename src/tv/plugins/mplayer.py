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
# Revision 1.29  2003/11/27 03:11:08  rshortt
# Shuffle things around a little bit and add ivtv capabilities.  I intend to
# depricate the ivtv_basic_tv plugin in favour of this once since that is
# just an mplayer plugin as well and I don't want to duplicate too much code.
#
# I will focus my development effort on this plugin instead of ivtv_basic_tv
# and will also be really using this one so I can test it out myself. :)
#
# I am planning on adding dvb support to this plugin as well.
#
# Revision 1.28  2003/11/25 09:37:00  krister
# Bugfixes, works for me now
#
# Revision 1.26.2.3  2003/11/25 01:24:12  rshortt
# Some further fixes and improvements, aldo removed MPLAYER_DEBUG since
# ChildApp does this now.
#
# Please test if you can.  VideoGroup configuration is still much undocumented
# but I am planning to do so.  Ping me if you need a quick hand.
#
# To test this you must check it out by:
# cvs update -r rob src/tv/plugins/mplayer.py
#
# Revision 1.26.2.2  2003/11/24 17:16:40  rshortt
# Bugfixes.
#
# Revision 1.26.2.1  2003/11/24 13:25:00  rshortt
# Some unstable changes on a branch.
#
# Revision 1.24  2003/11/23 19:53:01  rshortt
# Move some code into src/tv/channels.py and also make use of Freevo's
# frequency tables (and custom frequencies).
#
# This plugin indirectly makes use of the new VIDEO_GROUPS config item.
#
# Please test.  I don't have the setup to test this myself.
#
# Revision 1.23  2003/11/06 06:08:38  krister
# Added testcode for viewing the VCR/Composite1 input on the TV card
#
# Revision 1.22  2003/10/28 16:08:14  mikeruelle
# convert to new thread system
#
# Revision 1.21  2003/10/12 09:54:27  dischi
# BSD patches from Lars
#
# Revision 1.20  2003/09/14 01:38:59  outlyer
# More FreeBSD support from Lars
#
# Revision 1.19  2003/09/03 17:54:38  dischi
# Put logfiles into LOGDIR not $FREEVO_STARTDIR because this variable
# doesn't exist anymore.
#
# Revision 1.18  2003/09/02 20:29:53  dischi
# only use mixer if we have one
#
# Revision 1.17  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.16  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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
import threading
import signal

import util    # Various utilities
import osd     # The OSD class, used to communicate with the OSD daemon
import rc      # The RemoteControl class.
import event as em
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide
from tv.channels import FreevoChannels
import tv.ivtv as ivtv
 
import plugin

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


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
        self.thread = childapp.ChildThread()
        self.thread.stop_osd = True
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        self.app_mode = 'tv'
        self.fc = FreevoChannels()
        self.current_vg = None


    def Play(self, mode, tuner_channel=None, channel_change=0):

        if not tuner_channel:
            tuner_channel = self.fc.getChannel()
            
        vg = self.current_vg = self.fc.getVideoGroup(tuner_channel)


        # Convert to MPlayer TV setting strings
        norm = 'norm=%s' % vg.tuner_norm
        input = 'input=%s' % vg.input_num
        device= 'device=%s' % vg.vdev
            
        w, h = config.TV_VIEW_SIZE
        outfmt = 'outfmt=%s' % config.TV_VIEW_OUTFMT

        # Build the MPlayer command
        args = (config.MPLAYER_NICE, config.MPLAYER_CMD, config.MPLAYER_VO_DEV,
                config.MPLAYER_VO_DEV_OPTS)

        if mode == 'tv':
            if vg.group_type == 'ivtv':
                ivtv_dev = ivtv.IVTV(vg.vdev)
                ivtv_dev.init_settings()
                ivtv_dev.print_settings()
                self.fc.chanSet(tuner_channel)
            
                tvcmd = vg.vdev

                if config.MPLAYER_ARGS.has_key('ivtv'):
                    args += (config.MPLAYER_ARGS['ivtv'],)

            else:
                freq_khz = self.fc.chanSet(tuner_channel, app='mplayer')
                tuner_freq = '%1.3f' % (freq_khz / 1000.0)

                tvcmd = ('tv:// -tv driver=%s:freq=%s:%s:%s:'
                         '%s:width=%s:height=%s:%s %s' %
                         (config.TV_DRIVER, tuner_freq, device, input, norm, 
                          w, h, outfmt, config.TV_OPTS))

                if config.MPLAYER_ARGS.has_key('tv'):
                    args += (config.MPLAYER_ARGS['tv'],)


        elif mode == 'vcr':
            tvcmd = ('tv:// -tv driver=%s:%s:%s:'
                     '%s:width=%s:height=%s:%s %s' %
                     (config.TV_DRIVER, device, input, norm, 
                      w, h, outfmt, config.TV_OPTS))

            if config.MPLAYER_ARGS.has_key('tv'):
                args += (config.MPLAYER_ARGS['tv'],)

        else:
            print 'Mode "%s" is not implemented' % mode  # XXX ui.message()
            return

        args += (tvcmd,)
 
        mpl = '--prio=%s %s -vo %s%s -fs %s -slave %s' % args

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
        self.thread.start(MPlayerApp, (command))        
        
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
        if mixer:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.thread.stop('quit\n')

        rc.app(self.prev_app)
        if osd.focused_app():
            osd.focused_app().show()

        print 'stopped %s app' % self.mode
        if os.path.exists('/tmp/freevo.wid'): os.unlink('/tmp/freevo.wid')


    def eventhandler(self, event, menuw=None):
        print '%s: %s app got %s event' % (time.time(), self.mode, event)
        if event == em.STOP or event == em.PLAY_END:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return TRUE
        
        elif event == em.TV_CHANNEL_UP or event == em.TV_CHANNEL_DOWN:
            # XXX: channel Up/Down code will have to be reworked in order
            #      to handle multiple VideoGroups between channels.

            if self.mode == 'vcr':
                return
            
            elif self.current_vg.group_type == 'ivtv':
                # Go to the prev/next channel in the list
                if event == em.TV_CHANNEL_UP:
                    self.fc.chanUp()
                else:
                    self.fc.chanDown()
    
                self.thread.app.write('seek 999999 0\n')

            else:
                # Go to the prev/next channel in the list
                if event == em.TV_CHANNEL_UP:
                    freq_khz = self.fc.chanUp(app=self.thread.app)
                else:
                    freq_khz = self.fc.chanDown(app=self.thread.app)
    
                new_freq = '%1.3f' % (freq_khz / 1000.0)
                self.thread.app.write('tv_set_freq %s\n' % new_freq)

            self.current_vg = self.fc.getVideoGroup(self.fc.getChannel())

            # Display a channel changed message
            # XXX Experimental, disabled for now
            #tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            #now = time.strftime('%H:%M')
            #msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            #cmd = 'show_osd_msg "%s" 4000\n' % msg
            #self.thread.app.write(cmd)
            return TRUE
            
        elif event == em.TOGGLE_OSD:
            return FALSE
        
            # Display the channel info message
            # XXX Experimental, disabled for now
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
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
        childapp.ChildApp.__init__(self, app)
        

    def kill(self):
        # Use SIGINT instead of SIGKILL to make sure MPlayer shuts
        # down properly and releases all resources before it gets
        # reaped by childapp.kill().wait()
        self.write('quit')
        childapp.ChildApp.kill(self, signal.SIGINT)

        # XXX Krister testcode for proper X11 video
        if DEBUG: print 'Killing mplayer'


