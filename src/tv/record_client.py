#!/usr/bin/env python

#if 0 /*
# -----------------------------------------------------------------------
# record_client.py - A client interface to the Freevo recording server.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/05/13 16:13:24  rshortt
# Added updateFavoritesSchedule to the interface and make it accessable through
# the command-line of record_client.py.
#
# Revision 1.3  2003/05/13 01:20:22  rshortt
# Bugfixes.
#
# Revision 1.2  2003/05/12 11:21:51  rshortt
# bugfixes
#
# Revision 1.1  2003/05/11 22:41:22  rshortt
# The client interface to the recording server.
#
# Revision 1.4  2003/04/28 02:51:31  rshortt
# Making some progress here.
#
# Revision 1.3  2003/04/26 18:01:02  rshortt
# *** empty log message ***
#
# Revision 1.2  2003/04/26 15:52:05  rshortt
# *** empty log message ***
#
# Revision 1.1  2003/04/26 12:55:04  rshortt
# Starting work on a recording server.
#
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

import config

import time, sys
import xmlrpclib
from twisted.persisted import marmalade

TRUE = 1
FALSE = 0

server_string = 'http://%s:%s/' % \
                (config.RECORD_SERVER_IP, config.RECORD_SERVER_PORT)

server = xmlrpclib.Server(server_string)


def returnFromJelly(status, response):
    # print 'DEBUG::response: %s' % response
    if status:
        return (status, marmalade.unjellyFromXML(response))
    else:
        return (status, response)
   

def getScheduledRecordings():
    (status, message) = server.getScheduledRecordings()
    return returnFromJelly(status, message)


def saveScheduledRecordings(scheduledRecordings):
    (status, message) = server.saveScheduledRecordings(scheduledRecordings)
    return (status, message)


def echotest(teststr):
    return server.echotest('blah blah blah')


def scheduleRecording(prog=None):
    if not prog:
        print 'ERROR: no prog'
        return

    if prog.stop < time.time():
        print 'ERROR: cannot record it if it is over'
        return
        
    (status, message) = server.scheduleRecording(marmalade.jellyToXML(prog))
    return (status, message)


def removeScheduledRecording(prog=None):
    if not prog:
        return (FLASE, 'no prog')

    (status, message) = server.removeScheduledRecording(marmalade.jellyToXML(prog))
    return (status, message)


def cleanScheduledRecordings():
    (status, message) = server.cleanScheduledRecordings()
    return (status, message)


def isProgScheduled(prog, schedule=None):
    if schedule or schedule == {}:
        if schedule == {}:
            return (FALSE, 'prog not scheduled')

        for me in schedule.values():
            if me.start == prog.start and me.channel_id == prog.channel_id:
                return (TRUE, 'prog is scheduled')

        return (FALSE, 'prog not scheduled')
    else:
        (status, message) = server.isProgScheduled(marmalade.jellyToXML(prog), 
                                                   schedule)
        return (status, message) 
    

def findProg(chan, start):
    (status, response) = server.findProg(chan, start)

    return returnFromJelly(status, response)
    

def findMatches(find=None):
    (status, response) = server.findMatches(find)

    return returnFromJelly(status, response)


def addFavorite(name, prog, exactchan, exactdow, exacttod):
    (status, message) = server.addFavorite(name, prog, exactchan, exactdow, exacttod)
    return (status, message) 


def addEditedFavorite(name, title, chan, dow, mod, priority):
    (status, message) = server.addEditedFavorite(name, title, chan, dow, mod, priority)
    return (status, message) 


def removeFavorite(name):
    print 'CLIENT REMOVE FAVORITE: %s' % name
    (status, message) = server.removeFavorite(name)
    return (status, message) 


def clearFavorites():
    (status, message) = server.clearFavorites()
    return (status, message) 


def getFavorites():
    (status, response) = server.getFavorites()

    return returnFromJelly(status, response)


def getFavorite(name):
    print 'RCLIENT wants fav %s' % name
    (status, response) = server.getFavorite(name)

    return returnFromJelly(status, response)


def adjustPriority(favname, mod):
    (status, message) = server.adjustPriority(favname, mod)
    return (status, message) 


def isProgAFavorite(prog, favs):
    (status, message) = server.isProgAFavorite(marmalade.jellyToXML(prog), 
                                               marmalade.jellyToXML(favs))
    return (status, message) 


def removeFavoriteFromSchedule(fav):
    (status, message) = server.removeFavoriteFromSchedule(fav)
    return (status, message) 


def addFavoriteToSchedule(fav):
    (status, message) = server.addFavoriteToSchedule(fav)
    return (status, message) 


def updateFavoritesSchedule():
    (status, message) = server.updateFavoritesSchedule()
    return (status, message) 


if __name__ == '__main__':
    if len(sys.argv) >= 2: 
        function = sys.argv[1]
    else:
        function = 'none'


    if function == "updateFavoritesSchedule":
        (result, response) = updateFavoritesSchedule()
        print response


