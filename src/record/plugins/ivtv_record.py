# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# ivtv_record.py - A plugin to record tv using an ivtv based card.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/08/23 01:37:21  rshortt
# -Use new TV_SETTINGS.
# -You may now register this plugin with an arg called types which is a list of
#  all the types it will record for, defaulting to ['ivtv0','ivtv1','ivtv2'].
# -Change the channel or post an event for another plugin to do so (external tuner).
# -Honour passthrough mode if recording from an external cable box or something.
#
# Revision 1.3  2004/08/09 11:58:15  rshortt
# Clean comments and add one.
#
# Revision 1.2  2004/08/08 19:07:08  rshortt
# The first new recording plugin:
#
# -Asynchronous / non-blocking design, no threads.
# -Relies on poll().
# -Impliments an eventhandler.
# -Will handle recordings on multiple devices.
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


import sys, string
import random
import time, os
import threading
import signal

import config
import tv.ivtv
import childapp 
import plugin 
import eventhandler
from event import *
import util.tv_util as tv_util
from event import Event
from tv.channels import get_actual_channel

DEBUG = config.DEBUG

# TODO:  Calculate CHUNKSIZE based on the configured ivtv bitrate/max bitrate
#        and the poll_interval of the plugin.  The size of the ivtv encoding 
#        buffer (in the driver or card) does matter here.  If we don't read
#        enough data on each poll() it will overflow, if we read too much the
#        plugin will block for too long.  The value of 65536 is working quite
#        well for me with a constant bitrate of 4.5 Mb/sec and 0.1 sec poll().
CHUNKSIZE = 65536


class IVTVRecordSession:

    def __init__(self, prog, type):
        self.prog = prog
        self.type = type
        self.v_in = None
        self.v_out = None
        self.ivtv = None
        self.mode = 'idle'


    def poll(self):
        if self.mode == 'idle':
            pass
                
        elif self.mode == 'stop':
            self.v_in.close()
            self.v_out.close()
            self.ivtv.close()
            self.ivtv = None
            self.stop_time = 0

            self.mode = 'over'

            eventhandler.post(Event('RECORD_STOP', arg=(self.prog, self.type)))
            if DEBUG: print('IVTV: finished recording')

        elif self.mode == 'start':
            eventhandler.post(Event('RECORD_START', arg=(self.prog, self.type)))
            if DEBUG: print 'IVTV: started recording'

            self.ivtv = tv.ivtv.IVTV(self.type)
            self.ivtv.init_settings()

            chan = get_actual_channel(self.type, self.prog.channel_id)
            if self.ivtv.settings.input_name == 'tuner':
                passthrough_chan = self.ivtv.settings.passthrough
                if passthrough_chan:
                    self.ivtv.setchannel(passthrough_chan)
                    eventhandler.post(Event('CHAN_SWITCH', arg=(self.type, chan)))
                else:
                    self.ivtv.setchannel(self.prog.tunerid)

            else:
                eventhandler.post(Event('CHAN_SWITCH', arg=(self.type, chan)))


            if DEBUG: self.ivtv.print_settings()

            self.stop_time = time.time() + self.prog.rec_duration

            self.v_in  = open(self.ivtv.settings.vdev, 'r', \
                              os.O_RDONLY | os.O_NONBLOCK)
            self.v_out = open(self.prog.filename, 'w')

            self.mode = 'recording'

        elif self.mode == 'recording':
            if time.time() >= self.stop_time:
                self.mode = 'stop'

            buf = self.v_in.read(CHUNKSIZE)
            self.v_out.write(buf)

        else:
            self.mode = 'idle'


class PluginInterface(plugin.DaemonPlugin):

    def __init__(self, types=['ivtv0','ivtv1','ivtv2']):
        plugin.DaemonPlugin.__init__(self)
        self.poll_menu_only = False
        self.poll_interval = 1
        self.sessions = {}
        self.event_listener = True
        self.chan_types = []

        if isinstance(types, list) or isinstance(types, tuple):
            for t in types:
                self.chan_types.append(t)
        else:
            self.chan_types.append(types)

        plugin.register(self, plugin.RECORD)

        if DEBUG: print 'ACTIVATING IVTV RECORD PLUGIN'


    def Record(self, prog, type):
        if DEBUG: print('IVTV: %s' % prog)

        # XXX TODO:
        #  1) Find out what URL the prog is on (ivtv:/ivtv0:/ivtv1:).
        #  2) Key self.sessions based on available devices.
        #  3) See if the one we'd like to use is free.
        #  4) Start a recording session if we're allowed.
        #  5) This should support multiple recordings from different cards.

        if isinstance(self.sessions.get(type), IVTVRecordSession):
            print 'Sorry, already recording on %s.' % type
            return

        # It is safe to ignore config.TV_RECORDFILE_SUFFIX here.
        prog.filename = os.path.splitext(tv_util.getProgFilename(prog))[0] + '.mpeg'

        self.sessions[type] = IVTVRecordSession(prog, type)
        self.sessions[type].mode = 'start'
        

    def Stop(self, sname):
        session = self.sessions.get(sname)
        if isinstance(session, IVTVRecordSession):
            session.mode = 'stop'


    def poll(self):
        # if DEBUG: print 'IVTV: poll!'
        for s_k, s_v in self.sessions.items():
            s_v.poll()
            if s_v.mode == 'over':
                if DEBUG: print 'IVTV: found a finished job, deleting'
                del self.sessions[s_k]
                if DEBUG: print 'IVTV: sessions - %s' % self.sessions.keys()


    def eventhandler(self, event):
        if DEBUG: print 'IVTV: recorder heard event %s' % str(event)

        if event == RECORD:
            prog = event.arg[0]
            type = event.arg[1]

            if not type in self.chan_types:
                _debug_('Ignoring RECORD event for %s' % which)
                return

            self.Record(prog, type)

        elif event == STOP_RECORDING:
            prog = event.arg[0]
            type = event.arg[1]
            self.Stop(type)






