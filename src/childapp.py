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
# Revision 1.10  2003/05/28 17:24:23  dischi
# fixed bug when child is dead
#
# Revision 1.9  2003/04/24 19:55:44  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.8  2003/04/24 11:46:29  dischi
# fixed 'to many open files' bug
#
# Revision 1.7  2003/04/06 21:12:54  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded inports)
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


DEBUG = config.DEBUG


class ChildApp:

    def __init__(self, app):
        # Start the child app through 'runapp' which will unblock signals and
        # sets the priority.

        start_str = './runapp ' + app
        
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


        if DEBUG:
            print 'self.t1.isAlive()=%s, self.t2.isAlive()=%s' % (self.t1.isAlive(),
                                                                  self.t2.isAlive())
            time.sleep(0.1)
            print 'ChildApp.__init__(), pid=%s, app=%s, poll=%s' % (self.child.pid, start_str, self.child.poll())
            

    # Write a string to the app. 
    def write(self, line):
        try:
            self.infile.write(line)
            self.infile.flush()
        except IOError:
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

        try:
            if signal:
                if DEBUG: print 'childapp: killing pid %s signal %s' % \
                   (self.child.pid, signal)
                os.kill(self.child.pid, signal)
            
            # Wait for the child to exit
            try:
                if DEBUG: print 'childapp: Before wait(%s)' % self.child.pid
                for i in range(20):
                    if os.waitpid(self.child.pid, os.WNOHANG)[0] == self.child.pid:
                        break
                    time.sleep(0.1)
                else:
                    print 'force killing with signal 9'
                    os.kill(self.child.pid, 9)
                    self.child.wait()
                if DEBUG: print 'childapp: After wait()'
            except:
                pass

        except OSError:
            # Already dead
            pass

        try:
            self.outfile.close()
            self.errfile.close()
            self.infile.close()
        except:
            print 'error closing filehandler'
            pass

        
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
                if DEBUG:
                    print '%s: No data, stopping (pid %s)!' % (self.name, os.getpid())
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
                        


class Test_Thread(threading.Thread):

    def __init__(self, cmd):
        threading.Thread.__init__(self)
        self.app = Rec(cmd)
        

    def run(self):
        while 1:
            s = raw_input('Cmd>')
            if s.strip() == '':
                print 'Alive = %s' % self.app.isAlive()
            elif s.strip() == 'k':
                self.app.kill(signal.SIGINT)
                print 'Sent INT'
            elif s.strip() == 'q':
                sys.exit(0)


            
class Rec(ChildApp):

    def stdout_cb(self, line):
        print 'stdout data: "%s"' % line


    def stderr_cb(self, line):
        print 'stderr data: "%s"' % line


    
if __name__ == '__main__':

    #cmd = '/usr/local/bin/DIVX4rec -F 300000 -norm NTSC -input Television -m -r '
    #cmd += '22050 -w 320 -h 240 -ab 80 -vg 300 -vb 800 -H 50 -o tst3.avi'
    #cmd = './matrox_g400/v4l1_to_mga ntsc television us-cable 2'
    #cmd = '/usr/local/bin/mplayer -vo null -ao oss:/dev/dsp0 testfiles/Music/ThomasRusiak-Hiphopper.mp3'
    cmd = '/usr/bin/nice -0 mplayer -vo xv -ao oss:/dev/dsp -nobps -framedrop -nolirc -screenw 768 -screenh 576 -fs -demuxer 17 "/hdc/krister_mp3/mp3/(216)_sweet_-_ballroom_blitz-idm.mp3"'
    
    Test_Thread(cmd).start()

    while 1:
        time.sleep(1)
    
    app = Rec(cmd)
    
    print 'Started app'

    chan = 3
    while 1:
        s = raw_input('Cmd>')
        if s.strip() == '':
            print 'Alive = %s' % app.isAlive()
        elif s.strip() == 'k':
            app.kill(signal.SIGINT)
            print 'Sent INT'
        elif s.strip() == 'q':
            sys.exit(0)
        elif s.strip() == 'n':
            app.write('ntsc television us-cable %s\n' % chan)
            chan += 1
            print 'Wrote to app'
            
            
        
