#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# imdbp.py - IMDB helper script to generate fxd files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.8  2005/01/08 15:40:52  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.7  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.6  2004/01/08 17:33:14  outlyer
# Moved fxdimdb.py to util; it doesn't use the OSD, and having in video
# makes it import video/__init__...
#
# There is a reason for this to follow shortly :)
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
import os

try:
    import config
except ImportError:
    print 'imdb.py can\'t be executed outside the Freevo environment.'
    print 'Please use \'freevo imdb [args]\' instead'
    sys.exit(0)
    
from util.fxdimdb import FxdImdb, makeVideo
from random import Random

def usage():
    print 'imdb.py -s string:   search imdb for string'
    print
    print 'imdb.py -g filename:   guess imdb for possible filename match'    
    print
    print 'imdb.py [--rom-drive=/path/to/device] nr output files'
    print '  Generate output.fxd for the movie.'
    print '  Files is a list of files that belongs to this movie.'
    print '  Use [dvd|vcd] to add the whole disc or use [dvd|vcd][title]'
    print '  to add a special DVD or VCD title to the list of files'
    print
    print 'imdb.py [--rom-drive=/path/to/device] -a fxd-file file'
    print '  add file to fxd-file.fxd'
    print
    print 'If no rom-drive is given and one is required, /dev/cdrom is assumed'
    print
    sys.exit(1)

def parse_file_args(input):
    files = []
    cdid  = []
    for i in input:
        if i == 'dvd' or i == 'vcd' or i == 'cd':
            cdid += [ i ]
        else:
            files += [ i ]
    return files, cdid


#
# Main function
#
if __name__ == "__main__":
    import getopt

    drive = '/dev/cdrom'
    driveset = False

    task = ''
    search_arg = ''
    
    
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ag:s:', ('rom-drive=','list-guess='))
    except getopt.GetoptError:
        usage()
        pass
    
    for o, a in opts:
        if o == '-a':
            if task:
                usage()
            task = 'add'

        if o == '-s':
            if task:
                usage()
            task = 'search'
            search_arg = a

        if o == '-g':
            if task:
                usage()
            task = 'guess'
            search_arg = a

        if o == '--rom-drive':
            drive=a
            driveset = True

    fxd = FxdImdb()        
            
    if task == 'add':
        if len(args) == 2:
            usage()
        fxd.setFxdFile(arg[0])
        if fxd.isDiscset() == True:
            fxd.setDiscset(drive, None)
        elif fxd.isDiscset() == False:
            type = 'file'
            if arg[1].find('[dvd]') != -1: type = 'dvd'
            if arg[1].find('[vcd]') != -1: type = 'vcd'
            
            id = abs( Random() * 100 )
            if driveset == True:
                video = makeVideo(type, 'f' + str(id), arg[1], device=drive)
            else : video = makeVideo(type, 'f' + str(id), arg[1])
            fxd.setVideo(video)
        else:
            print 'Fxd file is not valid, updating failed'
            sys.exit(1)
        fxd.writeFxd()
        sys.exit(0)
    
    if task == 'search':
        if len(args) != 0:
            usage()

        filename = search_arg
        print "searching " + filename
        for result in fxd.searchImdb(filename):
            if result[3]:
                print '%s   %s (%s, %s)' % result
            else:
                print '%s   %s (%s)' % (result[0], result[1], result[2])
        sys.exit(0)


    if task == 'guess':
        filename = search_arg
        print "searching " + filename
        for result in fxd.guessImdb(filename):
            if result[3]:
                print '%s   %s (%s, %s)' % result
            else:
                print '%s   %s (%s)' % (result[0], result[1], result[2])
        sys.exit(0)
        
    # normal usage
    if len(args) < 2:
        usage()

    imdb_number = args[0]
    filename = args[1]


    files, cdid = parse_file_args(args[2:])

    if not (files or cdid):
        usage()
        
    fxd.setImdbId(imdb_number)
    fxd.setFxdFile(filename)
    
    x=0
    for file in files:
        type = 'file'
        if file.find('[dvd]') != -1: type = 'dvd'
        if file.find('[vcd]') != -1: type = 'vcd'
        if driveset == True: video = makeVideo(type, 'f' + str(x) , file, device=drive)
        else: video = makeVideo(type, 'f' + str(x), file)
        fxd.setVideo(video)
        x = x+1

    if not files:
        fxd.setDiscset(drive, None)
        
    fxd.writeFxd()
