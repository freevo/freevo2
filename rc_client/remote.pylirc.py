#if 0 /*
# -----------------------------------------------------------------------
# remote.py  -  Freevo remote control handling.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/06/07 11:34:01  dischi
# cleanup
#
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
import socket
import tty, time, os

import pylirc

# We need to use stuff from the main directory
sys.path += [ '..', '.','src/']

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config


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
    'e'           : 'REC',
    'Y'           : 'EJECT',
    'L'           : 'SUBTITLE'
    }


class RemoteLirc:

    def __init__(self):
        # TODO: Make the lircrc file configurable.
	pylirc.init('freevo','/etc/freevo/lircrc')        
	
	# Turn on blocking mode.
	pylirc.blocking(1)


    def get_cmd(self):
        while 1:
	    cmd = ''
            print 'Waiting for buttonpress'
	    list = pylirc.nextcode()
	    for code in list:
	        print "CODE: " + code
		cmd = code
            return cmd



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

    if DEBUG:
        print 'remote.py:',
        print sys.argv
    
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
    import traceback
    try:
        main()
    except:
        print 'Crash!'
        traceback.print_exc()
        time.sleep(1)
