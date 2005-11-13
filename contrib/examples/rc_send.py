#! /usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# rc_send.py - a small standalone program to send remote events to Freevo
# -----------------------------------------------------------------------
# $Id$
#
# Notes: need ENABLE_NETWORK_REMOTE = 1 in you local_conf.py
#
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/11/01 05:09:00  krister
# Standalone RC event sender app
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
# Please see the file doc/CREDITS for a complete list of authors.
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


######################################################################

def usage():
        print 'a small standalone program to send remote events to Freevo'
        print 'You need to set ENABLE_NETWORK_REMOTE = 1 in you local_conf.py'
        print
        print 'The first argument is the event name, e.g. "SELECT"'
        print 'Please see the freevo source file freevo/src/event.py'
        print 'for a list of event names'
        print
        print 'It takes two optional arguments:'
	print '    - the first is host which defaults to localhost'
	print '    - the second is port which defaults to 16310'
	print 
	print 'when run with no args it connects to the localhost on port 16130'
	print 'freevo remote'
	print 
	print 'when run with one arg it connects to the given host on port 16130'
	print 'python rc_send <EVENT> [HOST] [PORT]'
        print
        sys.exit(0)

######################################################################
        
def send(event, host, port):
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockobj.connect((host, port))
        err = sockobj.send(event)
        sockobj.close()
        print 'Sent event "%s" to host "%s" on port %s' % (event, host, port)

######################################################################
        
if __name__ == '__main__': 
    if len(sys.argv) < 2 or sys.argv[1] == '--help':
        usage()

    event = sys.argv[1]
    host = '127.0.0.1'
    port = 16310
    
    if len(sys.argv) > 2:
        host = sys.argv[2]
        if len(sys.argv) > 3:
            port = int(sys.argv[3])
    send(event, host, port)
    

