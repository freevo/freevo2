
#if 0 /*
# -----------------------------------------------------------------------
# generic_record.py - A plugin to record tv using VCR_CMD.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2003/09/05 14:28:01  rshortt
# Oops.  We don't need tv_util here anymore.
#
# Revision 1.7  2003/09/03 17:54:38  dischi
# Put logfiles into LOGDIR not $FREEVO_STARTDIR because this variable
# doesn't exist anymore.
#
# Revision 1.6  2003/08/23 12:51:43  dischi
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

import sys, string
import random
import time, os, string
import threading
import signal

import config
import childapp 
import plugin 

DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)

        plugin.register(Recorder(), 'RECORD')


class Recorder:

    def __init__(self):
        # Disable this plugin if not loaded by record_server.
        if string.find(sys.argv[0], 'record_server') == -1:
            return

        if DEBUG: print 'ACTIVATING GENERIC RECORD PLUGIN'

        self.thread = Record_Thread()
        self.thread.setDaemon(1)
        self.thread.mode = 'idle'
        self.thread.start()
        

    def Record(self, rec_prog):
        cl_options = { 'channel'  : rec_prog.tunerid,
                       'filename' : config.DIR_RECORD + '/' + rec_prog.filename,
                       'seconds'  : rec_prog.rec_duration }

        self.rec_command = config.VCR_CMD % cl_options

        self.thread.mode = 'record'
        self.thread.command = self.rec_command
        self.thread.mode_flag.set()
        
        print('Recorder::Record: %s' % self.rec_command)
        
        
    def Stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()


class RecordApp(childapp.ChildApp):

    def __init__(self, app):
        if DEBUG: 
            fname_out = os.path.join(config.LOGDIR, 'recorder_stdout.log')
            fname_err = os.path.join(config.LOGDIR, 'recorder_stderr.log')
            try:
                self.log_stdout = open(fname_out, 'a')
                self.log_stderr = open(fname_err, 'a')
            except IOError:
                print
                print (('ERROR: Cannot open "%s" and "%s" for ' +
                        'record logging!') % (fname_out, fname_err))
                print 'Please set DEBUG=0 or '
                print 'start Freevo from a directory that is writeable!'
                print
            else:
                print 'Record logging to "%s" and "%s"' % (fname_out, fname_err)

        childapp.ChildApp.__init__(self, app)
        

    def kill(self):
        childapp.ChildApp.kill(self, signal.SIGINT)

        if DEBUG:
            self.log_stdout.close()
            self.log_stderr.close()


class Record_Thread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        
        self.mode = 'idle'
        self.mode_flag = threading.Event()
        self.command  = ''
        self.app = None

    def run(self):
        while 1:
            print('Record_Thread::run: mode=%s' % self.mode)
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()
                
            elif self.mode == 'record':
                print('Record_Thread::run: cmd=%s' % self.command)

                tv_lock_file = config.FREEVO_CACHEDIR + '/record'
                open(tv_lock_file, 'w').close()

                self.app = RecordApp(self.command)
                
                while self.mode == 'record' and self.app.isAlive():
                    time.sleep(0.5)

                print('Record_Thread::run: past wait()!!')

                self.app.kill()

                os.remove(tv_lock_file)

                self.mode = 'idle'
                
            else:
                self.mode = 'idle'
            time.sleep(0.5)

