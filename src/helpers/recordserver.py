#if 0 /*
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.17  2003/10/20 01:41:55  rshortt
# Moving tv_util from src/tv/ to src/util/.
#
# Revision 1.16  2003/10/19 16:15:52  rshortt
# Added OS_EVENT_KILL.  recordserver will now kill and wait.
#
# Revision 1.15  2003/10/19 14:19:44  rshortt
# Added OS_EVENT_WAITPID event for popen3.waitpid() to post so that recordserver
# can pick it up and wait on its own child.  Child processes from recordserver
# now get signals and clean up properly.
#
# Revision 1.14  2003/10/19 12:46:30  rshortt
# Calling popen from the main loop now but signals still aren't getting thgough.
#
# Revision 1.13  2003/10/18 21:33:33  rshortt
# Subscribe to events and poll them from a callback method.
#
# Revision 1.12  2003/10/18 08:33:36  dischi
# do not restart if the server crashed in 10 secs
#
# Revision 1.11  2003/10/15 12:49:53  rshortt
# Patch from Eirik Meland that stops recording when you remove a recording
# program from the recording schedule.  There exists a race condition where
# removing a recording right before it starts recording the entry in the
# schedule will go away but recording will start anyways.  We should figure
# out a good way to eliminate this.
#
# A similar method should be created for the generic_record.py plugin.
#
# Revision 1.10  2003/10/13 12:49:46  rshortt
# Fixed a bad return in findMatches when there was no search string.
#
# Revision 1.9  2003/09/18 00:36:06  mikeruelle
# need to import config before any other freevo module
#
# Revision 1.8  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.7  2003/09/11 21:24:04  outlyer
# Move most of the verbose logging into "DEBUG" since logs were growing at
# a drastic rate ( > 250k per hour)
#
# Revision 1.6  2003/09/08 19:58:21  dischi
# run servers in endless loop in case of a crash
#
# Revision 1.5  2003/09/06 15:12:53  rshortt
# Now using plugin.init_special_plugin() to load the recording plugin.
#
# Revision 1.4  2003/09/05 20:27:18  rshortt
# Changing the filename again for consistencies sake.
#
# Revision 1.1  2003/09/05 15:03:28  mikeruelle
# welcome to your new home
#
# Revision 1.3  2003/09/05 02:48:12  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.2  2003/08/23 12:51:41  dischi
# removed some old CVS log messages
#
# Revision 1.1  2003/08/13 13:08:36  rshortt
# Moving record_server.py into the main src directory to resolve some nasty
# namespace issues that was preventing it from import needed modules, use
# the plugin system, and in some cases find a way to create an osd singleton
# and init the display (bad!).
#
# Revision 1.11  2003/08/11 18:07:09  rshortt
# Use config.LOGDIR.
#
# Revision 1.10  2003/08/11 18:01:24  rshortt
# Further integration of record_server.  Moved config items and plugin info
# into freevo_config.py.  Also in freevo_config.py I moved FREEVO_CACHEDIR
# higher up in the file so more things can use it.
#
# Revision 1.9  2003/07/13 18:08:52  rshortt
# Change tv_util.get_chan_displayname() to accept channel_id instead of
# a TvProgram object and also use config.TV_CHANNELS when available, which
# is 99% of the time.
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

import config #config must always be the first freeevo module imported

import rc
rc_object = rc.get_singleton(use_pylirc=0, use_netremote=0)

from tv.record_types import TYPES_VERSION
from tv.record_types import ScheduledRecordings

import tv.record_types
import tv.epg_xmltv
import util.tv_util as tv_util
import plugin
import util.popen3

from event import *

# We won't be needing LD_PRELOAD.
os.environ['LD_PRELOAD'] = ''

DEBUG = config.DEBUG

if DEBUG: print 'PLUGIN_RECORD: %s' % config.plugin_record

appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logfile = '%s/%s-%s.log' % (config.LOGDIR, appname, os.getuid())
log.startLogging(open(logfile, 'a'))

plugin.init_special_plugin(config.plugin_record)


class RecordServer(xmlrpc.XMLRPC):

    # note: add locking and r/rw options to get/save funs
    def getScheduledRecordings(self):
        file_ver = None
        scheduledRecordings = None

        if os.path.isfile(config.RECORD_SCHEDULE):
            if DEBUG: log.debug('GET: reading cached file (%s)' % config.RECORD_SCHEDULE)
            scheduledRecordings = marmalade.unjellyFromXML(open(config.RECORD_SCHEDULE, 'r'))
    
            try:
                file_ver = scheduledRecordings.TYPES_VERSION
            except AttributeError:
                log.debug('The cache does not have a version and must be recreated.')
    
            if file_ver != TYPES_VERSION:
                log.debug(('ScheduledRecordings version number %s is stale (new is %s), must ' +
                        'be reloaded') % (file_ver, TYPES_VERSION))
                scheduledRecordings = None
            else:
                if DEBUG:
                    log.debug('Got ScheduledRecordings (version %s).' % file_ver)
    
        if not scheduledRecordings:
            if DEBUG: log.debug('GET: making a new ScheduledRecordings')
            scheduledRecordings = ScheduledRecordings()
            self.saveScheduledRecordings(scheduledRecordings)
    
        if DEBUG: log.debug('ScheduledRecordings has %s items.' % len(scheduledRecordings.programList))
    
        return scheduledRecordings
    
    
    #
    # function to save the schedule to disk
    #
    def saveScheduledRecordings(self, scheduledRecordings=None):
    
        if not scheduledRecordings:
            if DEBUG: print 'SAVE: making a new ScheduledRecordings'
            scheduledRecordings = ScheduledRecordings()
    
        if DEBUG: log.debug('SAVE: saving cached file (%s)' % config.RECORD_SCHEDULE)
        if DEBUG: log.debug("SAVE: ScheduledRecordings has %s items." % len(scheduledRecordings.programList))
        marmalade.jellyToXML(scheduledRecordings, open(config.RECORD_SCHEDULE, 'w'))
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
                if DEBUG: log.debug('scheduleRecording: prog.channel_id="%s" chan.id="%s" chan.tunerid="%s"' % (prog.channel_id, chan.id, chan.tunerid))
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
        now = time.time()
        try:
            recording = prog.isRecording
        except:
            recording = FALSE

        if prog.start <= now and prog.stop >= now and recording:
            plugin.getbyname('RECORD').Stop()
       
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

        if DEBUG: log.debug('findProg: %s, %s' % (chan, start))

        if not chan or not start:
            return (FALSE, 'no chan or no start')

        self.updateGuide()

        for ch in guide.chan_list:
            if chan == ch.id:
                if DEBUG: log.debug('CHANNEL MATCH')
                for prog in ch.programs:
                    if start == '%s' % prog.start:
                        if DEBUG: log.debug('PROGRAM MATCH')
                        return (TRUE, prog)

        return (FALSE, 'prog not found')


    def findMatches(self, find=None):
        global guide

        if DEBUG: log.debug('findMatches: %s' % find)
    
        matches = []

        if not find:
            if DEBUG: log.debug('nothing to find')
            return (FALSE, 'no search string')

        self.updateGuide()

        pattern = '.*' + find + '\ *'
        regex = re.compile(pattern, re.IGNORECASE)
        now = time.time()

        for ch in guide.chan_list:
            for prog in ch.programs:
                if prog.stop < now:
                    continue
                if regex.match(prog.title) or regex.match(prog.desc):
                    if DEBUG: log.debug('PROGRAM MATCH: %s' % prog)
                    matches.append(prog)

        if matches:
            return (TRUE, matches)
        else:
            return (FALSE, 'no matches')


    def updateGuide(self):
        global guide

        # XXX TODO: only do this if the guide has changed?
        guide = tv.epg_xmltv.get_guide()

        
    def checkToRecord(self):
        if DEBUG: log.debug('in checkToRecord')
        rec_cmd = None
        rec_prog = None
        cleaned = None
        scheduledRecordings = self.getScheduledRecordings()

        progs = scheduledRecordings.getProgramList()

        now = time.time()
        for prog in progs.values():
            if DEBUG: log.debug('checkToRecord: progloop = %s' % prog)

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

                if DEBUG: log.debug('going to record: %s' % prog)
                prog.isRecording = TRUE
                prog.rec_duration = duration
                prog.filename = tv_util.getProgFilename(prog)
                rec_prog = prog


        for prog in progs.values():
            # If the program is over remove the entry.
            if prog.stop < now:
                if DEBUG: log.debug('found a program to clean')
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
        fav = tv.record_types.Favorite(name, prog, exactchan, exactdow, exacttod, priority)
    
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.addFavorite(fav)
        self.saveScheduledRecordings(scheduledRecordings)
        self.addFavoriteToSchedule(fav)

        return (TRUE, 'favorite added')
    
    
    def addEditedFavorite(self, name, title, chan, dow, mod, priority):
        fav = tv.record_types.Favorite()
    
        fav.name = name
        fav.title = title
        fav.channel = chan
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
    
        if DEBUG: log.debug('ap: mod=%s\n' % mod)
       
        sr = self.getScheduledRecordings()
        favs = sr.getFavorites().values()
    
        sys.stderr.write('adjusting prio of '+favname+'\n')
        for fav in favs:
            fav.priority = int(fav.priority)
    
            if fav.name == me.name:
                if DEBUG: log.debug('MATCH')
                fav.priority = newprio
                log.debug('moved prio of %s: %s => %s\n' % (fav.name, oldprio, newprio))
                continue
            if mod < 0:
                if fav.priority < newprio or fav.priority > oldprio:
                    if DEBUG:
                        log.debug('fp: %s, old: %s, new: %s\n' % (fav.priority, oldprio, newprio))
                        log.debug('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority + 1
                if DEBUG: log.debug('moved prio of %s: %s => %s\n' % (fav.name, fav.priority-1, fav.priority))
                
            if mod > 0:
                if fav.priority > newprio or fav.priority < oldprio:
                    if DEBUG: log.debug('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority - 1
                if DEBUG: log.debug('moved prio of %s: %s => %s\n' % (fav.name, fav.priority+1, fav.priority))
    
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
                if fav.channel == tv_util.get_chan_displayname(prog.channel_id) \
                   or fav.channel == 'ANY':
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
        if DEBUG: log.debug('top of the minute in %s seconds' % next_minute)
        reactor.callLater(next_minute, self.minuteCheck)


    def minuteCheck(self):
        reactor.callLater(60, self.minuteCheck)
        rec_prog = self.checkToRecord()
        if rec_prog:
            self.record_app = plugin.getbyname('RECORD')
            self.record_app.Record(rec_prog)
            

    def eventNotice(self):
        print 'RECORDSERVER GOT EVENT NOTICE'

        # Use callLater so that handleEvents will get called the next time
        # through the main loop.
        reactor.callLater(0, self.handleEvents) 


    def handleEvents(self):
        print 'RECORDSERVER HANDLING EVENT'

        event, event_repeat_count = rc_object.poll()

        if event:
            if event == OS_EVENT_POPEN2:
                print 'popen %s' % event.arg[1]
                event.arg[0].child = util.popen3.Popen3(event.arg[1])

            elif event == OS_EVENT_WAITPID:
                pid = event.arg[0]
                print 'waiting on pid %s' % pid

                for i in range(20):
                    try:
                        wpid = os.waitpid(pid, os.WNOHANG)[0]
                    except OSError:
                        # forget it
                        continue
                    if wpid == pid:
                        break
                    time.sleep(0.1)

            elif event == OS_EVENT_KILL:
                pid = event.arg[0]
                sig = event.arg[1]

                print 'killing pid %s with sig %s' % (pid, sig)
                try:
                    os.kill(pid, sig)
                except OSError:
                    pass

                for i in range(20):
                    try:
                        wpid = os.waitpid(pid, os.WNOHANG)[0]
                    except OSError:
                        # forget it
                        continue
                    if wpid == pid:
                        break
                    time.sleep(0.1)
                else:
                    print 'force killing with signal 9'
                    try:
                        os.kill(pid, 9)
                    except OSError:
                        pass
                    for i in range(20):
                        try:
                            wpid = os.waitpid(pid, os.WNOHANG)[0]
                        except OSError:
                            # forget it
                            continue
                        if wpid == pid:
                            break
                        time.sleep(0.1)
                print 'recorderver: After wait()'
            else:
                print 'not handling event %s' % str(event)
                return
        else:
            print 'no event to get' 


def main():
    app = Application("RecordServer")
    rs = RecordServer()
    app.listenTCP(config.RECORD_SERVER_PORT, server.Site(rs))
    rs.startMinuteCheck()
    rc_object.subscribe(rs.eventNotice)
    app.run(save=0)
    

if __name__ == '__main__':
    import traceback
    import time
    while 1:
        try:
            start = time.time()
            main()
        except:
            traceback.print_exc()
            if start + 10 > time.time():
                print 'server problem, sleeping 1 min'
                time.sleep(60)

