#if 0 /*
# -----------------------------------------------------------------------
# channels.py - Freevo module to handle channel changing.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.13  2004/02/05 14:23:50  outlyer
# Patch from Viggo Fredriksen
#
# o Move to ChildApp2 for mplayer TV plugin
# o Channel changing via the number pad on the remote
#
# Revision 1.12  2004/02/04 14:11:19  outlyer
# Cleanup and fixup:
#
# o Now uses the mplayer OSD to show channel information when changing channels,
#     or you press the 'display' key.
# o Removed many old CVS log messages
# o Removed many debug-related 'print' statements
#
# Revision 1.11  2003/12/31 16:08:08  rshortt
# Use a fifth field in TV_CHANNELS to specify an optional VideoGroup
# (VIDEO_GROUPS index).  Also fix a frequency bug in channels.py.
#
# Revision 1.10  2003/11/25 16:32:33  rshortt
# Make plugin_external_tuner work again.
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

import config, plugin
import tv.freq, tv.v4l2
import epg_xmltv
import time

DEBUG = config.DEBUG

# Sample from local_conf.py:
#VIDEO_GROUPS = [
#    VideoGroup(vdev='/dev/video0',
#               adev=None,
#               input_type='tuner',
#               tuner_type='external',
#               tuner_chan='3',
#               desc='Bell ExpressVu',
#               recordable=True),
#    VideoGroup(vdev='/dev/video1',
#               adev='/dev/dsp1',
#               input_type='tuner',
#               desc='ATI TV-Wonder',
#               recordable=True),
#    VideoGroup(vdev='/dev/video2',
#               adev=None,
#               input_type='webcam',
#               desc='Logitech Quickcam',
#               recordable=False),
#]

class FreevoChannels:

    def __init__(self):
        self.chan_index = 0

        if config.plugin_external_tuner: 
            plugin.init_special_plugin(config.plugin_external_tuner)


    def getVideoGroup(self, chan):
        """
        Gets the VideoGroup object used by this Freevo channel.
        """
        group = 0

        for i in range(len(config.TV_CHANNELS)):
            chan_info = config.TV_CHANNELS[i]
            if chan_info[2] == chan:
                try:
                    group = int(chan_info[4])
                except:
                    # XXX: put a better exception here
                    group = 0

        return config.VIDEO_GROUPS[group]


    def chanUp(self, app=None, app_cmd=None):
        """
        Using this method will not support custom frequencies.
        """
        return self.chanSet(self.getNextChannel(), app, app_cmd)


    def chanDown(self, app=None, app_cmd=None):
        """
        Using this method will not support custom frequencies.
        """
        return self.chanSet(self.getPrevChannel(), app, app_cmd)


    def chanSet(self, chan, app=None, app_cmd=None):
        new_chan = None

        for pos in range(len(config.TV_CHANNELS)):
            chan_cfg = config.TV_CHANNELS[pos]
            if chan_cfg[2] == chan:
                new_chan = chan
                self.chan_index = pos

        if not new_chan:
            print _('ERROR: Cannot find tuner channel "%s" in the TV channel listing') % chan
            return

        vg = self.getVideoGroup(new_chan)

        if vg.tuner_type == 'external':
            tuner = plugin.getbyname('EXTERNAL_TUNER')
            tuner.setChannel(new_chan)

            if vg.input_type == 'tuner' and vg.tuner_chan:
                freq = self.tunerSetFreq(vg.tuner_chan, app, app_cmd)
                return freq

            return 0

        else:
            return self.tunerSetFreq(chan, app, app_cmd)

        return 0


    def tunerSetFreq(self, chan, app=None, app_cmd=None):
        vg = self.getVideoGroup(chan)

        freq = config.FREQUENCY_TABLE.get(chan)
        if freq:
            if DEBUG:
                print 'USING CUSTOM FREQUENCY: chan="%s", freq="%s"' % \
                      (chan, freq)
        else:
            freq = tv.freq.CHANLIST[vg.tuner_chanlist][str(chan)]
            if DEBUG:
                print 'USING STANDARD FREQUENCY: chan="%s", freq="%s"' % \
                      (chan, freq)

        if app:
            if app_cmd:
                self.appSend(app, app_cmd)
            else:
                # If we have app and not app_cmd we return the frequency so
                # the caller (ie: mplayer/tvtime/mencoder plugin) can set it
                # or provide it on the command line.
                return freq
        else:
            # XXX: add code here for TUNER_LOW capability, the last time that I
            #      half-heartedly tried this it din't work as expected.
            # XXX Moved here by Krister, only return actual values
            freq *= 16
            freq /= 1000

            # Lets set the freq ourselves using the V4L device.
            try:
                vd = tv.v4l2.Videodev(vg.vdev)
                try:
                    vd.setfreq(freq)
                except:
                    vd.setfreq_old(freq)
                vd.close()
            except:
                print _('Failed to set freq for channel %s') % chan

        return 0


    def getChannel(self):
        return config.TV_CHANNELS[self.chan_index][2]

    def getManChannel(self,channel=0):
        return config.TV_CHANNELS[(channel-1) % len(config.TV_CHANNELS)][2]

    def getNextChannel(self):
        return config.TV_CHANNELS[(self.chan_index+1) % len(config.TV_CHANNELS)][2]


    def getPrevChannel(self):
        return config.TV_CHANNELS[(self.chan_index-1) % len(config.TV_CHANNELS)][2]


    def setChanlist(self, chanlist):
        self.chanlist = freq.CHANLIST[chanlist]


    def appSend(self, app, app_cmd):
        if not app or not app_cmd:
            return

        app.write(app_cmd)


    def getChannelInfo(self):
        '''Get program info for the current channel'''

        tuner_id = self.getChannel()
        chan_name = config.TV_CHANNELS[self.chan_index][1]
        chan_id = config.TV_CHANNELS[self.chan_index][0]

        channels = epg_xmltv.get_guide().GetPrograms(start=time.time(),
                                               stop=time.time(), chanids=[chan_id])

        if channels and channels[0] and channels[0].programs:
            start_s = time.strftime('%H:%M', time.localtime(channels[0].programs[0].start))
            stop_s = time.strftime('%H:%M', time.localtime(channels[0].programs[0].stop))
            ts = '(%s-%s)' % (start_s, stop_s)
            prog_info = '%s %s' % (ts, channels[0].programs[0].title)
        else:
            prog_info = 'No info'

        return tuner_id, chan_name, prog_info





# fc = FreevoChannels()
# print 'CHAN: %s' % fc.getChannel()
# fc.chanSet('780')
# print 'CHAN: %s' % fc.getChannel()
