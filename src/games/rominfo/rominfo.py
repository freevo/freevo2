#if 0 /*
# -----------------------------------------------------------------------
# rominfo.py - Some Utilities for roms
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/04/24 19:56:14  dischi
# comment cleanup for 1.3.2-pre4
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


import os
import sys
import zipfile

"""This file parses the output of 'xmame -listroms > romlist.txt'"""


class RomInfo:

    def __init__(self, filename='', filesize=0, crc=0):
        self.filename = filename
        self.filesize = filesize
        self.crc = crc

    def __str__(self):
        s = '%-15s %6s 0x%08x' % (self.filename, self.filesize, self.crc)
        return s


    def __cmp__(self, other):
        res = ((self.filename == other.filename) and
               (self.filesize == other.filesize) and
               (self.crc == other.crc))
        if res:
            return 0
        else:
            return cmp(self.filename, other.filename)

    
class GameInfo:

    def __init__(self, name=''):
        self.name = name
        self.roms = []  # List of RomInfo objects


    def __str__(self):
        s = 'Game %s\n' % self.name
        self.roms.sort()
        for rom in self.roms:
            s += '  %s\n' % rom
        return s


    def __cmp__(self, other):
        # Names don't matter

        # Check all roms
        # It is ok if there are more roms in the 'other' set,
        # it's still a match
        for rom in self.roms:
            found = 0
            for rom2 in other.roms:
                if rom == rom2:
                    found = 1
                    break
            if not found:
                return -1

        # If we get here all roms were matched
        return 0


crc_list = {}

# Initialize self from a text description of the game
def parse_gameinfo(lines):
    if lines[0].find('This is the list of the ROMs required') != 0:
        return None

    gamename = lines[0].split()[-1][1:-2]
    gi = GameInfo(gamename)

    for line in lines[2:]:
        if line.find('NO GOOD DUMP KNOWN') != -1:
            #print 'Game %s misses some roms.' % gamename
            return None
        
        romname, romsize, dummy, crc = line.split()
        romname = romname.lower()
        romsize = int(romsize)
        crc = long(crc, 16)

        if crc in crc_list:
            #print '%s in list already' % rinfo[0]
            crc_list[crc].append(gi)
        else:
            crc_list[crc] = [gi]

        gi.roms.append(RomInfo(romname, romsize, crc))

    return gi
        
    
def parse_romlist(fname):
    fd = open(fname)

    linesl = []

    curr = []
    while 1:

        line = fd.readline()
        if not line:
            break

        line = line.strip()
        if len(line):
            curr.append(line)
        else:
            if len(curr):
                linesl.append(curr)
                curr = []

    print 'Got %s records' % len(linesl)

    gamelist = []
    for lines in linesl:
        gi = parse_gameinfo(lines)
        if gi:
            gamelist.append(gi)


#
# Check if the ROM length is a power of 2
#
def chkromlength(size):
    while size and (size & 1) == 0:
        size = size >> 1

    if size & 0xffffffe:
        return 0
    else:
        return 1

    
def parse_zipfile(fname):
    archive = zipfile.ZipFile(open(fname))
    
    gi = GameInfo(fname)

    matches = []
    for f in archive.filelist:
        romname, romsize, crc = f.filename.lower(), f.file_size, f.CRC
        crc = long('%x' % crc, 16)
        print '%s: %s bytes, CRC 0x%08x %d' % (romname, romsize, crc, crc)
        if not chkromlength(romsize):
            print 'Not a ROM'
            continue

        if crc in crc_list:
            matchl = crc_list[crc]
            for match in matchl:
                if not match in matches:
                    #print '%s matches' % match.name
                    matches.append(match)
        else:
            print '%s: Couldnt match 0x%08x in the romlist!' % (fname, crc)
            return 0

        gi.roms.append(RomInfo(romname, romsize, crc))

    # Check the games in the 'matches' list
    print 'Checking matches for:'
    print gi
    glist = []
    for match in matches:
        print 'Checking if zipfile matches %s...' % match.name,
        if match == gi:
            print 'ok'
            glist.append(match)
        else:
            print 'fail'
            print match
        
    print 'Game:'
    print gi
    print
    print 'Matches:'
    for game in glist:
        print game
    

if __name__ == '__main__':
    parse_romlist(sys.argv[1])

    print 'parsed romlist'

    for fname in sys.argv[2:]:
        print '=' * 80
        print fname
        parse_zipfile(fname)
        print
