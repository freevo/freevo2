
#if 0 /*
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
# Revision 1.8  2003/07/14 11:44:42  rshortt
# Add some init and print methods to Videodev and IVTV.
#
# Revision 1.7  2003/07/11 02:16:51  rshortt
# Removing audio problem workaround because it is no longer needed.
#
# Revision 1.6  2003/07/07 01:59:06  rshortt
# Updating for current ivtv CVS, added bitrate_mode and use constant bitrate
# by default.
#
# Revision 1.5  2003/06/08 17:01:50  rshortt
# A workaround for a strange audio problem and print more codec info.
#
# Revision 1.4  2003/06/05 00:04:46  rshortt
# Create the tv lock file so the idlebar plugin will know. :)
#
# Revision 1.3  2003/06/01 16:05:40  rshortt
# Further suport for ivtv based cards.  Now you can set the bitrate to encode at or the stream type to use.
#
# Revision 1.2  2003/05/29 12:08:46  rshortt
# Make sure we close the device when done.
#
# Revision 1.1  2003/05/29 00:45:53  rshortt
# Plugin to record using an ivtv (PVR-250/350) based capture card.
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

import sys, string
import random
import time, os
import threading
import signal

import config
import tv_util, ivtv
import childapp 
import plugin 

DEBUG = 1

TRUE = 1
FALSE = 0

CHUNKSIZE = 65536


class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)

        print 'ACTIVATING IVTV RECORD PLUGIN'
        plugin.register(Recorder(), 'RECORD')


class Recorder:

    def __init__(self):
        self.thread = Record_Thread()
        self.thread.setDaemon(1)
        self.thread.mode = 'idle'
        self.thread.start()
        

    def Record(self, rec_prog):

        self.thread.mode = 'record'
        self.thread.prog = rec_prog
        self.thread.mode_flag.set()
        
        print('Recorder::Record: %s' % rec_prog)
        
        
    def Stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()



class Record_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.prog  = ''
        self.app = None

    def run(self):
        while 1:
            print('Record_Thread::run: mode=%s' % self.mode)
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'record':
                print 'Record_Thread::run: started recording'

                tv_lock_file = config.FREEVO_CACHEDIR + '/record'
                open(tv_lock_file, 'w').close()

                video_save_file = '%s/%s.mpeg' % (config.DIR_RECORD, 
                                             string.replace(self.prog.filename,
                                                            ' ', '_'))
                
                (v_norm, v_input, v_clist, v_dev) = config.TV_SETTINGS.split()

                v = ivtv.IVTV(v_dev)

                v.init_settings()

                print 'Setting Channel to %s' % self.prog.tunerid
                v.setchannel(self.prog.tunerid)

                v.print_settings()

                now = time.time()
                stop = now + self.prog.rec_duration

                time.sleep(2)

                v_in  = open(v_dev, 'r')
                v_out = open(video_save_file, 'w')

                while time.time() < stop:
                    buf = v_in.read(CHUNKSIZE)
                    v_out.write(buf)

                v_in.close()
                v_out.close()
                v.close()
                v = None

                os.remove(tv_lock_file)

                print('Record_Thread::run: finished recording')

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'
            time.sleep(0.5)


    

