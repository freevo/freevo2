#if 0 /*
# -----------------------------------------------------------------------
# childapp.py - Runs an application in a child process
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.14  2003/09/20 17:30:23  dischi
# do not close streams when we have to kill the app by force
#
# Revision 1.13  2003/09/19 22:07:57  dischi
# add unified PlayerThread function to avoid duplicate code
#
# Revision 1.12  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
# Revision 1.11  2003/08/22 17:51:29  dischi
# Some changes to make freevo work when installed into the system
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

import sys
import time
import os
import popen2
import threading
import signal

import config
import osd
import rc
from event import *

class ChildApp:

    def __init__(self, app):
        # Start the child app through 'runapp' which will unblock signals and
        # sets the priority.
        prio = 0
        if app.find('--prio=') == 0 and not config.RUNAPP:
            try:
                prio = int(app[7:app.find(' ')])
            except:
                pass
            app = app[app.find(' ')+1:]

        start_str = '%s %s' % (config.RUNAPP, app)

        self.child = popen2.Popen3(start_str, 1, 100) 
        self.outfile = self.child.fromchild 
        self.errfile = self.child.childerr
        self.infile = self.child.tochild
        
        self.t1 = Read_Thread('stdout', self.outfile, self.stdout_cb)
        self.t1.setDaemon(1)
        self.t1.start()
        
        self.t2 = Read_Thread('stderr', self.errfile, self.stderr_cb)
        self.t2.setDaemon(1)
        self.t2.start()

        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))
            
        if config.DEBUG:
            print 'self.t1.isAlive()=%s, self.t2.isAlive()=%s' % (self.t1.isAlive(),
                                                                  self.t2.isAlive())
            time.sleep(0.1)
            print 'ChildApp.__init__(), pid=%s, app=%s, poll=%s' % \
                  (self.child.pid, start_str, self.child.poll())
            

    # Write a string to the app. 
    def write(self, line):
        try:
            self.infile.write(line)
            self.infile.flush()
        except (IOError, ValueError):
            pass
        

    # Override this method to receive stdout from the child app
    # The function receives complete lines
    def stdout_cb(self, line):
        pass


    # Override this method to receive stderr from the child app
    # The function receives complete lines
    def stderr_cb(self, line):
        pass


    def isAlive(self):
        return self.t1.isAlive() or self.t2.isAlive()

    
    def kill(self, signal=9):
        # killed already
        if not self.child:
            return

        import traceback
        traceback.print_exc()
        
        # maybe child is dead and only waiting?
        if os.waitpid(self.child.pid, os.WNOHANG)[0] == self.child.pid:
            self.outfile.close()
            self.errfile.close()
            self.infile.close()
            self.child = None
            return
        
        if signal:
            _debug_('childapp: killing pid %s signal %s' % (self.child.pid, signal))
            os.kill(self.child.pid, signal)
            
        # Wait for the child to exit
        try:
            _debug_('childapp: Before wait(%s)' % self.child.pid)
            for i in range(20):
                if os.waitpid(self.child.pid, os.WNOHANG)[0] == self.child.pid:
                    break
                time.sleep(0.1)
            else:
                print 'force killing with signal 9'
                os.kill(self.child.pid, 9)
                self.child.wait()
            _debug_('childapp: After wait()')

        except OSError:
            pass
        
        # this may cause some problems with threads
        # in the child because not everything died :-(
        # try:
        # self.outfile.close()
        # self.errfile.close()
        # self.infile.close()
        # except:
        #    print 'error closing filehandler'
        #    pass
        self.child = None


        
class Read_Thread(threading.Thread):

    def __init__(self, name, fp, callback):
        threading.Thread.__init__(self)
        self.name = name
        self.fp = fp
        self.callback = callback

        
    def run(self):
        try:
            self._handle_input()
        except IOError:
            pass
        except ValueError:
            pass


    def _handle_input(self):
        
        saved = ''
        while 1:

            # XXX There should be a C helper app that converts CR to LF.
            data = self.fp.readline(300)
            if not data:
                _debug_('%s: No data, stopping (pid %s)!' % (self.name, os.getpid()))
                break
            else:
                data = data.replace('\r', '\n')
                lines = data.split('\n')

                # Only one partial line?
                if len(lines) == 1:
                    saved += data
                else:
                    # Combine saved data and first line, send to app
                    self.callback(saved + lines[0])
                    saved = ''

                    # There's one or more lines + possibly a partial line
                    if lines[-1] != '':
                        # The last line is partial, save it for the next time
                        saved = lines[-1]

                        # Send all lines except the last partial line to the app
                        for line in lines[1:-1]:
                            self.callback(line)
                    else:
                        # Send all lines to the app
                        for line in lines[1:]:
                            self.callback(line)
                        


class DummyApp:
    def __init__(self, name=None, parameter=None):
        self.app_name  = name
        self.parameter = parameter
        
    def write(self, string):
        pass

        
class ChildThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.mode        = 'idle'
        self.mode_flag   = threading.Event()
        self.stop_osd    = False
        self.app         = DummyApp()
        self.manual_stop = False
        
        self.setDaemon(1)
        threading.Thread.start(self)


    def start(self, app, param):
        """
        set thread to play mode
        """
        self.app         = DummyApp(app, param)
        self.mode        = 'play'
        self.manual_stop = False
        self.mode_flag.set()


    def stop(self, cmd=None):
        if self.mode != 'play':
            return
        
        if cmd:
            self.manual_stop = True
            _debug_('sending exit command to app')
            self.app.write(cmd)
            # wait for the app to terminate itself
            for i in range(20):
                if self.mode != 'play':
                    break
                time.sleep(0.1)

        self.mode = 'stop'
        self.mode_flag.set()
        while self.mode == 'stop':
            time.sleep(0.3)

        
    def run(self):
        while 1:
            if self.mode == 'idle':
                self.mode_flag.wait()
                self.mode_flag.clear()

            elif self.mode == 'play':

                if self.stop_osd and config.STOP_OSD_WHEN_PLAYING:
                    osd.stop()

                self.app = self.app.app_name(self.app.parameter)
                
                if hasattr(self.app, 'item'):
                    rc.post_event(Event(PLAY_START, arg=self.app.item))
                
                while self.mode == 'play' and self.app.isAlive():
                    time.sleep(0.1)

                if self.mode == 'play' and not self.manual_stop:
                    if hasattr(self.app, 'stopped'): 
                        self.app.stopped()
                    else:
                        _debug_('app has no stopped function, send PLAY_END')
                        rc.post_event(PLAY_END)
                        
                self.app.kill()

                # Ok, we can use the OSD again.
                if self.stop_osd and config.STOP_OSD_WHEN_PLAYING:
                    osd.restart()
                
                self.mode = 'idle'
                
            else:
                self.mode = 'idle'
