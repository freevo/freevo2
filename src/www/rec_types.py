#if 0 /*
# -----------------------------------------------------------------------
# rec_types.py - Some classes that are important to recording.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/01/29 05:29:34  krister
# Rob Shortts WWW server scripts for Freevo recording.
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
import time, os, string
import config
import rec_interface 

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
TYPES_VERSION = 1

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


class ScheduledRecordings:
 

    def __init__(self):
        self.programList = {}
        self.TYPES_VERSION = TYPES_VERSION
        

    def addProgram(self, prog, key=None):
        if not key:
            key = rec_interface.getKey(prog)

        print 'addProgram: key is "%s"' % key
        if not self.programList.has_key(key):
            print 'addProgram: actually adding "%s"' % prog
            self.programList[key] = prog
        else:
            print 'We already know about this recording.'
        print 'addProgram: len is "%s"' % len(self.programList)


    def removeProgram(self, prog, key=None):
        if not key:
            key = rec_interface.getKey(prog)

        if self.programList.has_key(key):
            del self.programList[key]
            print 'removed recording: %s' % prog
        else:
            print 'We do not know about this recording.'


    def getProgramList(self):
        return self.programList


    def setProgramList(self, pl):
        self.programList = pl



class Favorite:


    def __init__(self, prio=0, prog=None):
        self.TYPES_VERSION = TYPES_VERSION
        self.title = prog.title



