#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# bluetooth.py - control freevo via cell phone
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Please read the instructions at Docs/plugins/bluetooth.txt before
# mailing me. My adress is "ikea@hotbrev.com" and I'll answer any
# questions regarding this program.
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/12/23 15:11:35  dischi
# new bluetooth plugin
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


import time, os, re, socket, sys, config


global BLUE_RFCOMM



def init_sock():

    #Open the blutooth device. rfcomm is used to set a connection BEFORE this is used.
    print 'bluetooth: opening', BLUE_RFCOMM
    try:
        bluefd = os.open(BLUE_RFCOMM, os.O_RDWR); global bluefd
    except OSError:
        print 'bluetooth: CRITICAL ERROR (Could not open device ', BLUE_RFCOMM, ')'
        sys.exit(1) 

    #Sends the initstring to the phone telling it to return all keypad events.
    os.write(bluefd, "AT+CMER=3,2,0,0,0\r")
	

def read_conf():
	
    #rfcomm device path
    if config.BLUE_RFCOMM != '':
        BLUE_RFCOMM = config.BLUE_RFCOMM; global BLUE_RFCOMM
    else:
        print 'bluetooth: WARNING (Could not read BLUE_RFCOMM from config, using default!)'
	BLUE_RFCOMM = '/dev/bluetooth/rfcomm/1' 


print 'bluetooth_config, a configuration helper for the bluetooth Freevo plugin.'
if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'This plugin helps to define the buttons for the bluetooth plugin.'
    print 'Please read Docs/plugins/bluetooth.txt for more details.'
    sys.exit(0)

print
print 'Path (BLUE_RFCOMM) must be set in local_conf.py, and remember to have rfcomm'
print 'up and running'
print
print 'The output here will be something like "event s,1", where "s" is the name of'
print 'the button (use that in the config.'
print '",1" or ",0" tells you if you pressed (,1) or released (,0) the button.'
print
print 'DO NOT INCLUDE ,0 OR ,1 IN THE CONFIG!'
print
print 'Exit with ctrl + c'
print
print

read_conf()
init_sock()
    
try:
    global bluefd
    bluefd = os.open(BLUE_RFCOMM, os.O_RDWR)
except OSError:
    print 'bluetooth: CRITICAL ERROR (Could not open device ', BLUE_RFCOMM, ')'
    sys.exit(2)
		
    
rex = re.compile(r"\+CKEV:\s+(\w+,\w+)")
s=""
while 1:
    try:
	s += os.read(bluefd, 1024)
    	if rex.search(s):
	    print
            print 'event: ', rex.search(s).group(1)
	    s = ""	
    except KeyboardInterrupt:
        break
    
os.write(bluefd, "AT+CMER=0,0,0,0,0\r")
os.close(bluefd)
sys.exit(1)

