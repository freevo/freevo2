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
# Revision 1.36  2004/07/04 08:15:29  dischi
# add config.MPLAYER_ARGS_DEF (why was that missing?)
#
# Revision 1.35  2004/06/28 17:12:22  dischi
# reduce cache for dvb
#
# Revision 1.34  2004/06/25 20:03:33  dischi
# basic dvb support
#
# Revision 1.33  2004/02/13 17:36:54  dischi
# fixed crash on stop
#
# Revision 1.32  2004/02/05 14:23:50  outlyer
# Patch from Viggo Fredriksen
#
# o Move to ChildApp2 for mplayer TV plugin
# o Channel changing via the number pad on the remote
#
# Revision 1.31  2004/02/04 14:11:19  outlyer
# Cleanup and fixup:
#
# o Now uses the mplayer OSD to show channel information when changing channels,
#     or you press the 'display' key.
# o Removed many old CVS log messages
# o Removed many debug-related 'print' statements
#
# Revision 1.30  2003/12/31 16:13:15  rshortt
# Make it possible to change channels between those that have different
# VideoGroups.  For example, on my setup channel 3 is my webcam, 4-50 is
# analog cable, and 200+ is my satellite system.  I can start on channel 3,
# see my webcam on the tv (security cam), channel+ and instantly view my
# cable channels and channel+ through to my satellite channels.
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
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        self.app_mode = 'tv'
        self.fc = FreevoChannels()
        self.current_vg = None


    def Play(self, mode, tuner_channel=None):

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
                config.MPLAYER_VO_DEV_OPTS, config.MPLAYER_ARGS_DEF)

        if mode == 'tv':
            if vg.group_type == 'ivtv':
                ivtv_dev = ivtv.IVTV(vg.vdev)
                ivtv_dev.init_settings()
                ivtv_dev.setinput(vg.input_num)
                #ivtv_dev.print_settings()
                self.fc.chanSet(tuner_channel)
            
                tvcmd = vg.vdev

                if config.MPLAYER_ARGS.has_key('ivtv'):
                    args += (config.MPLAYER_ARGS['ivtv'],)

            elif vg.group_type == 'webcam':
                self.fc.chanSet(tuner_channel, app='mplayer')
                tvcmd = ''

                if config.MPLAYER_ARGS.has_key('webcam'):
                    args += (config.MPLAYER_ARGS['webcam'],)

            elif vg.group_type == 'dvb':
                self.fc.chanSet(tuner_channel, app='mplayer')
                tvcmd = ''
                args += ('"dvb://%s" -vf pp=de/fd -cache 1024' % tuner_channel,)

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

        mpl = '--prio=%s %s -vo %s%s -fs %s -slave %s %s' % args

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
        self.app = childapp.ChildApp2(command)
        
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



    def Stop(self, channel_change=0):
        mixer = plugin.getbyname('MIXER')
        if mixer and not channel_change:
            mixer.setLineinVolume(0)
            mixer.setMicVolume(0)
            mixer.setIgainVolume(0) # Input on emu10k cards.

        self.app.stop('quit\n')

        rc.app(self.prev_app)
        if osd.focused_app() and not channel_change:
            osd.focused_app().show()

        if os.path.exists('/tmp/freevo.wid'): os.unlink('/tmp/freevo.wid')


    def eventhandler(self, event, menuw=None):
        s_event = '%s' % event

        if event == em.STOP or event == em.PLAY_END:
            self.Stop()
            rc.post_event(em.PLAY_END)
            return TRUE

        elif event in [ em.TV_CHANNEL_UP, em.TV_CHANNEL_DOWN] or s_event.startswith('INPUT_'):
            if event == em.TV_CHANNEL_UP:
                nextchan = self.fc.getNextChannel()
            elif event == em.TV_CHANNEL_DOWN:
                nextchan = self.fc.getPrevChannel()
            else:
                chan = int( s_event[6] )
                nextchan = self.fc.getManChannel(chan)

            nextvg = self.fc.getVideoGroup(nextchan)

            if self.current_vg != nextvg:
                self.Stop(channel_change=1)
                self.Play('tv', nextchan)
                return TRUE

            if self.mode == 'vcr':
                return
            
            elif self.current_vg.group_type == 'dvb':
                self.Stop(channel_change=1)
                self.Play('tv', nextchan)
                return TRUE

            elif self.current_vg.group_type == 'ivtv':
                self.fc.chanSet(nextchan)
                self.app.write('seek 999999 0\n')

            else:
                freq_khz = self.fc.chanSet(nextchan, app=self.app)
                new_freq = '%1.3f' % (freq_khz / 1000.0)
                self.app.write('tv_set_freq %s\n' % new_freq)

            self.current_vg = self.fc.getVideoGroup(self.fc.getChannel())

            # Display a channel changed message
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            now = time.strftime('%H:%M')
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'osd_show_text "%s"\n' % msg
            self.app.write(cmd)
            return TRUE

        elif event == em.TOGGLE_OSD:
            # Display the channel info message
            tuner_id, chan_name, prog_info = self.fc.getChannelInfo()
            now = time.strftime('%H:%M')
            msg = '%s %s (%s): %s' % (now, chan_name, tuner_id, prog_info)
            cmd = 'osd_show_text "%s"\n' % msg
            self.app.write(cmd)
            return FALSE
            
        return FALSE
    
