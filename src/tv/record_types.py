#if 0 /*
# -----------------------------------------------------------------------
# record_types.py - Some classes that are important to recording.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/05/11 22:41:51  rshortt
# Classes used by tv/recording apps.
#
# Revision 1.1  2003/04/26 12:55:04  rshortt
# Starting work on a recording server.
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

import sys
import time, os, string
# import config
# import rec_interface 
# from epg_types import TvProgram

from twisted.spread import pb

# The file format version number. It must be updated when incompatible
# changes are made to the file format.
TYPES_VERSION = 1

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0


class ScheduledRecordings:
 

    def __init__(self):
        self.programList = {}
	self.favorites = {}
        self.TYPES_VERSION = TYPES_VERSION
        

    def addProgram(self, prog, key=None):
        if not key:
            # key = rec_interface.getKey(prog)
            pass

        print 'addProgram: key is "%s"' % key
        if not self.programList.has_key(key):
            print 'addProgram: actually adding "%s"' % prog
            self.programList[key] = prog
        else:
            print 'We already know about this recording.'
        print 'addProgram: len is "%s"' % len(self.programList)


    def removeProgram(self, prog, key=None):
        if not key:
            # key = rec_interface.getKey(prog)
            pass

        if self.programList.has_key(key):
            del self.programList[key]
            print 'removed recording: %s' % prog
        else:
            print 'We do not know about this recording.'


    def getProgramList(self):
        return self.programList


    def setProgramList(self, pl):
        self.programList = pl


    def addFavorite(self, fav):
        if not self.favorites.has_key(fav.name):
            print 'addFavorites: actually adding "%s"' % fav.name
            self.favorites[fav.name] = fav
        else:
            print 'We already have a favorite called "%s".' % fav.name


    def removeFavorite(self, name):
        if self.favorites.has_key(name):
            del self.favorites[name]
            print 'removed favorite: %s' % name
        else:
            print 'We do not have a favorite called "%s".' % name


    def getFavorites(self):
        return self.favorites


    def setFavorites(self, favs):
        self.favorites = favs


    def setFavoritesList(self, favs):
        newfavs = {}

        for fav in favs:
            if not newfavs.has_key(fav.name):
                newfavs[fav.name] = fav

        self.setFavorites(newfavs)


    def clearFavorites(self):
        self.favorites = {}


class Favorite:


    def __init__(self, name=None, prog=None, exactchan=FALSE, exactdow=FALSE, 
                 exacttod=FALSE, priority=0):
        self.TYPES_VERSION = TYPES_VERSION
        self.name = name
        self.priority = priority

        if prog:
            self.title = prog.title

	    if exactchan:
                self.channel_id = prog.channel_id
            else:
                self.channel_id = 'ANY'
          
	    if exactdow:
	        lt = time.localtime(prog.start)
                self.dow = lt[6]
            else:
                self.dow = 'ANY'
          
	    if exacttod:
	        # TODO: translate the TOD from prog.start
	        lt = time.localtime(prog.start)
                # self.tod = '%s:%s' % (lt[3], lt[4])
                self.mod = (lt[3]*60)+lt[4]
            else:
                self.mod = 'ANY'

        else:
            self.title = 'NONE'
            self.channel_id = 'NONE'
            self.dow = 'NONE'
            self.mod = 'NONE'


class ScheduledTvProgram:

    LOW_QUALTY  = 1
    MED_QUALTY  = 2
    HIGH_QUALTY = 3

    def __init__(self):
        self.tunerid      = None
        self.isRecording  = FALSE
        self.isFavorite   = FALSE
        self.favoriteName = None
        self.removed      = FALSE
        self.quality      = self.HIGH_QUALITY


