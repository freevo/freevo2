# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# xawtv.py - use xawtv for tv viewing
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2004/07/26 18:10:19  dischi
# move global event handling to eventhandler.py
#
# Revision 1.6  2004/07/25 19:47:40  dischi
# use application and not rc.app
#
# Revision 1.5  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.4  2004/06/06 17:18:39  mikeruelle
# removing unnecessary and bad kill method
#
# Revision 1.3  2004/03/21 23:03:23  mikeruelle
# docs fro devels, this is not for newbs yet
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


import config
import time, os
import string
import signal
import re

import util    # Various utilities
      # The RemoteControl class.
import childapp # Handle child applications
import tv.epg_xmltv as epg # The Electronic Program Guide
import event as em
from tv.channels import FreevoChannels

import plugin
import eventhandler

# Set to 1 for debug output
DEBUG = config.DEBUG

class PluginInterface(plugin.Plugin):
    """
    Plugin to watch tv with xawtv. very beta use at your own risk.
    to activate:
    plugin.activate('tv.xawtv', args=('/usr/bin/xawtv', '/usr/bin/xawtv-remote',))

    replace the paths for the programs fo wherever you installed them.
    currently only remote support really works well. Keyboard is taken by
    xawtv so you have to know its keys. Also you need a .xawtv file in the
    homedir of whoever is running the program. it must be synced up with your
    tv_channels variable or you will get wierd behavior. Only base video
    groups functionality on startup and no vg switching on ch+/ch- at the
    moment.
    """
    def __init__(self, app, remote):
        plugin.Plugin.__init__(self)

	#XXX might want to check to see if .xawtv present.
	# we really don't have much of a prayer if it isn't

        # create the xawtv object and register it
        plugin.register(Xawtv(app, remote), plugin.TV)

class Xawtv:

    __muted    = 0
    __igainvol = 0
    
    def __init__(self, app, remote):
        self.tuner_chidx = 0    # Current channel, index into config.TV_CHANNELS
        self.app_mode = 'tv'
	self.fc = FreevoChannels()
        self.current_vg = None
	self.xawtv_prog = app
	self.remote_prog = remote

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
        if not tuner_channel:
            tuner_channel = self.fc.getChannel()
        vg = self.current_vg = self.fc.getVideoGroup(tuner_channel)

        if not vg.group_type == 'normal':
            print 'Xawtv only supports normal. "%s" is not implemented' % vg.group_type
            return

        if mode == 'tv' or mode == 'vcr':
            
            w, h = config.TV_VIEW_SIZE
	    cf_norm = vg.tuner_norm
	    cf_input = vg.input_num
	    cf_device = vg.vdev

            s_norm = cf_norm.upper()

            if mode == 'vcr':
	        cf_input = '1'
		if hasattr(config, "TV_VCR_INPUT_NUM") and config.TV_VCR_INPUT_NUM:
		    cf_input = config.TV_VCR_INPUT_NUM

            if hasattr(config, "TV_XAWTV_OPTS") and config.TV_XAWTV_OPTS:
	        daoptions = config.TV_XAWTV_OPTS
            else:
	        daoptions = '-xv -f'

            command = '%s %s -device %s ' % (self.xawtv_prog,
	                                     daoptions,
                                             cf_device)

        else:
            print 'Mode "%s" is not implemented' % mode  # BUG ui.message()
            return

        self.mode = mode

        mixer = plugin.getbyname('MIXER')

        # BUG Mixer manipulation code.
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
        self.app=XawtvApp(command, self.remote_prog)        

	if tuner_channel:
	    time.sleep(0.5)
	    self.app.sendcmd('setstation %s' % tuner_channel)
        #XXX use remote to change the input we want

        eventhandler.append(self)

        # Suppress annoying audio clicks
        time.sleep(0.4)
        # BUG Hm.. This is hardcoded and very unflexible.
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

        self.app.stop()
        eventhandler.remove(self)

    def eventhandler(self, event, menuw=None):
        _debug_('%s: %s app got %s event' % (time.time(), self.mode, event))
        if event == em.STOP or event == em.PLAY_END:
            self.app.sendcmd('quit')
            time.sleep(1)
            self.Stop()
            eventhandler.post(em.PLAY_END)
            return True
        
        elif event == em.TV_CHANNEL_UP or event == em.TV_CHANNEL_DOWN:
            if self.mode == 'vcr':
                return
             
            if event == em.TV_CHANNEL_UP:
                self.TunerPrevChannel()
                self.app.sendcmd('setstation next')
            else:
                self.TunerNextChannel()
                self.app.sendcmd('setstation prev')
	    
            return True
            
        elif event == em.TOGGLE_OSD:
	    #try to send channel name
            self.app.sendcmd('msg \'%s\'' % self.TunerGetChannel())
            return True
        
        elif event == em.OSD_MESSAGE:
            self.app.sendcmd('msg \'%s\'' % event.arg)
            return True
       
        elif event in em.INPUT_ALL_NUMBERS:
            self.app.sendcmd('keypad %s' % event.arg)
	    
        elif event == em.BUTTON:
            if event.arg == 'PREV_CH':
                self.app.sendcmd('setstation back')
                return True
	        

        return False
        
            

# ======================================================================
class XawtvApp(childapp.ChildApp2):
    """
    class controlling the in and output from the xawtv process
    """

    def __init__(self, app, remote):
        self.remote = remote
        childapp.ChildApp2.__init__(self, app, stop_osd=1)

    def sendcmd(self, cmd):
        os.system('%s %s' % (self.remote, cmd))
