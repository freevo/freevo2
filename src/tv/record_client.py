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
# Revision 1.18  2004/03/13 20:11:36  rshortt
# Some quick debug for addEditedFavorite()
#
# Revision 1.17  2004/03/13 18:31:51  rshortt
# Lets see traceback and exception.  We should clean this file up further.
#
# Revision 1.16  2004/03/08 19:15:49  dischi
# use our marmalade
#
# Revision 1.15  2004/03/05 20:49:11  rshortt
# Add support for searching by movies only.  This uses the date field in xmltv
# which is what tv_imdb uses and is really acurate.  I added a date property
# to TvProgram for this and updated findMatches in the record_client and
# recordserver.
#
# Revision 1.14  2004/02/23 21:41:10  dischi
# start some unicode fixes, still not working every time
#
# Revision 1.13  2004/02/23 08:22:10  gsbarbieri
# i18n: help translators job.
#
# Revision 1.12  2004/01/09 02:07:05  rshortt
# Marmalade name and title for favorites.  Thanks Matthieu Weber.
#
# Revision 1.11  2003/11/30 16:30:58  rshortt
# Convert some tv variables to new format (TV_).
#
# Revision 1.10  2003/11/16 17:38:48  dischi
# i18n patch from David Sagnol
#
# Revision 1.9  2003/09/05 02:32:46  rshortt
# Getting rid of the hack to strip out "tv." because it is now safe to import the tv namespace.
#
# This hack also messed up any new xmltv data that had "tv." in a channel id.
#
# Revision 1.8  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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

import time, sys, socket, traceback, string
import xmlrpclib
import epg_types

from util.marmalade import jellyToXML, unjellyFromXML

TRUE  = 1
FALSE = 0

server_string = 'http://%s:%s/' % \
                (config.TV_RECORD_SERVER_IP, config.TV_RECORD_SERVER_PORT)

server = xmlrpclib.Server(server_string)

def returnFromJelly(status, response):
    if status:
        return (status, unjellyFromXML(response))
    else:
        return (status, response)
   

def getScheduledRecordings():
    try: 
        (status, message) = server.getScheduledRecordings()
    except Exception, e:
        print e
        return (FALSE, 'record_client: '+_('connection error'))

    return returnFromJelly(status, message)


def saveScheduledRecordings(scheduledRecordings):
    try:
        (status, message) = server.saveScheduledRecordings(scheduledRecordings)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message)


def connectionTest(teststr='testing'):
    try:
        (status, message) = server.echotest(teststr)
    except Exception, e:
        print e
        traceback.print_exc()
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message)


def scheduleRecording(prog=None):
    if not prog:
        return (FALSE, _('no program'))

    if prog.stop < time.time():
        return (FALSE, _('ERROR')+': '+_('cannot record it if it is over'))
        
    try:
        (status, message) = server.scheduleRecording(jellyToXML(prog))
    except:
        traceback.print_exc()
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message)


def removeScheduledRecording(prog=None):
    if not prog:
        return (FLASE, _('no program'))

    try:
        (status, message) = server.removeScheduledRecording(jellyToXML(prog))
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message)


def cleanScheduledRecordings():
    try:
        (status, message) = server.cleanScheduledRecordings()
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message)


def isProgScheduled(prog, schedule=None):
    if schedule or schedule == {}:
        if schedule == {}:
            return (FALSE, _('program not scheduled'))

        for me in schedule.values():
            if me.start == prog.start and me.channel_id == prog.channel_id:
                return (TRUE, _('program is scheduled'))

        return (FALSE, _('program not scheduled'))
    else:
        try:
            (status, message) = server.isProgScheduled(jellyToXML(prog), schedule)
        except:
            return (FALSE, 'record_client: '+_('connection error'))

        return (status, message) 
    

def findProg(chan, start):
    try:
        (status, response) = server.findProg(chan, start)
    except:
        return (FALSE, 'record_client: '+_('connection error'))


    return returnFromJelly(status, response)
    

def findMatches(find='', movies_only=0):
    try:
        (status, response) = server.findMatches(find, movies_only)
    except Exception, e:
        print 'Search error for \'%s\'' % find
        print e
        return (FALSE, 'record_client: '+_('connection error'))

    return returnFromJelly(status, response)


def addFavorite(name, prog, exactchan, exactdow, exacttod):
    try:
        (status, message) = server.addFavorite(name, prog, exactchan, exactdow, exacttod)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def addEditedFavorite(name, title, chan, dow, mod, priority):
    try:
        (status, message) = \
            server.addEditedFavorite(jellyToXML(name), \
            jellyToXML(title), chan, dow, mod, priority)
    except Exception, e:
        print e
        traceback.print_exc()
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def removeFavorite(name):
    try:
        (status, message) = server.removeFavorite(name)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def clearFavorites():
    try:
        (status, message) = server.clearFavorites()
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def getFavorites():
    try:
        (status, response) = server.getFavorites()
    except:
        return (FALSE, 'record_client: '+_('connection error'))


    return returnFromJelly(status, response)


def getFavorite(name):
    try:
        (status, response) = server.getFavorite(name)
    except:
        return (FALSE, 'record_client: '+_('connection error'))


    return returnFromJelly(status, response)


def adjustPriority(favname, mod):
    try:
        (status, message) = server.adjustPriority(favname, mod)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def isProgAFavorite(prog, favs):
    try:
        (status, message) = server.isProgAFavorite(jellyToXML(prog), jellyToXML(favs))
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def removeFavoriteFromSchedule(fav):
    try:
        (status, message) = server.removeFavoriteFromSchedule(fav)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def addFavoriteToSchedule(fav):
    try:
        (status, message) = server.addFavoriteToSchedule(fav)
    except:
        return (FALSE, 'record_client: '+_('connection error'))

    return (status, message) 


def updateFavoritesSchedule():
    try:
        (status, message) = server.updateFavoritesSchedule()
    except:
        return (FALSE, 'record_client: '+_('connection error'))

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

    if function == "moviesearch":
        if len(sys.argv) >= 3:
            find = sys.argv[2]
        else:
            find = ''

        (result, response) = findMatches(find, 1)
        if result:
            for prog in response:
                print 'Prog: %s' % prog.title
        else:
            print 'result: %s, response: %s ' % (result, response)


