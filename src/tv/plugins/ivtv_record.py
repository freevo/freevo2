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
# Revision 1.28  2004/07/26 18:10:19  dischi
# move global event handling to eventhandler.py
#
# Revision 1.27  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.26  2004/06/28 18:23:34  rshortt
# I guess this shouldn't be in here since its back in recordserver.
#
# Revision 1.25  2004/06/23 19:07:05  outlyer
# The snapshot in the event doesn't work. I've tried it numerous times, and it
# is being killed before completing.
#
# Did no one else actually try this change?
#
# Revision 1.24  2004/06/22 01:05:51  rshortt
# Get the filename from tv_util.getProgFilename().
#
# Revision 1.23  2004/06/10 02:32:17  rshortt
# Add RECORD_START/STOP events along with VCR_PRE/POST_REC commands.
#
# Revision 1.22  2004/06/07 16:46:00  rshortt
# Didn't mean to add partial support for multiple recording plugins yet.
#
# Revision 1.21  2004/06/07 16:10:51  rshortt
# Change 'RECORD' to plugin.RECORD.
#
# Revision 1.20  2004/05/28 01:48:22  outlyer
# Florian Demmer's patch for consecutive recordings and a patch to move the
# snapshot to after we set the flag to idle, just to be safe.
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
import util.tv_util as tv_util

from event import Event
from tv.channels import FreevoChannels

DEBUG = config.DEBUG

CHUNKSIZE = 65536


class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)

        plugin.register(Recorder(), plugin.RECORD)


class Recorder:

    def __init__(self):
        # Disable this plugin if not loaded by record_server.
        if string.find(sys.argv[0], 'recordserver') == -1:
            return

        if DEBUG: print 'ACTIVATING IVTV RECORD PLUGIN'

        self.thread = Record_Thread()
        self.thread.setDaemon(1)
        self.thread.mode = 'idle'
        self.thread.start()
        

    def Record(self, rec_prog):
        # It is safe to ignore config.TV_RECORDFILE_SUFFIX here.
        rec_prog.filename = os.path.splitext(tv_util.getProgFilename(rec_prog))[0] + '.mpeg'

        self.thread.mode = 'record'
        self.thread.prog = rec_prog
        self.thread.mode_flag.set()
        
        if DEBUG: print('Recorder::Record: %s' % rec_prog)
        

    def Stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()



class Record_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.prog = None
        self.app = None


    def run(self):
        while 1:
            if DEBUG: print('Record_Thread::run: mode=%s' % self.mode)
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'record':
                eventhandler.post(Event('RECORD_START', arg=self.prog))
                if DEBUG: print 'Record_Thread::run: started recording'

                fc = FreevoChannels()
                if DEBUG: print 'CHAN: %s' % fc.getChannel()

                (v_norm, v_input, v_clist, v_dev) = config.TV_SETTINGS.split()

                v = tv.ivtv.IVTV(v_dev)

                v.init_settings()
                vg = fc.getVideoGroup(self.prog.tunerid)

                if DEBUG: print 'Setting Input to %s' % vg.input_num
                v.setinput(vg.input_num)

                if DEBUG: print 'Setting Channel to %s' % self.prog.tunerid
                fc.chanSet(str(self.prog.tunerid))

                if DEBUG: v.print_settings()

                now = time.time()
                stop = now + self.prog.rec_duration

                time.sleep(2)

                v_in  = open(v_dev, 'r')
                v_out = open(self.prog.filename, 'w')

                while time.time() < stop:
                    buf = v_in.read(CHUNKSIZE)
                    v_out.write(buf)
                    if self.mode == 'stop':
                        break

                v_in.close()
                v_out.close()
                v.close()
                v = None

                self.mode = 'idle'

                eventhandler.post(Event('RECORD_STOP', arg=self.prog))
                if DEBUG: print('Record_Thread::run: finished recording')

            else:
                self.mode = 'idle'

            time.sleep(0.5)
