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
#from tv.channels import FreevoChannels

DEBUG = config.DEBUG

# XXX:  Calculate CHUNKSIZE based on the configured ivtv bitrate/max bitrate
#       and the poll_interval of the plugin.  The size of the ivtv encoding 
#       buffer (in the driver or card) does matter here.  If we don't read
#       enough data on each poll() it will overflow, if we read too much the
#       plugin will block for too long.  The value of 65536 is working quite
#       well for me with a constant bitrate of 4.5 Mb/sec and 0.1 sec poll().
CHUNKSIZE = 65536


class IVTVRecordSession:

    def __init__(self, prog):
        self.prog = prog
        self.v_in = None
        self.v_out = None
        self.vdev = None
        self.mode = 'idle'


    def poll(self):
        if self.mode == 'idle':
            pass
                
        elif self.mode == 'stop':
            self.v_in.close()
            self.v_out.close()
            self.vdev.close()
            self.vdev = None
            self.stop_time = 0

            self.mode = 'over'

            eventhandler.post(Event('RECORD_STOP', arg=self.prog))
            if DEBUG: print('IVTV: finished recording')

        elif self.mode == 'start':
            eventhandler.post(Event('RECORD_START', arg=self.prog))
            if DEBUG: print 'IVTV: started recording'

            #fc = FreevoChannels()
            #if DEBUG: print 'CHAN: %s' % fc.getChannel()

            (v_norm, v_input, v_clist, v_dev) = config.TV_SETTINGS.split()

            self.vdev = tv.ivtv.IVTV(v_dev)

            self.vdev.init_settings()
            #vg = fc.getVideoGroup(self.prog.tunerid)

            #if DEBUG: print 'Setting Input to %s' % vg.input_num
            self.vdev.setinput(4)

            if DEBUG: print 'Setting Channel to %s' % self.prog.tunerid
            #fc.chanSet(str(self.prog.tunerid))

            if DEBUG: self.vdev.print_settings()

            self.stop_time = time.time() + self.prog.rec_duration

            self.v_in  = open(v_dev, 'r', os.O_RDONLY | os.O_NONBLOCK)
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

    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.poll_menu_only = False
        self.poll_interval = 1
        self.sessions = {}
        self.event_listener = True

        plugin.register(self, plugin.RECORD)

        if DEBUG: print 'ACTIVATING IVTV RECORD PLUGIN'


    def Record(self, rec_prog):
        if DEBUG: print('IVTV: %s' % rec_prog)

        # It is safe to ignore config.TV_RECORDFILE_SUFFIX here.
        rec_prog.filename = os.path.splitext(tv_util.getProgFilename(rec_prog))[0] + '.mpeg'

        # XXX TODO:
        #  1) Find out what URL the prog is on (ivtv:/ivtv0:/ivtv1:).
        #  2) Key self.sessions based on available devices.
        #  3) See if the one we'd like to use is free.
        #  4) Start a recording session if we're allowed.
        #  5) This should support multiple recordings from different cards.

        if isinstance(self.sessions.get('ivtv'), IVTVRecordSession):
            print 'Sorry, already recording on ivtv.'
            return

        self.sessions['ivtv'] = IVTVRecordSession(rec_prog)
        self.sessions['ivtv'].mode = 'start'
        

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
            self.Record(event.arg)

        elif event == STOP_RECORDING:
            self.Stop('ivtv')






