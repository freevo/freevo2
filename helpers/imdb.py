#!/usr/bin/env python
#if 0 /*
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
# Revision 1.27  2003/08/04 18:42:03  dischi
# remove some stuff we do not need with the new freevo script
#
# Revision 1.26  2003/07/18 21:31:03  dischi
# new imdb helper based in the new fxdimdb
#
# Revision 1.26 2003/07/16 22:07:00 den_RDC
#   rewrite to use fxd_imdb class
#
# Revision 1.25  2003/06/25 15:37:37  dischi
# some try-except if you can't write files
#
# Revision 1.24  2003/06/24 18:38:41  dischi
# Fixed handling when search returns only one result
#
# Revision 1.23  2003/06/24 18:12:45  dischi
# fixed string translation with urllib (not urllib2)
#
# Revision 1.22  2003/06/24 16:15:07  dischi
# o updated by den_RDC - changed code to urllib2 - exceptions are handled by
#   urllib2, including 302 redirection -- proxy servers ,including transparant
#   proxies now work
# o added support for better image finder. Right now there we can also get
#   posters from www.impawards.com
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
import os

import config

from video.fxdimdb import FxdImdb, makeVideo
from random import Random


FALSE = 0
TRUE = 1

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
    driveset = FALSE

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
            driveset = TRUE

    fxd = FxdImdb()        
            
    if task == 'add':
        if len(args) == 2:
            usage()
        fxd.setFxdFile(arg[0])
        if fxd.isDiscset() == TRUE:
            fxd.setDiscset(drive, None)
        elif fxd.isDiscset() == FALSE:
            type = 'file'
            if arg[1].find('[dvd]') != -1: type = 'dvd'
            if arg[1].find('[vcd]') != -1: type = 'vcd'
            
            id = abs( Random() * 100 )
            if driveset == TRUE:
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
        if driveset == TRUE: video = makeVideo(type, 'f' + str(x) , file, device=drive)
        else: video = makeVideo(type, 'f' + str(x), file)
        fxd.setVideo(video)
        x = x+1
        
    fxd.writeFxd()
