# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mame_types.py - Some classes to keep track of information from MAME
#                 roms.  The cache makes use of this.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2005/01/08 15:40:51  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.6  2004/07/10 12:33:38  dischi
# header cleanup
#
# Revision 1.5  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.4  2003/06/20 01:33:56  rshortt
# Removing the need for the rominfo program.  Now we parse the output of
# xmame --listinfo directly and build a list of all supported MAME roms.
# This should only need to be updated when you upgrade xmame and you should
# remove your existing romlist-n.pickled.
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
import time, os, string
import config

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
TYPES_VERSION = 2

class MameRom:

    def __init__(self):
        self.filename = ''
        self.title = ''
        self.name = ''
        self.description = ''
        self.year = ''
        self.manufacturer = ''
        self.cloneof = ''
        self.romof = ''


    def getFilename(self):
        return self.filename

    def setFilename(self, f):
        self.filename = f

    def getDirname(self):
        return self.dirname

    def setDirname(self, d):
        self.dirname = d

    def getTitle(self):
        return self.title

    def setTitle(self, t):
        self.title = t

    def getImageFile(self):
        return self.imageFile

    def setImageFile(self, i):
        self.imageFile = i

    def getPartial(self):
        return self.partial

    def setPartial(self, p):
        self.partial = p

    def getMatched(self):
        return self.matched

    def setMatched(self, m):
        self.matched = m

    def getTrashme(self):
        return self.trashme

    def setTrashme(self, t):
        self.trashme = t


class MameRomList:
    # We are using a dictionary that will be keyed on the
    # absolute filename of the actual rom.
    mameRoms = {}
 
    def __init__(self):
        self.TYPES_VERSION = TYPES_VERSION
        
    def addMameRom(self, rom):
        if not self.mameRoms.has_key(rom.getFilename()):
            self.mameRoms[rom.getFilename()] = rom
        else:
            print "We already know about %s." % rom.getFilename()

    def getMameRoms(self):
        return self.mameRoms

    def setMameRoms(self, mr):
        self.mameRoms = mr

    def Sort(self):
        self.mameRoms.Sort()
        

