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
# Revision 1.5  2003/11/23 20:47:13  rshortt
# Another typo!
#
# Revision 1.4  2003/11/23 20:46:07  rshortt
# Dumb typo.
#
# Revision 1.3  2003/11/23 19:21:49  rshortt
# Add getChannelInfo, taken from a method of the mplayer tv plugin.  I have
# some changes to that as well which will use this one instead.
#
# Revision 1.2  2003/11/16 17:38:48  dischi
# i18n patch from David Sagnol
#
# Revision 1.1  2003/10/11 14:55:29  rshortt
# A new module to handle all of the channel requirements of Freevo from
# one place.  This will also be used as a layer between Freevo's channel
# list, frequency table, and custom frequencies and childapps like mplayer
# or tvtime.
#
# This is not used by anything by default and requires further work.
#
# Revision 1.2  2003/10/06 02:57:21  rshortt
# Almost in action...
#
# Revision 1.1  2003/09/19 02:22:20  rshortt
# thinking out loud
#
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
        # XXX: soon make TV_CHANNELS a list of real objects instead of a 
        #      list of lists.
        # self.TV_CHANNELS = the lists of objects or something
        self.chan_index = 0

        # XXX: Make sure plugin won't allow you to init any plugin
        #      more than once.  Also it might be better to move
        #      this init line into the recordserver since in the TV
        #      interface it will already be initialized in main.
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
                    group = chan_info[3]
                except:
                    # XXX: put a better exception here
                    group = 0

        return config.VIDEO_GROUPS[group]


    def chanUp(self, app=None, app_cmd=None):
        """
        Using this method will not support custom frequencies.
        """
        self.chanSet(self.getNextChannel(), app, app_cmd)


    def chanDown(self, app=None, app_cmd=None):
        """
        Using this method will not support custom frequencies.
        """
        self.setChannel(self.getPrevChannel(), app, app_cmd)


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
            if vg.input_type == 'tuner' and vg.tuner_chan:
                return self.tunerSetFreq(vg.tuner_chan, app, app_cmd)

            tuner = plugin.getbyname('EXTERNAL_TUNER')
            tuner.setChannel(new_chan)

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
            # freq = self.chanlist[str(chan)]
            freq = tv.freq.CHANLIST[vg.tuner_chanlist][str(chan)]
            if DEBUG:
                print 'USING STANDARD FREQUENCY: chan="%s", freq="%s"' % \
                      (chan, freq)

        # XXX: add code here for TUNER_LOW capability, the last time that I
        #      half-heartedly tried this it din't work as expected.
        freq *= 16
        freq /= 1000

        if app:
            if app_cmd:
                self.appSend(app, app_cmd)
            else:
                # If we have app and not app_cmd we return the frequency so
                # the caller (ie: mplayer/tvtime/mencoder plugin) can set it
                # or provide it on the command line.
                return freq
        else:
            # Letf set the freq ourselves using the V4L device.
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


    def getNextChannel(self):
        return config.TV_CHANNELS[(self.chan_index+1) % len(config.TV_CHANNELS)][2]


    def getPrevChannel(self):
        return (self.chan_index-1) % len(config.TV_CHANNELS)


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
