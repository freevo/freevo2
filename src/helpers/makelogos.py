#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# makelogos.py - Download TV station logos using the XMLTV info
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.2  2004/06/23 11:11:18  dischi
# bufix
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


import os
import sys
import urllib2
import cStringIO
import Image

import config
from tv import xmltv

# Check if the logos directory exists, if not, make it before
# proceeding

if not os.path.isdir(config.TV_LOGOS):
        print "Logo directory does not exist\n"
        print "Creating: %s\n" % (config.TV_LOGOS)
        os.mkdir(config.TV_LOGOS)

x = xmltv.read_channels(open(config.XMLTV_FILE))

for i in x:
        try:
                imgsrc = i['icon'][0]['src']
        except KeyError:
                imgsrc = None
        channel = i['id']
        #print '%s - %s' % (imgsrc,channel)
        if imgsrc != None:
                # Get the file into a fp
                fp = urllib2.urlopen(str(imgsrc))
                # Make a seekable file object
                img = cStringIO.StringIO(fp.read())
                # Convert the image into a PNG and save to logos directory
                output_file = config.TV_LOGOS + '/' + channel + '.png'
                try: Image.open(img).save(output_file)
                except IOError: pass

