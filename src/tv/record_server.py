#!/usr/bin/env python

#if 0 /*
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.6  2003/05/20 23:43:58  rshortt
# Improve search using regex.
#
# Revision 1.5  2003/05/14 00:04:54  rshortt
# Better error handling.
#
# Revision 1.4  2003/05/13 16:13:23  rshortt
# Added updateFavoritesSchedule to the interface and make it accessable through
# the command-line of record_client.py.
#
# Revision 1.3  2003/05/13 01:20:22  rshortt
# Bugfixes.
#
# Revision 1.2  2003/05/12 11:21:51  rshortt
# bugfixes
#
# Revision 1.1  2003/05/12 02:09:06  rshortt
# A new recording backend which is intended to run outside of the main freevo process.
#
# Revision 1.6  2003/05/11 22:28:50  rshortt
# Now uses the plugin interface to get a recording childapp.
#
# Revision 1.5  2003/05/06 01:40:01  rshortt
# Now uses a childapp to record.  I'm going to make that part into a plugin next.
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

import sys, string, random, time, os, re

from twisted.web import xmlrpc, server
from twisted.internet.app import Application
from twisted.internet import reactor
from twisted.persisted import marmalade
from twisted.python import log

from record_types import TYPES_VERSION
from record_types import ScheduledRecordings

import record_types
import epg_xmltv
import tv_util
import plugin

# We need to locate record_config.py
cfgfilepath = [ os.environ['FREEVO_STARTDIR'],
                os.path.expanduser('~/.freevo'),
                '/etc/freevo',
                '.' ]

got_cfg = 0
for dirname in cfgfilepath:
    cfgfilename = dirname + '/record_config.py'
    if os.path.isfile(cfgfilename):
        print 'Loading cfg: %s' % cfgfilename
        execfile(cfgfilename, globals(), locals())
        got_cfg = 1
        break

if not got_cfg:
    print "\nERROR: can't find record_config.py"
    sys.exit(1)


plugin.init()

DEBUG = 1

TRUE = 1
FALSE = 0

appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logfile = '/var/log/freevo/internal-%s-%s.log' % (appname, os.getuid())
log.startLogging(open(logfile, 'a'))


## Note: config.RECORD_SCHEDULE is an xml file.

class RecordServer(xmlrpc.XMLRPC):

    # note: add locking and r/rw options to get/save funs
    def getScheduledRecordings(self):
        file_ver = None
        scheduledRecordings = None

        if os.path.isfile(RECORD_SCHEDULE):
            if DEBUG: log.debug('GET: reading cached file (%s)' % RECORD_SCHEDULE)
            scheduledRecordings = marmalade.unjellyFromXML(open(RECORD_SCHEDULE, 'r'))
    
            try:
                file_ver = scheduledRecordings.TYPES_VERSION
            except AttributeError:
                log.debug('The cache does not have a version and must be recreated.')
    
            if file_ver != TYPES_VERSION:
                log.debug(('ScheduledRecordings version number %s is stale (new is %s), must ' +
                        'be reloaded') % (file_ver, TYPES_VERSION))
            else:
                if DEBUG:
                    log.debug('Got ScheduledRecordings (version %s).' % file_ver)
    
        if scheduledRecordings == None:
            log.debug('GET: making a new ScheduledRecordings')
            scheduledRecordings = ScheduledRecordings()
    
        log.debug('ScheduledRecordings has %s items.' % len(scheduledRecordings.programList))
    
        return scheduledRecordings
    
    
    #
    # function to save the schedule to disk
    #
    def saveScheduledRecordings(self, scheduledRecordings=None):
    
        if not scheduledRecordings:
            if DEBUG: print 'SAVE: making a new ScheduledRecordings'
            scheduledRecordings = ScheduledRecordings()
    
        if DEBUG: log.debug('SAVE: saving cached file (%s)' % RECORD_SCHEDULE)
        if DEBUG: log.debug("SAVE: ScheduledRecordings has %s items." % len(scheduledRecordings.programList))
        marmalade.jellyToXML(scheduledRecordings, open(RECORD_SCHEDULE, 'w'))
        return TRUE

 
    def scheduleRecording(self, prog=None):
        global guide

        if not prog:
            return (FALSE, 'no prog')
    
        if prog.stop < time.time():
            return (FALSE, 'cannot record it if it is over')
            
        self.updateGuide()
    
        for chan in guide.chan_list:
            if prog.channel_id == chan.id:
                log.debug('scheduleRecording: prog.channel_id="%s" chan.id="%s" chan.tunerid="%s"' % (prog.channel_id, chan.id, chan.tunerid))
                prog.tunerid = chan.tunerid
    
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.addProgram(prog, tv_util.getKey(prog))
        self.saveScheduledRecordings(scheduledRecordings)
       
        return (TRUE, 'recording scheduled')
    

    def removeScheduledRecording(self, prog=None):
        if not prog:
            return (FALSE, 'no prog')

        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.removeProgram(prog, tv_util.getKey(prog))
        self.saveScheduledRecordings(scheduledRecordings)
       
        return (TRUE, 'recording removed')
   

    def isProgScheduled(self, prog, schedule=None):
    
        if schedule == {}:
            return (FALSE, 'prog not scheduled')

        if not schedule:
            schedule = self.getScheduledRecordings().getProgramList()

        for me in schedule.values():
            if me.start == prog.start and me.channel_id == prog.channel_id:
                return (TRUE, 'prog is scheduled')

        return (FALSE, 'prog not scheduled')


    def findProg(self, chan=None, start=None):
        global guide

        log.debug('findProg: %s, %s' % (chan, start))

        if not chan or not start:
            return (FALSE, 'no chan or no start')

        self.updateGuide()

        for ch in guide.chan_list:
            if chan == ch.id:
                log.debug('CHANNEL MATCH')
                for prog in ch.programs:
                    if start == '%s' % prog.start:
                        log.debug('PROGRAM MATCH')
                        return (TRUE, prog)

        return (FALSE, 'prog not found')


    def findMatches(self, find=None):
        global guide

        log.debug('findMatches: %s' % find)
    
        matches = []

        if not find:
            log.debug('nothing to find')
            return []

        self.updateGuide()

        pattern = '.*' + find + '\ *'
        regex = re.compile(pattern, re.IGNORECASE)
        now = time.time()

        for ch in guide.chan_list:
            for prog in ch.programs:
                if prog.stop < now:
                    continue
                if regex.match(prog.title) or regex.match(prog.desc):
                    log.debug('PROGRAM MATCH: %s' % prog)
                    matches.append(prog)

        if matches:
            return (TRUE, matches)
        else:
            return (FALSE, 'no matches')


    def updateGuide(self):
        global guide

        # XXX TODO: only do this if the guide has changed?
        guide = epg_xmltv.get_guide()

        
    def checkToRecord(self):
        log.debug('in checkToRecord')
        rec_cmd = None
        rec_prog = None
        cleaned = None
        scheduledRecordings = self.getScheduledRecordings()

        progs = scheduledRecordings.getProgramList()

        now = time.time()
        for prog in progs.values():
            log.debug('checkToRecord: progloop = %s' % prog)

            try:
                recording = prog.isRecording
            except:
                recording = FALSE

            if prog.start <= now and prog.stop >= now and recording == FALSE:
                # just add to the 'we want to record this' list
                # then end the loop, and figure out which has priority,
                # remember to take into account the full length of the shows
                # and how much they overlap, or chop one short
                # yeah thats a good idea but make sure its not like 5 mins

                duration = int(prog.stop - now - 10)
                if duration < 10:
                    return FALSE
                # title = tv_util.getProgFilename(prog)
                # rec_cmd = '%s %s %s "%s"' % \
                #   (config.REC_CMD, prog.tunerid, duration, title)
                # aflags = '-d /dev/dsp1 -r 32000 -b 16 -s -ab 128'
                # vflags = '-input Television -vb 1400 -vq 100 -w 480 -h 360'

                # cl_options = { 'channel'  : prog.tunerid,
                #                'filename' : title,
                #                'seconds'  : duration }

                # rec_cmd = config.VCR_CMD % cl_options

                # rec_cmd = '/var/media/bin/tvrecord %s %s "%s"' % \
                #    (prog.tunerid, duration, title)

                # log.debug('REC_CMD: %s' % rec_cmd)
                log.debug('going to record: %s' % prog)
                prog.isRecording = TRUE
                prog.rec_duration = duration
                prog.filename = tv_util.getProgFilename(prog)
                rec_prog = prog


        for prog in progs.values():
            # If the program is over remove the entry.
            if prog.stop < now:
                log.debug('found a program to clean')
                cleaned = TRUE
                del progs[tv_util.getKey(prog)]

        if rec_prog or cleaned:
            scheduledRecordings.setProgramList(progs)
            self.saveScheduledRecordings(scheduledRecordings)
            return rec_prog

        return FALSE


    def addFavorite(self, name, prog, exactchan=FALSE, exactdow=FALSE, exacttod=FALSE):
        if not name:
            return (FALSE, 'no name')
    
        (status, favs) = self.getFavorites()
        priority = len(favs) + 1
        fav = record_types.Favorite(name, prog, exactchan, exactdow, exacttod, priority)
    
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.addFavorite(fav)
        self.saveScheduledRecordings(scheduledRecordings)
        self.addFavoriteToSchedule(fav)

        return (TRUE, 'favorite added')
    
    
    def addEditedFavorite(self, name, title, chan, dow, mod, priority):
        fav = record_types.Favorite()
    
        fav.name = name
        fav.title = title
        fav.channel_id = chan
        fav.dow = dow
        fav.mod = mod
        fav.priority = priority
    
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.addFavorite(fav)
        self.saveScheduledRecordings(scheduledRecordings)
        self.addFavoriteToSchedule(fav)

        return (TRUE, 'favorite added')
    
    
    def removeFavorite(self, name=None):
        if not name:
            return (FALSE, 'no name')
       
        (status, fav) = self.getFavorite(name)
        self.removeFavoriteFromSchedule(fav)
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.removeFavorite(name)
        self.saveScheduledRecordings(scheduledRecordings)

        return (TRUE, 'favorite removed')
       
    
    def clearFavorites(self):
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.clearFavorites()
        self.saveScheduledRecordings(scheduledRecordings)

        return (TRUE, 'favorites cleared')
    
    
    def getFavorites(self):
        return (TRUE, self.getScheduledRecordings().getFavorites())
    
    
    def getFavorite(self, name):
        (status, favs) = self.getFavorites()
    
        if favs.has_key(name):
            fav = favs[name] 
            return (TRUE, fav)
        else:
            return (FALSE, 'not a favorite')
    
    
    def adjustPriority(self, favname, mod=0):
        save = []
        mod = int(mod)
        (status, me) = getFavorite(favname)
        oldprio = int(me.priority)
        newprio = oldprio + mod
    
        log.debug('ap: mod=%s\n' % mod)
       
        sr = self.getScheduledRecordings()
        favs = sr.getFavorites().values()
    
        sys.stderr.write('adjusting prio of '+favname+'\n')
        for fav in favs:
            fav.priority = int(fav.priority)
    
            if fav.name == me.name:
                log.debug('MATCH')
                fav.priority = newprio
                log.debug('moved prio of %s: %s => %s\n' % (fav.name, oldprio, newprio))
                continue
            if mod < 0:
                if fav.priority < newprio or fav.priority > oldprio:
                    log.debug('fp: %s, old: %s, new: %s\n' % (fav.priority, oldprio, newprio))
                    log.debug('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority + 1
                log.debug('moved prio of %s: %s => %s\n' % (fav.name, fav.priority-1, fav.priority))
                
            if mod > 0:
                if fav.priority > newprio or fav.priority < oldprio:
                    log.debug('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority - 1
                log.debug('moved prio of %s: %s => %s\n' % (fav.name, fav.priority+1, fav.priority))
    
        sr.setFavoritesList(favs)
        self.saveScheduledRecordings(sr)

        return (TRUE, 'priorities adjusted')
    
    
    def isProgAFavorite(self, prog, favs=None):
        if not favs:
            (status, favs) = self.getFavorites()
    
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
                            return (TRUE, fav.name)
                        elif abs(int(fav.mod) - int(min_of_day)) <= 8:
                            return (TRUE, fav.name)
    
        # if we get this far prog is not a favorite
        return (FALSE, 'not a favorite')
    
    
    def removeFavoriteFromSchedule(self, fav):
        # TODO: make sure the program we remove is not
        #       covered by another favorite.
    
        tmp = {}
        tmp[fav.name] = fav
    
        scheduledRecordings = self.getScheduledRecordings()
        progs = scheduledRecordings.getProgramList()
        for prog in progs.values():
            (isFav, favorite) = self.isProgAFavorite(prog, tmp)
            if isFav:
                self.removeScheduledRecording(prog)

        return (TRUE, 'favorite unscheduled')
    
    
    def addFavoriteToSchedule(self, fav):
        global guide
        favs = {}
        favs[fav.name] = fav

        self.updateGuide()
    
        for ch in guide.chan_list:
            for prog in ch.programs:
                (isFav, favorite) = self.isProgAFavorite(prog, favs)
                if isFav:
                    prog.isFavorite = favorite
                    self.scheduleRecording(prog)

        return (TRUE, 'favorite scheduled')
    
    
    def updateFavoritesSchedule(self):
        #  TODO: do not re-add a prog to record if we have
        #        previously decided not to record it.

        global guide
    
        self.updateGuide()
    
        # First get the timeframe of the guide.
        last = 0
        for ch in guide.chan_list:
            for prog in ch.programs:
                if prog.start > last: last = prog.start
    
        scheduledRecordings = self.getScheduledRecordings()
    
        (status, favs) = self.getFavorites()

        if not len(favs):
            return (FALSE, 'there are no favorites to update')
       
    
        # Then remove all scheduled favorites in that timeframe to
        # make up for schedule changes.
        progs = scheduledRecordings.getProgramList()
        for prog in progs.values():
    
            # try:
            #     favorite = prog.isFavorite
            # except:
            #     favorite = FALSE
    
            # if prog.start <= last and favorite:
            (isFav, favorite) = self.isProgAFavorite(prog, favs)
            if prog.start <= last and isFav:
                self.removeScheduledRecording(prog)
    
        for ch in guide.chan_list:
            for prog in ch.programs:
                (isFav, favorite) = self.isProgAFavorite(prog, favs)
                if isFav:
                    prog.isFavorite = favorite
                    self.scheduleRecording(prog)

        return (TRUE, 'favorites schedule updated')
    

    #################################################################
    #  Start XML-RPC published methods.                             #
    #################################################################

    def xmlrpc_getScheduledRecordings(self):
        return (TRUE, marmalade.jellyToXML(self.getScheduledRecordings()))


    def xmlrpc_saveScheduledRecordings(self, scheduledRecordings=None):
        status = self.saveScheduledRecordings(scheduledRecordings)

        if status:
            return (status, 'saveScheduledRecordings::success')
        else:
            return (status, 'saveScheduledRecordings::failure')


    def xmlrpc_scheduleRecording(self, prog=None):
        if not prog:
            return (FALSE, 'RecordServer::scheduleRecording:  no prog')

        prog = marmalade.unjellyFromXML(prog)

        (status, response) = self.scheduleRecording(prog)

        return (status, 'RecordServer::scheduleRecording: %s' % response)


    def xmlrpc_removeScheduledRecording(self, prog=None):
        if not prog:
            return (FALSE, 'RecordServer::removeScheduledRecording:  no prog')

        prog = marmalade.unjellyFromXML(prog)

        (status, response) = self.removeScheduledRecording(prog)

        return (status, 'RecordServer::removeScheduledRecording: %s' % response)


    def xmlrpc_isProgScheduled(self, prog=None, schedule=None):
        if not prog:
            return (FALSE, 'removeScheduledRecording::failure:  no prog')

        prog = marmalade.unjellyFromXML(prog)

        if schedule:
            schedule = marmalade.unjellyFromXML(schedule)

        (status, response) = self.isProgScheduled(prog, schedule)

        return (status, 'RecordServer::isProgScheduled: %s' % response)


    def xmlrpc_findProg(self, chan, start):
        (status, response) = self.findProg(chan, start)

        if status:
            return (status, marmalade.jellyToXML(response))
        else:
            return (status, 'RecordServer::findProg: %s' % response)


    def xmlrpc_findMatches(self, find):
        (status, response) = self.findMatches(find)

        if status:
            return (status, marmalade.jellyToXML(response))
        else:
            return (status, 'RecordServer::findMatches: %s' % response)


    def xmlrpc_echotest(self, blah):
        return (TRUE, 'RecordServer::echotest: %s' % blah)


    def xmlrpc_addFavorite(self, name, prog, exactchan=FALSE, exactdow=FALSE, exacttod=FALSE):
        prog = marmalade.unjellyFromXML(prog)
        (status, response) = self.addFavorite(name, prog, exactchan, exactdow, exacttod)

        return (status, 'RecordServer::addFavorite: %s' % response)


    def xmlrpc_addEditedFavorite(self, name, title, chan, dow, mod, priority):
        (status, response) = self.addEditedFavorite(name, title, chan, dow, mod, priority)

        return (status, 'RecordServer::addEditedFavorite: %s' % response)


    def xmlrpc_removeFavorite(self, name=None):
        (status, response) = self.removeFavorite(name)

        return (status, 'RecordServer::removeFavorite: %s' % response)


    def xmlrpc_clearFavorites(self):
        (status, response) = self.clearFavorites()

        return (status, 'RecordServer::clearFavorites: %s' % response)


    def xmlrpc_getFavorites(self):
        return (TRUE, marmalade.jellyToXML(self.getScheduledRecordings().getFavorites()))


    def xmlrpc_getFavorite(self, name):
        (status, response) = self.getFavorite(name)

        if status:
            return (status, marmalade.jellyToXML(response))
        else:
            return (status, 'RecordServer::getFavorite: %s' % response)


    def xmlrpc_adjustPriority(self, favname, mod=0):
        (status, response) = self.adjustPriority(favname, mod)

        return (status, 'RecordServer::adjustPriority: %s' % response)


    def xmlrpc_isProgAFavorite(self, prog, favs=None):
        prog = marmalade.unjellyFromXML(prog)
        if favs:
            favs = marmalade.unjellyFromXML(favs)

        (status, response) = self.isProgAFavorite(prog, favs)

        return (status, 'RecordServer::adjustPriority: %s' % response)


    def xmlrpc_removeFavoriteFromSchedule(self, fav):
        (status, response) = self.removeFavoriteFromSchedule(fav)

        return (status, 'RecordServer::removeFavoriteFromSchedule: %s' % response)


    def xmlrpc_addFavoriteToSchedule(self, fav):
        (status, response) = self.addFavoriteToSchedule(fav)

        return (status, 'RecordServer::addFavoriteToSchedule: %s' % response)


    def xmlrpc_updateFavoritesSchedule(self):
        (status, response) = self.updateFavoritesSchedule()

        return (status, 'RecordServer::updateFavoritesSchedule: %s' % response)


    #################################################################
    #  End XML-RPC published methods.                               #
    #################################################################


    def startMinuteCheck(self):
        next_minute = (int(time.time()/60) * 60 + 60) - int(time.time())
        log.debug('top of the minute in %s seconds' % next_minute)
        reactor.callLater(next_minute, self.minuteCheck)


    def minuteCheck(self):
        reactor.callLater(60, self.minuteCheck)
        rec_prog = self.checkToRecord()
        if rec_prog:
            self.record_app = plugin.getbyname('RECORD')
            self.record_app.Record(rec_prog)
            

def main():
    app = Application("RecordServer")
    rs = RecordServer()
    app.listenTCP(RECORD_SERVER_PORT, server.Site(rs))
    rs.startMinuteCheck()
    app.run(save=0)
    

if __name__ == '__main__':
    main()


