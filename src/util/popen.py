# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# popen.py - process control using pyNotifier
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'Process', 'killall' ]

# python imports
import os
import fcntl
import copy
import popen2
import glob
import re
import logging

# notifier
import notifier

log = logging.getLogger('popen')

# the global watcher object
watcher = None


def killall():
    """
    killall running processes
    """
    watcher.killall()


class Process:
    """
    Base class for started child processes
    """
    def __init__( self, app, debugname = None):
        """
        Init the child process 'app'. This can either be a string or a list
        of arguments (similar to popen2). If debugname is given, the stdout
        and stderr will also be written. To get the stdout and stderr, you
        need to inherit from this class and override stdout_cb and stderr_cb.
        """
        if isinstance(app, str):
            # app is a string to execute. It will be executed by 'sh -c '
            # inside the popen code
            self.binary = app.lstrip()
            
            start_str = app
        else:
            # app is a list
            while '' in app:
                app.remove( '' )

            self.binary = str( ' ' ).join( app )
            start_str = app
            
            log.info('running %s' % self.binary)
        
        self.__kill_timer = None
        self.stopping = False
        self.dead = False
        self.child = popen2.Popen3( start_str, True, 100 )
        # IO_Handler for stdout
        self.stdout = IO_Handler( 'stdout', self.child.fromchild,
                                    self.stdout_cb, debugname )
        # IO_Handler for stderr
        self.stderr = IO_Handler( 'stderr', self.child.childerr,
                                    self.stderr_cb, debugname )
        watcher.add( self, self.__child_died )
        
        

    def write( self, line ):
        """
        Write a string to the app. 
        """
        try:
            self.child.tochild.write(line)
            self.child.tochild.flush()
        except (IOError, ValueError):
            pass
        

    def isAlive( self ):
        """
        Return True if the app is still running
        """
        return not self.dead
        

    def stop( self, cmd = '' ):
        """
        Stop the child. If 'cmd' is given, this stop command will send to
        the app to stop itself. If this is not working, kill -15 and kill -9
        will be used to kill the app.
        """
        if self.stopping:
            return

        self.stopping = True

        if self.isAlive() and not self.__kill_timer:
            if cmd:
                log.info('sending exit command to app')
                self.write(cmd)
                cb = notifier.Callback( self._kill, 15 )
                self.__kill_timer = notifier.addTimer( 3000, cb )
            else:
                cb = notifier.Callback( self._kill, 15 )
                self.__kill_timer = notifier.addTimer( 0, cb )

            while not self.dead:
                notifier.step()


    def _kill( self, signal ):
        """
        Internal kill helper function
        """
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
            
        self.__kill_timer = notifier.addTimer( 3000, cb )
        
        return False


    def _killall( self, signal ):
        """
        Internal killall helper function
        """
        if not self.isAlive():
            self.dead = True
            return False
        # child needs some assistance with dying ...
        try:
            # kill all applications with the string <appname> in their
            # commandline. This implementation uses the /proc filesystem,
            # it is Linux-dependent.
            unify_name = re.compile('[^A-Za-z0-9]').sub
            appname = unify_name('', self.binary)

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
                        os.kill(pid, signal)
                    except:
                        pass
        except OSError:
            pass

        log.info('kill -%d %s' % ( signal, self.binary ))
        if signal == 15:
            cb = notifier.Callback( self._killall, 9 )
            self.__kill_timer = notifier.addTimer( 2000, cb )
        else:
            log.critical('PANIC %s' % self.binary)
            
        return False

    def __child_died( self, proc ):
        """
        Callback from watcher when the child died.
        """
        self.dead = True
        # cleanup IO handler and kill timer
        self.stdout.cleanup()
        self.stderr.cleanup()
        if self.__kill_timer:
            notifier.removeTimer( self.__kill_timer )
        self.finished()

        
    def finished(self):
        """
        Override this method to handle cleanup / notifications after the child
        is dead.
        """
        pass

        
    def stdout_cb( self, line ):
        """
        Override this method to receive stdout from the child app
        The function receives complete lines
        """
        pass


    def stderr_cb( self, line ):
        """
        Override this method to receive stderr from the child app
        The function receives complete lines
        """
        pass


class IO_Handler:
    """
    Reading data from socket (stdout or stderr)
    """
    def __init__( self, name, fp, callback, logger = None):
        self.name = name
        self.fp = fp
        fcntl.fcntl( self.fp.fileno(), fcntl.F_SETFL, os.O_NONBLOCK )
        self.callback = callback
        self.logger = None
        self.saved = ''
        notifier.addSocket( fp, self._handle_input )
        if logger:
            logger = '%s-%s.log' % ( logger, name )
            try:
                try:
                    os.unlink(logger)
                except:
                    pass
                self.logger = open(logger, 'w')
                log.info('logging child to "%s"' % logger)
            except IOError:
                log.warning('Error: Cannot open "%s" for logging' % logger)
            

    def close( self ):
        notifier.removeSocket( self.fp )
        self.fp.close()
        if self.logger:
            self.logger.close()
        

    def cleanup( self ):
        notifier.removeSocket( self.fp )


    def _handle_input( self, socket ):
        data = self.fp.read( 10000 )
        if not data:
            log.debug( '%s: No data, stopping (pid %s)!' % \
                       ( self.name, os.getpid() ) )
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
        log.info('new process watcher instance')
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
                if isinstance( p.child, popen2.Popen3 ):
                    pid, status = os.waitpid( p.child.pid, os.WNOHANG )
                else:
                    pid, status = os.waitpid( p.pid, os.WNOHANG )
            except OSError:
                remove_proc.append( p )
                continue
            if not pid: continue
            log.info('DEAD CHILD: %s (%s)' % ( pid, status ))
            if status == -1:
                log.error('error retrieving process information from %d' % p)
            elif os.WIFEXITED( status ) or os.WIFSIGNALED( status ) or \
                     os.WCOREDUMP( status ):
                self.__processes[ p ]( p )
                remove_proc.append( p )

        # remove dead processes
        for p in remove_proc:
            if p in self.__processes:
                del self.__processes[ p ]

    def killall( self ):
        for p in copy.copy(self.__processes):
            p.stop()


# init global watcher object
watcher = _Watcher()

# add checking for dead children to the notifier
notifier.addDispatcher( watcher.step )
