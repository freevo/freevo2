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
# Revision 1.6  2003/05/14 00:18:55  rshortt
# Better error handling.
#
# Revision 1.5  2003/05/14 00:04:54  rshortt
# Better error handling.
#
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

import time, sys, socket
import xmlrpclib
from twisted.persisted import marmalade

TRUE = 1
FALSE = 0

server_string = 'http://%s:%s/' % \
                (config.RECORD_SERVER_IP, config.RECORD_SERVER_PORT)

server = xmlrpclib.Server(server_string)


def returnFromJelly(status, response):
    if status:
        return (status, marmalade.unjellyFromXML(response))
    else:
        return (status, response)
   

def getScheduledRecordings():
    try: 
        (status, message) = server.getScheduledRecordings()
    except:
        return (FALSE, 'record_client: connection error')

    return returnFromJelly(status, message)


def saveScheduledRecordings(scheduledRecordings):
    try:
        (status, message) = server.saveScheduledRecordings(scheduledRecordings)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message)


def connectionTest(teststr='testing'):
    try:
        (status, message) = server.echotest(teststr)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message)


def scheduleRecording(prog=None):
    if not prog:
        print 'ERROR: no prog'
        return

    if prog.stop < time.time():
        print 'ERROR: cannot record it if it is over'
        return
        
    try:
        (status, message) = server.scheduleRecording(marmalade.jellyToXML(prog))
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message)


def removeScheduledRecording(prog=None):
    if not prog:
        return (FLASE, 'no prog')

    try:
        (status, message) = server.removeScheduledRecording(marmalade.jellyToXML(prog))
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message)


def cleanScheduledRecordings():
    try:
        (status, message) = server.cleanScheduledRecordings()
    except:
        return (FALSE, 'record_client: connection error')

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
        try:
            (status, message) = server.isProgScheduled(marmalade.jellyToXML(prog), 
                                                       schedule)
        except:
            return (FALSE, 'record_client: connection error')

        return (status, message) 
    

def findProg(chan, start):
    try:
        (status, response) = server.findProg(chan, start)
    except:
        return (FALSE, 'record_client: connection error')


    return returnFromJelly(status, response)
    

def findMatches(find=None):
    try:
        (status, response) = server.findMatches(find)
    except:
        return (FALSE, 'record_client: connection error')


    return returnFromJelly(status, response)


def addFavorite(name, prog, exactchan, exactdow, exacttod):
    try:
        (status, message) = server.addFavorite(name, prog, exactchan, exactdow, exacttod)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def addEditedFavorite(name, title, chan, dow, mod, priority):
    try:
        (status, message) = server.addEditedFavorite(name, title, chan, dow, mod, priority)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def removeFavorite(name):
    try:
        (status, message) = server.removeFavorite(name)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def clearFavorites():
    try:
        (status, message) = server.clearFavorites()
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def getFavorites():
    try:
        (status, response) = server.getFavorites()
    except:
        return (FALSE, 'record_client: connection error')


    return returnFromJelly(status, response)


def getFavorite(name):
    try:
        (status, response) = server.getFavorite(name)
    except:
        return (FALSE, 'record_client: connection error')


    return returnFromJelly(status, response)


def adjustPriority(favname, mod):
    try:
        (status, message) = server.adjustPriority(favname, mod)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def isProgAFavorite(prog, favs):
    try:
        (status, message) = server.isProgAFavorite(marmalade.jellyToXML(prog), 
                                                   marmalade.jellyToXML(favs))
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def removeFavoriteFromSchedule(fav):
    try:
        (status, message) = server.removeFavoriteFromSchedule(fav)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def addFavoriteToSchedule(fav):
    try:
        (status, message) = server.addFavoriteToSchedule(fav)
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


def updateFavoritesSchedule():
    try:
        (status, message) = server.updateFavoritesSchedule()
    except:
        return (FALSE, 'record_client: connection error')

    return (status, message) 


if __name__ == '__main__':
    if len(sys.argv) >= 2: 
        function = sys.argv[1]
    else:
        function = 'none'


    if function == "updateFavoritesSchedule":
        (result, response) = updateFavoritesSchedule()
        print response


    if function == "test":
        (result, response) = connectionTest('connection test')
        print 'result: %s, response: %s ' % (result, response)


