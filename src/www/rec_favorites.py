#if 0 /*
# -----------------------------------------------------------------------
# rec_favorites.py - A module to make sure we record our favorites.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/02/08 18:35:26  dischi
# added new version of freevoweb from Rob Shortt
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

import sys, string
import random
import time, os, string
import cPickle as pickle

# Configuration file. 
import config

# Various utilities
import util

# RegExp
import re

import rec_types
import rec_interface as ri
import epg_xmltv


# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0



def addFavorite(name, prog, exactchan=FALSE, exactdow=FALSE, exacttod=FALSE):
    if not name:
        print 'ERROR: no name'
        return

    priority = len(getFavorites()) + 1
    fav = rec_types.Favorite(name, prog, exactchan, exactdow, exacttod, priority)

    scheduledRecordings = ri.getScheduledRecordings()
    scheduledRecordings.addFavorite(fav)
    ri.saveScheduledRecordings(scheduledRecordings)
    addFavoriteToSchedule(fav)


def addEditedFavorite(name, title, chan, dow, mod, priority):
    fav = rec_types.Favorite()

    fav.name = name
    fav.title = title
    fav.channel_id = chan
    fav.dow = dow
    fav.mod = mod
    fav.priority = priority

    scheduledRecordings = ri.getScheduledRecordings()
    scheduledRecordings.addFavorite(fav)
    ri.saveScheduledRecordings(scheduledRecordings)
    addFavoriteToSchedule(fav)


def removeFavorite(name=None):
    if not name:
        print 'ERROR: no name'
        return

   
    removeFavoriteFromSchedule(getFavorite(name))
    scheduledRecordings = ri.getScheduledRecordings()
    scheduledRecordings.removeFavorite(name)
    ri.saveScheduledRecordings(scheduledRecordings)
   

def clearFavorites():
    scheduledRecordings = ri.getScheduledRecordings()
    scheduledRecordings.clearFavorites()
    ri.saveScheduledRecordings(scheduledRecordings)


def getFavorites():
    return ri.getScheduledRecordings().getFavorites()


def getFavorite(name):
    favs = getFavorites()

    if favs.has_key(name):
        fav = favs[name] 
    else:
        fav = None

    return fav


def adjustPriority(favname, mod=0):
    save = []
    mod = int(mod)
    me = getFavorite(favname)
    oldprio = int(me.priority)
    newprio = oldprio + mod

    tmp = 'ap: mod=%s\n' % mod
    sys.stderr.write(tmp)
   
    sr = ri.getScheduledRecordings()
    favs = sr.getFavorites().values()

    sys.stderr.write('adjusting prio of '+favname+'\n')
    for fav in favs:
        fav.priority = int(fav.priority)

        if fav.name == me.name:
            sys.stderr.write('  MATCH')
            fav.priority = newprio
            tmp = '  moved prio of %s: %s => %s\n' % (fav.name, oldprio, newprio)
            sys.stderr.write(tmp)
            continue
        if mod < 0:
            if fav.priority < newprio or fav.priority > oldprio:
                tmp = '  fp: %s, old: %s, new: %s\n' % (fav.priority, oldprio, newprio)
                sys.stderr.write(tmp)
                tmp = '  skipping: %s\n' % fav.name
                sys.stderr.write(tmp)
                continue
            fav.priority = fav.priority + 1
            tmp = '  moved prio of %s: %s => %s\n' % (fav.name, fav.priority-1, fav.priority)
            sys.stderr.write(tmp)
            
        if mod > 0:
            if fav.priority > newprio or fav.priority < oldprio:
                tmp = '  skipping: %s\n' % fav.name
                sys.stderr.write(tmp)
                continue
            fav.priority = fav.priority - 1
            tmp = '  moved prio of %s: %s => %s\n' % (fav.name, fav.priority+1, fav.priority)
            sys.stderr.write(tmp)

    sr.setFavoritesList(favs)
    ri.saveScheduledRecordings(sr)
   


def isProgAFavorite(prog, favs=None):
  
    if not favs:
        favs = getFavorites()

    lt = time.localtime(prog.start)
    dow = '%s' % lt[6]
    # tod = '%s:%s' % (lt[3], lt[4])
    # mins_in_day = 1440
    min_of_day = '%s' % ((lt[3]*60)+lt[4])

    for fav in favs.values():

        if prog.title == fav.title:    
            if fav.channel_id == prog.channel_id or fav.channel_id == 'ANY':
                if fav.dow == dow or fav.dow == 'ANY':
                    if fav.mod == min_of_day or fav.mod == 'ANY':
                        return fav.name
                    elif abs(int(fav.mod) - int(min_of_day)) <= 8:
                        return fav.name
                        

    # if we get this far prog is not a favorite
    return FALSE


def removeFavoriteFromSchedule(fav):
    # TODO: make sure the program we remove is not
    #       covered by another favorite.

    tmp = {}
    tmp[fav.name] = fav

    scheduledRecordings = ri.getScheduledRecordings()
    progs = scheduledRecordings.getProgramList()
    for prog in progs.values():
        if isProgAFavorite(prog, tmp):
            ri.removeScheduledRecording(prog)


def addFavoriteToSchedule(fav):
    favs = {}
    favs[fav.name] = fav
    guide = epg_xmltv.get_guide()

    for ch in guide.chan_list:
        for prog in ch.programs:
            favorite = isProgAFavorite(prog, favs)
            if favorite:
                prog.isFavorite = favorite
                ri.scheduleRecording(prog)


def updateFavoritesSchedule():
    #  TODO: do not re-add a prog to record if we have
    #        previously decided not to record it.

    guide = epg_xmltv.get_guide()

    # First get the timeframe of the guide.
    last = 0
    for ch in guide.chan_list:
        for prog in ch.programs:
            if prog.start > last: last = prog.start

    scheduledRecordings = ri.getScheduledRecordings()

    favs = getFavorites()

    # Then remove all scheduled favorites in that timeframe to
    # make up for schedule changes.
    progs = scheduledRecordings.getProgramList()
    for prog in progs.values():

        # try:
        #     favorite = prog.isFavorite
        # except:
        #     favorite = FALSE

        # if prog.start <= last and favorite:
        if prog.start <= last and isProgAFavorite(prog, favs):
            ri.removeScheduledRecording(prog)

    for ch in guide.chan_list:
        for prog in ch.programs:
            favorite = isProgAFavorite(prog, favs)
            if favorite:
                prog.isFavorite = favorite
                ri.scheduleRecording(prog)


def main():
    updateFavoritesSchedule()


if __name__ == '__main__':
    main()
     

