#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# makestationlist.py - Generates stationlist.xml for use with tvtime
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo: Map the various frequencies from freevo.conf to the frequencies
#       for tv time.       
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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
import config
import cgi

if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'convert freevo_config.py station list for tvtime'
    print 'this script has no options'
    print
    sys.exit(0)


norm = "US-Cable"

fp = open('/tmp/stationlist.xml','w')

fp.write('<?xml version="1.0"?>\n')
fp.write('<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">\n')
fp.write('<stationlist xmlns="http://tvtime.sourceforge.net/DTD/">\n')
fp.write('  <list norm="NTSC" frequencies="%s">\n' % (norm))

c = 0
for m in config.TV_CHANNELS:
    fp.write('    <station name="%s" active="1" position="%s" band="US Cable" channel="%s"/>\n' % (cgi.escape(m[1]),c,m[2]))
    c = c + 1

fp.write('  </list>\n')
fp.write('</stationlist>\n')
fp.close()
