#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# extendedadd.py - import all music files into sql database
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# Revision 1.1  2004/01/16 08:14:04  outlyer
# Forgot to commit this earlier. This is:
#
# extendedmeta: Parser for embedded covers, folder cache, and sqlite scoring
# dbutil:       Helper class for dealing with the sqlite db
# extendedadd:  A tool which calls the extendedmeta functions on a path, an
#               example of how to add all three types of data from the
#               command-line. Since the data is already used in blurr2, and
#               the info skins, it's nice to have.
#
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

# The basics
import os,string,fnmatch,sys

# The DB stuff
import sqlite

# Metadata tools
import mmpython

import config, util

from util.extendedmeta import AddExtendedMeta

if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1] == '--help':
        print 'Freevo extendedmeta helper'
        sys.exit(0)

    if len(sys.argv) > 1:
        print "Adding %s to DB, extracting covers and folder data" % (sys.argv[1])
        AddExtendedMeta(sys.argv[1])
    #else:
    #    print "Populating Database with entries"
    #    for dir in config.AUDIO_ITEMS:
    #        print "Scanning %s" % dir[0]
    #        addPathDB(dir[1],dir[0])


#if sys.argv[1]:
#    AudioParser(sys.argv[1])
#    extract_image(sys.argv[1])
#else:
#    jobs = list()
#    for dir in config.AUDIO_ITEMS:
#        print "Scanning %s" % dir[0]
#        a = util.recursefolders(dir[1],recurse=1)
#        for m in a:
#            if os.path.dirname(m) not in jobs:
#                jobs.append(os.path.dirname(m))
#
#    for path in jobs:
#        AudioParser(path)
#        try:
#            extract_image(path)
#        except IOError:
#            # Already exists
#            pass


