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
# Revision 1.67  2004/11/04 17:40:17  dischi
# change to new notifier interface
#
# Revision 1.66  2004/11/01 20:14:04  dischi
# fix debug
#
# Revision 1.65  2004/10/30 18:47:14  dischi
# fix missing import
#
# Revision 1.64  2004/10/29 18:16:41  dischi
# moved killall to this file
#
# Revision 1.63  2004/10/06 19:24:00  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.62  2004/10/06 18:44:24  dischi
# rewrite to use pyNotifier and no threads
#
# Revision 1.61  2004/09/15 20:47:42  dischi
# avoid duplicate events
#
# Revision 1.60  2004/08/23 20:38:56  dischi
# fix osd stop/restart
#
# Revision 1.59  2004/08/23 12:39:59  dischi
# remove osd.py dep
#
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
import fcntl
import threading, thread
import signal
import copy
import popen2
import glob
import re

import notifier

import config
import eventhandler
import gui
import cleanup
import util

from event import *

watcher = None


def killall(appname, sig=9):
    """
    kills all applications with the string <appname> in their commandline.

    The <sig> parameter indicates the signal to use.
    This implementation uses the /proc filesystem, it might be Linux-dependent.
    """

    unify_name = re.compile('[^A-Za-z0-9]').sub
    appname = unify_name('', appname)

    cmdline_filenames = glob.glob('/proc/[0-9]*/cmdline')

    for cmdline_filename in cmdline_filenames:
        try:
            fd = vfs.open(cmdline_filename)
            cmdline = fd.read()
            fd.close()
        except IOError:
            continue
        if unify_name('', cmdline).find(appname) != -1:
            # Found one, kill it
            pid = int(cmdline_filename.split('/')[2])
            try:
                os.kill(pid, sig)
            except:
                pass
    return


class Instance:
    """
    Base class for started child processes
    """
    ready = False

    def __init__( self, app, debugname = None, doeslogging = 0, prio = 0,
                  stop_osd = 2 ):
        cleanup.register( self.stop )

        self.is_video = 0                       # Be more explicit
        if stop_osd == 2: 
            self.is_video = 1
            eventhandler.post( Event( VIDEO_START ) )
            stop_osd = 1

        self.stop_osd = stop_osd
        if self.stop_osd:
            gui.display.hide()
        
        if hasattr(self, 'item'):
            eventhandler.post( Event( PLAY_START, arg = self.item ) )

        # return status of the child
        self.status = 0

        if isinstance( app, unicode ):
            app = app.encode( config.LOCALE, 'ignore' )
            
        if isinstance(app, str):
            # app is a string to execute. It will be executed by 'sh -c '
            # inside the popen code
            self.binary = app.lstrip()
                
            start_str = app
            debug_name = app[ : app.find( ' ' ) ]
        else:
            # app is a list
            if app[ 0 ].startswith( '--prio' ): app = app[ 1 : ]
            while '' in app:
                app.remove( '' )

            self.binary = str( ' ' ).join( app )
            start_str = app
            
            debug_name = app[ 0 ]
            _debug_('running %s' % self.binary, 1)
        
        if debug_name.rfind('/') > 0:
            debug_name = debug_name[ debug_name.rfind( '/' ) + 1 : ]
        else:
            debug_name = debug_name

        if debugname:
	    debug_name = debugname
	
	if doeslogging or config.CHILDAPP_DEBUG:
	    doeslogging = 1
	
        self.__kill_timer = None
        self.stopping = False
        self.child   = popen2.Popen3( start_str, True, 100 )
        self.outfile = self.child.fromchild 
        self.errfile = self.child.childerr
        self.infile  = self.child.tochild

        self.__io_out = IO_Handler( 'stdout', self.outfile, self.stdout_cb,
                                   debug_name, doeslogging )
        self.__io_err = IO_Handler( 'stderr', self.errfile, self.stderr_cb,
                                   debug_name, doeslogging )
        watcher.add( self.child, self.__child_died )
        
        if prio and config.CONF.renice:
            os.system('%s %s -p %s 2>/dev/null >/dev/null' % \
                      (config.CONF.renice, prio, self.child.pid))
            
        self.ready = True
        self.dead = False
        

    # Write a string to the app. 
    def write( self, line ):
        try:
            self.infile.write(line)
            self.infile.flush()
        except (IOError, ValueError):
            pass
        

    def isAlive( self ):
        if not self.ready: # return true if constructor has not finished yet
            return True
        return not self.outfile.closed and not self.errfile.closed
        

    def stop( self, cmd = '' ):
        """
        stop the child
        """
        if self.stopping:
            return

        self.stopping = True
        cleanup.unregister( self.stop )

        if self.isAlive() and not self.__kill_timer:
            if cmd:
                _debug_('sending exit command to app')
                self.write(cmd)
                cb = notifier.Callback( self._kill, 15 )
                self.__kill_timer = notifier.addTimer( 1000, cb )
            else:
                cb = notifier.Callback( self._kill, 15 )
                self.__kill_timer = notifier.addTimer( 0, cb )

            while not self.dead:
                notifier.step( False, False )

    def stop_event(self):
        """
        event to send on stop
        """
        return PLAY_END


    def _kill( self, signal ):
        if not self.isAlive():
            self.dead = True
            return False
        # child needs some assistance with dying ...
        try:
            os.kill( self.child.pid, signal )
        except OSError:
            pass

        if signal == 15:
            cb = notifier.Callback( self._kill, 9 )
        else:
            cb = notifier.Callback( self._killall, 15 )
            
        self.__kill_timer = notifier.addTimer( 1000, cb )
        
        return False

    def _killall( self, signal ):
        if not self.isAlive():
            self.dead = True
            return False
        # child needs some assistance with dying ...
        try:
            killall( self.binary, signal )
        except OSError:
            pass

        _debug_('kill -%d %s' % ( signal, self.binary ), 1)
        if signal == 15:
            cb = notifier.Callback( self._killall, 9 )
            self.__kill_timer = notifier.addTimer( 1000, cb )
        else:
            _debug_('PANIC %s' % self.binary, 0)
            
        return False

    def __child_died( self, proc ):
        self.dead = True
        # cleanup IO handler and kill timer
        self.__io_out.cleanup()
        self.__io_err.cleanup()
        if self.__kill_timer:
            notifier.removeTimer( self.__kill_timer )
            
        # Ok, we can use the OSD again.
        if self.stop_osd:
            gui.display.show()

        if not self.stopping:
            if self.is_video:
                eventhandler.post( Event( VIDEO_END ) )
        
            eventhandler.post( self.stop_event() )
        
    # Override this method to receive stdout from the child app
    # The function receives complete lines
    def stdout_cb( self, line ):
        pass


    # Override this method to receive stderr from the child app
    # The function receives complete lines
    def stderr_cb( self, line ):
        pass


class IO_Handler:
    """
    reading data from socket 
    """
    def __init__( self, name, fp, callback, logger = None, doeslogging = 0 ):
        self.name = name
        self.fp = fp
        fcntl.fcntl( self.fp.fileno(), fcntl.F_SETFL, os.O_NONBLOCK )
        self.callback = callback
        self.logger = None
        self.saved = ''
        notifier.addSocket( fp, self._handle_input )
        if logger and doeslogging:
            logger = os.path.join( config.LOGDIR,
                                        '%s-%s.log' % ( logger, name ) )
            try:
                try:
                    os.unlink(logger)
                except:
                    pass
                self.logger = open(logger, 'w')
                _debug_('logging child to "%s"' % logger, 1)
            except IOError:
                _debug_('Error: Cannot open "%s" for logging' % logger, 0)
            
    def cleanup( self ):
        notifier.removeSocket( self.fp )

    def _handle_input( self, socket ):
        data = self.fp.read( 100 )
        if not data:
            _debug_( '%s: No data, stopping (pid %s)!' % \
                     ( self.name, os.getpid() ), 2 )
            notifier.removeSocket( self.fp )
            self.fp.close()
            if self.logger:
                self.logger.close()
        else:
            data  = data.replace('\r', '\n')
            lines = data.split('\n')

            # Only one partial line?
            if len(lines) == 1:
                self.saved += data
            else:
                # Combine saved data and first line, send to app
                if self.logger:
                    self.logger.write( self.saved + lines[ 0 ] + '\n' )
                self.callback( self.saved + lines[ 0 ] )
                self.saved = ''

                # There's one or more lines + possibly a partial line
                if lines[ -1 ] != '':
                    # The last line is partial, save it for the next time
                    self.saved = lines[ -1 ]

                    # Send all lines except the last partial line to the app
                    for line in lines[ 1 : -1 ]:
                        if self.logger:
                            self.logger.write( line + '\n' )
                        self.callback( line )
                else:
                    # Send all lines to the app
                    for line in lines[ 1 : ]:
                        if self.logger:
                            self.logger.write( line + '\n' )
                        self.callback( line )
        return True
    

class _Watcher:
    def __init__( self ):
        _debug_( "new process watcher instance" )
        self.__processes = {}


    def add( self, proc, cb ):
        self.__processes[ proc ] = cb

    def remove( self, proc ):
        if self.__processes.has_key():
            del self.__processes[ proc ]
    
    def step( self ):
        remove_proc = []
        for p in copy.copy( self.__processes ):
            try:
                if isinstance( p, popen2.Popen3 ):
                    pid, status = os.waitpid( p.pid, os.WNOHANG )
                else:
                    pid, status = os.waitpid( p.pid, os.WNOHANG )
            except OSError:
                remove_proc.append( p )
                continue
            if not pid: continue
            _debug_(">>> DEAD CHILD: %s (%s)" % ( pid, status ), 1)
            if status == -1:
                _debug_("error retrieving process information from %d" % p, 0)
            elif os.WIFEXITED( status ) or os.WIFSIGNALED( status ) or \
                     os.WCOREDUMP( status ):
                self.__processes[ p ]( p )
                remove_proc.append( p )

        # remove dead processes
        for p in remove_proc: del self.__processes[ p ]

watcher = _Watcher()
