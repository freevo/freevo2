# -*- coding: iso-8859-1 -*-
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
# Revision 1.58  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# Revision 1.57  2004/07/10 12:33:36  dischi
# header cleanup
#
# Revision 1.56  2004/06/06 06:51:55  dischi
# fix prio handling
#
# Revision 1.55  2004/05/31 10:40:57  dischi
# update to new callback handling in rc
#
# Revision 1.54  2004/05/30 18:27:53  dischi
# More event / main loop cleanup. rc.py has a changed interface now
#
# Revision 1.53  2004/05/29 19:06:46  dischi
# register poll function to rc
#
# Revision 1.52  2004/05/09 14:16:16  dischi
# let the child stdout handled by main
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


import sys
import time
import os
import util.popen3
import threading, thread
import signal
import copy

import config
import osd
import rc
import eventhandler
import util

from event import *


class ChildApp:
    """
    Base class for started child processes
    """
    ready = False

    def __init__(self, app, debugname=None, doeslogging=0):
        self.lock = thread.allocate_lock()

        prio = 0

        if isinstance(app, unicode):
            app = app.encode(config.LOCALE, 'ignore')
            
        if isinstance(app, str):
            # app is a string to execute. It will be executed by 'sh -c '
            # inside the popen code
            if app.find('--prio=') == 0 and not config.RUNAPP:
                try:
                    prio = int(app[7:app.find(' ')])
                except:
                    pass
                app = app[app.find(' ')+1:]
            if app.find('--prio=') == 0:
                self.binary = app[app.find(' ')+1:].lstrip()
            else:
                self.binary = app.lstrip()
                
            start_str = '%s %s' % (config.RUNAPP, app)
            debug_name = app[:app.find(' ')]

        else:
            # app is a list
            while '' in app:
                app.remove('')

            if app[0].find('--prio=') == 0 and not config.RUNAPP:
                try:
                    prio = int(app[0][7:])
                except:
                    pass
                app = copy.copy(app[1:])

            self.binary = str(' ').join(app)

            if config.RUNAPP:
                start_str = [ config.RUNAPP ] + app
            else:
                start_str = app
            
            debug_name = app[0]

        
        if debug_name.rfind('/') > 0:
            debug_name = debug_name[debug_name.rfind('/')+1:]
        else:
            debug_name = debug_name

        if debugname:
	    debug_name = debugname
	
	if doeslogging or config.CHILDAPP_DEBUG:
	    doeslogging = 1
	
        self.child   = util.popen3.Popen3(start_str)
        self.outfile = self.child.fromchild 
        self.errfile = self.child.childerr
        self.infile  = self.child.tochild
        
        self.t1 = Read_Thread('stdout', self.outfile, self.stdout_cb, debug_name, doeslogging)
        self.t1.setDaemon(1)
        self.t1.start()
        
        self.t2 = Read_Thread('stderr', self.errfile, self.stderr_cb, debug_name, doeslogging)
        self.t2.setDaemon(1)
        self.t2.start()

        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))
            
        if config.DEBUG:
            print 'self.t1.isAlive()=%s, self.t2.isAlive()=%s' % (self.t1.isAlive(),
                                                                  self.t2.isAlive())
            time.sleep(0.1)
            if not isinstance(start_str, str):
                start_str = str(' ').join(start_str)
            print 'ChildApp.__init__(), pid=%s, app=%s, poll=%s' % \
                  (self.child.pid, start_str, self.child.poll())

        self.ready = True
        

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
        if not self.ready: # return true if constructor has not finished yet
            return True
        return self.t1.isAlive() or self.t2.isAlive()
        

    def wait(self):
        return util.popen3.waitpid(self.child.pid)

        
    def kill(self, signal=15):

        # killed already
        if hasattr(self,'child'):
            if not self.child:
                _debug_('already dead', 2)
                return
        else:
            _debug_('This should never happen!',1)
            return

        self.lock.acquire()
        # maybe child is dead and only waiting?
        if self.wait():
            _debug_('done the easy way', 2)
            self.child = None
            if not self.infile.closed:
                self.infile.close()
            self.lock.release()
            return

        if signal:
            _debug_('childapp: killing pid %s signal %s' % (self.child.pid, signal))
            try:
                os.kill(self.child.pid, signal)
            except OSError:
                pass
            
        _debug_('childapp: Before wait(%s)' % self.child.pid)
        for i in range(20):
            if self.wait():
                break
            time.sleep(0.1)
        else:
            print 'force killing with signal 9'
            try:
                os.kill(self.child.pid, 9)
            except OSError:
                pass
            for i in range(20):
                if self.wait():
                    break
                time.sleep(0.1)
        _debug_('childapp: After wait()')


        # now check if the app is really dead. If it is, outfile
        # should be closed by the reading thread
        for i in range(5):
            if self.outfile.closed:
                break
            time.sleep(0.1)
        else:
            # Problem: the program had more than one thread, each thread has a
            # pid. We killed only a part of the program. The filehandles are
            # still open, the program still lives. If we try to close the infile
            # now, Freevo will be dead.
            # Solution: there is no good one, let's try killall on the binary. It's
            # ugly but it's the _only_ way to stop this nasty app
            print 'Oops, command refuses to die, try bad hack....'
            util.killall(self.binary, sig=15)
            for i in range(20):
                if self.outfile.closed:
                    break
                time.sleep(0.1)
            else:
                # still not dead. Puh, something is realy broekn here.
                # Try killall -9 as last chance
                print 'Try harder to kill the app....'
                util.killall(self.binary, sig=9)
                for i in range(20):
                    if self.outfile.closed:
                        break
                    time.sleep(0.1)
                else:
                    # Oops...
                    print 'PANIC'
            if not self.infile.closed:
                self.infile.close()
        self.child = None
        self.lock.release()


        
class Read_Thread(threading.Thread):
    """
    Thread for reading stdout or stderr from the child
    """
    def __init__(self, name, fp, callback, logger=None, doeslogging=0):
        threading.Thread.__init__(self)
        self.name = name
        self.fp = fp
        self.callback = callback
        self.logger = None
        if logger and doeslogging:
            logger = os.path.join(config.LOGDIR, '%s-%s.log' % (logger, name))
            try:
                try:
                    os.unlink(logger)
                except:
                    pass
                self.logger = open(logger, 'w')
                print String(_( 'logging child to "%s"' )) % logger
            except IOError:
                print
                print String(_('ERROR')) + ': ' + \
                      String(_( 'Cannot open "%s" for logging!')) % logger
                print String(_('Set CHILDAPP_DEBUG=0 in local_conf.py, '+\
                               'or make %s writable!' )) % config.LOGDIR
            
        
    def run(self):
        try:
            self._handle_input()
        except (IOError, ValueError):
            pass


    def _handle_input(self):
        
        saved = ''
        while 1:

            data = self.fp.readline(300)
            if not data:
                _debug_('%s: No data, stopping (pid %s)!' % (self.name, os.getpid()),2)
                self.fp.close()
                if self.logger:
                    self.logger.close()
                break
            else:
                data  = data.replace('\r', '\n')
                lines = data.split('\n')

                # Only one partial line?
                if len(lines) == 1:
                    saved += data
                else:
                    # Combine saved data and first line, send to app
                    if self.logger:
                        self.logger.write(saved + lines[0]+'\n')
                    rc.register(self.callback, False, 0, saved + lines[0])
                    saved = ''

                    # There's one or more lines + possibly a partial line
                    if lines[-1] != '':
                        # The last line is partial, save it for the next time
                        saved = lines[-1]

                        # Send all lines except the last partial line to the app
                        for line in lines[1:-1]:
                            if self.logger:
                                self.logger.write(line+'\n')
                            rc.register(self.callback, False, 0, line)
                    else:
                        # Send all lines to the app
                        for line in lines[1:]:
                            if self.logger:
                                self.logger.write(line+'\n')
                            rc.register(self.callback, False, 0, line)
                        



class ChildApp2(ChildApp):
    """
    Enhanced version of ChildApp handling most playing stuff
    """
    def __init__(self, app, debugname=None, doeslogging=0, stop_osd=2):
        rc.register(self.poll, True, 10)
        rc.register(self.stop, True, rc.SHUTDOWN)
        
        self.is_video = 0                       # Be more explicit
        if stop_osd == 2: 
            self.is_video = 1
            eventhandler.post(Event(VIDEO_START))
            stop_osd = config.OSD_STOP_WHEN_PLAYING

        self.stop_osd = stop_osd
        if self.stop_osd:
           osd.stop()
        
        if hasattr(self, 'item'):
            eventhandler.post(Event(PLAY_START, arg=self.item))

        # return status of the child
        self.status = 0
        
        # start the child
        ChildApp.__init__(self, app, debugname, doeslogging)


    def stop_event(self):
        """
        event to send on stop
        """
        return PLAY_END


    def wait(self):
        """
        wait for the child process to stop
        """
        try:
            pid, status = os.waitpid(self.child.pid, os.WNOHANG)
        except OSError:
            # strange, no child? So it is finished
            return True
        
        if pid == self.child.pid:
            self.status = status
            return True
        return False
    
        
    def stop(self, cmd=''):
        """
        stop the child
        """
        rc.unregister(self.poll)
        rc.unregister(self.stop)

        if cmd and self.isAlive():
            _debug_('sending exit command to app')
            self.write(cmd)
            # wait for the app to terminate itself
            for i in range(20):
                if not self.isAlive():
                    break
                time.sleep(0.1)

        # kill the app
        self.kill()

        # Ok, we can use the OSD again.
        if self.stop_osd:
            osd.restart()

        if self.is_video:
            eventhandler.post(Event(VIDEO_END))

        
    def poll(self):
        """
        stop everything when child is dead
        """
        if not self.isAlive():
            eventhandler.post(self.stop_event())
            self.stop()
            
