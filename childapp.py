#
# childapp.py
#
# Runs an application in a child process. Input can be written to it as
# well as capturing the output (both stdout and stderr) which is sent
# to callback functions.
#
# $Id$

import sys
import random
import time, os, glob
import string, popen2, fcntl, select, struct
import threading
import signal

DEBUG = 1

class ChildApp:

    def __init__(self, app):
        # Start the child app through 'runapp' which will unblock signals
        self.child = popen2.Popen3('./runapp ' + app, 1, 100) 
        self.outfile = self.child.fromchild 
        self.errfile = self.child.childerr
        self.infile = self.child.tochild
        
        self.t1 = Read_Thread('stdout', self.outfile, self.stdout_cb)
        self.t1.start()
        
        self.t2 = Read_Thread('stderr', self.errfile, self.stderr_cb)
        self.t2.start()
        

    # Write a string to the app. 
    def write(self, str):
        try:
            self.infile.write(str)
            self.infile.flush()
        except IOError:
            pass
        

    # Override this method to receive stdout from the child app
    def stdout_cb(self, str):
        pass


    # Override this method to receive stderr from the child app
    def stderr_cb(self, str):
        pass


    def isAlive(self):
        return self.t1.isAlive() or self.t2.isAlive()

    
    def kill(self, signal=9):
            os.kill(self.child.pid, signal)
            
            # Wait for the child to exit
            try:
                self.child.wait()
            except:
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


    def _handle_input(self):
        
        saved = ''
        while 1:

            # XXX There should be a C helper app that converts CR to LF.
            data = self.fp.readline(300)
            if not data:
                if DEBUG:
                    print '%s: No data, stopping!' % self.name
                break
            else:
                data = data.replace('\r', '\n')
                lines = data.split('\n')

                # Partial line?
                if len(lines) == 1:
                    saved += data
                else:
                    # There's one or more lines + possibly a partial line
                    lastelem = -1
                    if lines[-1] != '':
                        # The last line is partial
                        saved = lines[-1]
                        lastelem = -2


                    # Add first line to saved data
                    self.callback(saved + lines[0])

                    for line in lines[1:lastelem]:
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

    def stdout_cb(self, str):
        print 'stdout data: "%s"' % str


    def stderr_cb(self, str):
        print 'stderr data: "%s"' % str


    
if __name__ == '__main__':

    #cmd = '/usr/local/bin/DIVX4rec -F 300000 -norm NTSC -input Television -m -r '
    #cmd += '22050 -w 320 -h 240 -ab 80 -vg 300 -vb 800 -H 50 -o tst3.avi'
    #cmd = './matrox_g400/v4l1_to_mga ntsc television us-cable 2'
    cmd = '/usr/local/bin/mplayer -nolirc -nobps -idx -framedrop -cache 512 -vo mga -screenw 768 -screenh 576 -fs -ao oss:/dev/dsp0 /movies_local/recorded/0_rec_2002-04-22_210228.avi'

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
            
            
        
