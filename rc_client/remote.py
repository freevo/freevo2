#!/usr/local/bin/python


import sys
import socket
import random
import termios, tty, time, os
import string, popen2, fcntl, select
import traceback

# We need to use stuff from the main directory
sys.path += [ '..', '.' ]

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# Set to 1 for debug output
DEBUG = 1


cmds_kbd = {
    'S'           : 'SLEEP',
    'm'           : 'MENU',
    'g'           : 'GUIDE',
    'Q'           : 'EXIT',
    'k'           : 'UP',
    'j'           : 'DOWN',
    'h'           : 'LEFT',
    'l'           : 'RIGHT',
    ' '           : 'SELECT',
    'P'           : 'POWER',
    'M'           : 'MUTE',
    'Z'           : 'VOL+',
    'X'           : 'VOL-',
    'C'           : 'CH+',
    'V'           : 'CH-',
    '1'           : '1',
    '2'           : '2',
    '3'           : '3',
    '4'           : '4',
    '5'           : '5',
    '6'           : '6',
    '7'           : '7',
    '8'           : '8',
    '9'           : '9',
    '0'           : '0',
    'D'           : 'DISPLAY',
    'E'           : 'ENTER',
    '_'           : 'PREV_CH',
    'o'           : 'PIP_ONOFF',
    'w'           : 'PIP_SWAP',
    'i'           : 'PIP_MOVE',
    'v'           : 'TV_VCR',
    'r'           : 'REW',
    'p'           : 'PLAY',
    'f'           : 'FFWD',
    'u'           : 'PAUSE',
    's'           : 'STOP',
    'e'           : 'REC'
    }


class RemoteLirc:

    def __init__(self):
        self.lirc = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        # Read directly from the remote control daemon, no translation
        self.lirc.connect('/dev/lircd')
        self.cmds = config.RC_CMDS

    def get_cmd(self):
        while 1:
            print 'Waiting for buttonpress'
            str = ''
            while 1:
                c = self.lirc.recv(1)
                if c == '\n':
                    break
                else:
                    str += c
            print 'Got str = "%s"' % str
            if len(str.split()) < 4:
                continue
            remote = str.split()[3]
            button = str.split()[2]
            cntx = str.split()[1]
            cntd = int(cntx, 16)
            cmd = self.cmds.get(button, '')
            print 'cnt: %s=%s' % (cntx, cntd)
            if cmd != '':
                # Slow down start of autorepeat
                if cntd == 0 or cntd > 6:
                    # Only get every other code, slows down autorepeat
                    if not cntd % 3:
                        print 'Translation: "%s" -> "%s"' % (button, cmd)
                        return cmd
            else:
                print 'Translation: "%s" not found!' % (button,)
            time.sleep(0.1)



class RemoteKbd:

    def __init__(self):
        tty.setraw(sys.stdin.fileno())
        self.cmds = cmds_kbd

    def get_cmd(self):
        infd = sys.stdin.fileno()

        # Loop until a key is pressed
        while 1:
            #ready = select.select([infd],[],[], .1) # wait for input or timeout

            # Is there data to read?
            #if ready[0] == []: 
            #    continue # No, try again

            button = ord(sys.stdin.read(1))

            # Check for CTRL-C
            if button == 3:
                sys.exit(0)
                
            print 'got data = %d\n\r' % (button, ),
            
            cmd = self.cmds.get(chr(button), '')

            print 'cnt: %s=%s' % (button, cmd)

            if cmd != '':
                print 'Translation: "%s" -> "%s"\r' % (button, cmd)
                return cmd
            else:
                print 'Translation: "%s" not found!\r' % (button,)


          
def getcmd(remote, mode = 'sim'):

    host = config.REMOTE_CONTROL_HOST
    port = config.REMOTE_CONTROL_PORT

    # Set up the UDP/IP connection to the Freevo main application
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while 1:

       cmd = remote.get_cmd()

       if mode == 'sim':
           print_cmds(remote.cmds)
           print '\r\nPress the simulated remote control keys in this window!\r'
           print 'Got cmd == %s\r' % cmd
           
       try:
           sock.sendto(cmd, (host, port))
       except:
           print 'Freevo is down, discarding the command!\r'
           break               # Go back and reconnect
        


def print_cmds(cmds):
    print '\r\nKeyboard commands:\r'
    for cmd in cmds.keys():
        print "Button/Key  '%s' = %s\r" % (cmd, cmds[cmd])


def main():
    # Default is simulated remote
    mode = 'sim'
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--remote=lirc':
            mode = 'lirc'

    if mode == 'sim':
        remote = RemoteKbd()
        print_cmds(remote.cmds)
        print '\r\nPress the simulated remote control keys in this window!\r'
    else:
        remote = RemoteLirc()

    print '\r'

    getcmd(remote, mode)

    
if __name__ == "__main__":
    try:
        main()
    except:
        print 'Crash!'
        traceback.print_exc()
        time.sleep(1)
