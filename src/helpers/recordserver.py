#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.56  2004/07/11 13:54:33  dischi
# cache scheduledRecordings in memory
#
# Revision 1.55  2004/07/10 12:33:39  dischi
# header cleanup
#
# Revision 1.54  2004/07/09 21:05:46  rshortt
# Add warnings in case the recording plugin isn't there.
#
# Revision 1.53  2004/07/09 16:20:54  outlyer
# Remove the request logging for 0-level debug. Exceptions will still be
# logged, but standard requests will not.
#
# (i.e. this removes the Apache-style access logging for DEBUG = 0)
#
# Revision 1.52  2004/07/09 11:19:21  dischi
# fix unicode crash
#
# Revision 1.51  2004/07/09 02:28:53  outlyer
# If the automatic caching fails (as was happening for me) then just leave
# the png file in place for Freevo's OSD to pickle on access (rather than
# pre-pickled as before)
#
# If your system was caching the image properly before, then this shouldn't
# make any difference and the code probably won't even be called.
#
# Revision 1.50  2004/07/01 19:10:45  dischi
# add TV_RECORD_SERVER_GID
#
# Revision 1.49  2004/06/29 03:46:54  outlyer
# Hide some print statements. If these were supposed to go into debug, I can
# change that.
#
# Revision 1.48  2004/06/28 20:40:16  dischi
# make it possible to switch uid
#
# Revision 1.47  2004/06/23 21:20:10  dischi
# put snapshot in again with a try except
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


import sys, string, random, time, os, re, pwd, stat
import config
from util import vfs

# change uid
if __name__ == '__main__':
    try:
        if config.TV_RECORD_SERVER_UID and os.getuid() == 0:
            os.setgid(config.TV_RECORD_SERVER_GID)
            os.setuid(config.TV_RECORD_SERVER_UID)
            os.environ['USER'] = pwd.getpwuid(os.getuid())[0]
            os.environ['HOME'] = pwd.getpwuid(os.getuid())[5]
    except Exception, e:
        print e

from twisted.web import xmlrpc, server
from twisted.internet.app import Application
from twisted.internet import reactor
from twisted.python import log

from util.marmalade import jellyToXML, unjellyFromXML

import rc
rc_object = rc.get_singleton(use_pylirc=0, use_netremote=0)

from tv.record_types import TYPES_VERSION
from tv.record_types import ScheduledRecordings

import tv.record_types
import tv.epg_xmltv
import util.tv_util as tv_util
import plugin
import util.popen3
from   util.videothumb import snapshot


from event import *

def _debug_(text):
    if config.DEBUG:
        log.debug(String(text))
        
_debug_('PLUGIN_RECORD: %s' % config.plugin_record)

appname = os.path.splitext(os.path.basename(sys.argv[0]))[0]
logfile = '%s/%s-%s.log' % (config.LOGDIR, appname, os.getuid())
log.startLogging(open(logfile, 'a'))

plugin.init_special_plugin(config.plugin_record)

# XXX: In the future we should have one lock per VideoGroup.
tv_lock_file = config.FREEVO_CACHEDIR + '/record'


def print_plugin_warning():
    print '*************************************************'
    print '**  Warning: No recording plugin registered.  **'
    print '**           Check your local_conf.py for a   **'
    print '**           bad "plugin_record =" line or    **'
    print '**           this log for a plugin failure.   **'
    print '**           Recordings will fail!            **'
    print '*************************************************'


if not plugin.getbyname('RECORD'):
    print_plugin_warning()


class RecordServer(xmlrpc.XMLRPC):

    # note: add locking and r/rw options to get/save funs
    def getScheduledRecordings(self):
        file_ver = None
        scheduledRecordings = None

        if os.path.isfile(config.TV_RECORD_SCHEDULE):
            _debug_('GET: reading cached file (%s)' % config.TV_RECORD_SCHEDULE)
            if hasattr(self, 'scheduledRecordings_cache'):
                mod_time, scheduledRecordings = self.scheduledRecordings_cache
                try:
                    if os.stat(config.TV_RECORD_SCHEDULE)[stat.ST_MTIME] == mod_time:
                        _debug_('Return cached data')
                        return scheduledRecordings
                except OSError:
                    pass
                
            f = open(config.TV_RECORD_SCHEDULE, 'r')
            scheduledRecordings = unjellyFromXML(f)
            f.close()
            
            try:
                file_ver = scheduledRecordings.TYPES_VERSION
            except AttributeError:
                _debug_('The cache does not have a version and must be recreated.')
    
            if file_ver != TYPES_VERSION:
                _debug_(('ScheduledRecordings version number %s is stale (new is %s), must ' +
                        'be reloaded') % (file_ver, TYPES_VERSION))
                scheduledRecordings = None
            else:
                _debug_('Got ScheduledRecordings (version %s).' % file_ver)
    
        if not scheduledRecordings:
            _debug_('GET: making a new ScheduledRecordings')
            scheduledRecordings = ScheduledRecordings()
            self.saveScheduledRecordings(scheduledRecordings)
    
        _debug_('ScheduledRecordings has %s items.' % \
                len(scheduledRecordings.programList))
    
        try:
            mod_time = os.stat(config.TV_RECORD_SCHEDULE)[stat.ST_MTIME]
            self.scheduledRecordings_cache = mod_time, scheduledRecordings
        except OSError:
            pass
        return scheduledRecordings
    
    
    #
    # function to save the schedule to disk
    #
    def saveScheduledRecordings(self, scheduledRecordings=None):
    
        if not scheduledRecordings:
            _debug_('SAVE: making a new ScheduledRecordings')
            scheduledRecordings = ScheduledRecordings()
    
        _debug_('SAVE: saving cached file (%s)' % config.TV_RECORD_SCHEDULE)
        _debug_("SAVE: ScheduledRecordings has %s items." % \
                len(scheduledRecordings.programList))
        try:
            f = open(config.TV_RECORD_SCHEDULE, 'w')
        except IOError:
            os.unlink(config.TV_RECORD_SCHEDULE)
            f = open(config.TV_RECORD_SCHEDULE, 'w')
            
        jellyToXML(scheduledRecordings, f)
        f.close()

        try:
            mod_time = os.stat(config.TV_RECORD_SCHEDULE)[stat.ST_MTIME]
            self.scheduledRecordings_cache = mod_time, scheduledRecordings
        except OSError:
            pass

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
                _debug_('scheduleRecording: prog.channel_id="%s" chan.id="%s" chan.tunerid="%s"' % (prog.channel_id, chan.id, chan.tunerid))
                prog.tunerid = chan.tunerid
    
        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.addProgram(prog, tv_util.getKey(prog))
        self.saveScheduledRecordings(scheduledRecordings)

        # check, maybe we need to start right now
        self.checkToRecord()

        return (TRUE, 'recording scheduled')
    

    def removeScheduledRecording(self, prog=None):
        if not prog:
            return (FALSE, 'no prog')

        # get our version of 'prog'
        # It's a bad hack, but we can use isRecording than
        sr = self.getScheduledRecordings()
        progs = sr.getProgramList()

        for saved_prog in progs.values():
            if String(saved_prog) == String(prog):
                prog = saved_prog
                break
            
        try:
            recording = prog.isRecording
        except Exception, e:
            print e
            recording = FALSE

        scheduledRecordings = self.getScheduledRecordings()
        scheduledRecordings.removeProgram(prog, tv_util.getKey(prog))
        self.saveScheduledRecordings(scheduledRecordings)
        now = time.time()

        # if prog.start <= now and prog.stop >= now and recording:
        if recording:
            print 'stopping current recording'
            rec_plugin = plugin.getbyname('RECORD')
            if rec_plugin:
                rec_plugin.Stop()
       
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

        _debug_('findProg: %s, %s' % (chan, start))

        if not chan or not start:
            return (FALSE, 'no chan or no start')

        self.updateGuide()

        for ch in guide.chan_list:
            if chan == ch.id:
                _debug_('CHANNEL MATCH: %s' % ch.id)
                for prog in ch.programs:
                    if start == '%s' % prog.start:
                        _debug_('PROGRAM MATCH: %s' % prog.decode().title)
                        return (TRUE, prog.decode())

        return (FALSE, 'prog not found')


    def findMatches(self, find=None, movies_only=None):
        global guide

        _debug_('findMatches: %s' % find)
    
        matches = []
        max_results = 500

        if not find and not movies_only:
            _debug_('nothing to find')
            return (FALSE, 'no search string')

        self.updateGuide()

        pattern = '.*' + find + '\ *'
        regex = re.compile(pattern, re.IGNORECASE)
        now = time.time()

        for ch in guide.chan_list:
            for prog in ch.programs:
                if prog.stop < now:
                    continue
                if not find or regex.match(prog.title) or regex.match(prog.desc) \
                   or regex.match(prog.sub_title):
                    if movies_only:
                        # We can do better here than just look for the MPAA 
                        # rating.  Suggestions are welcome.
                        if 'MPAA' in prog.decode().getattr('ratings').keys():
                            matches.append(prog.decode())
                            _debug_('PROGRAM MATCH: %s' % prog.decode())
                    else:
                        # We should never get here if not find and not 
                        # movies_only.
                        matches.append(prog.decode())
                        _debug_('PROGRAM MATCH: %s' % prog.decode())
                if len(matches) >= max_results:
                    break

        _debug_('Found %d matches.' % len(matches))

        if matches:
            return (TRUE, matches)
        else:
            return (FALSE, 'no matches')


    def updateGuide(self):
        global guide

        # XXX TODO: only do this if the guide has changed?
        guide = tv.epg_xmltv.get_guide()

        
    def checkToRecord(self):
        _debug_('in checkToRecord')
        rec_cmd = None
        rec_prog = None
        cleaned = None
        delay_recording = FALSE
        total_padding = 0

        sr = self.getScheduledRecordings()
        progs = sr.getProgramList()

        currently_recording = None
        for prog in progs.values():
            try:
                recording = prog.isRecording
            except:
                recording = FALSE

            if recording:
                currently_recording = prog

        now = time.time()
        for prog in progs.values():
            _debug_('checkToRecord: progloop = %s' % String(prog))

            try:
                recording = prog.isRecording
            except:
                recording = FALSE

            if (prog.start - config.TV_RECORD_PADDING) <= now \
                   and (prog.stop + config.TV_RECORD_PADDING) >= now \
                   and recording == FALSE:
                # just add to the 'we want to record this' list
                # then end the loop, and figure out which has priority,
                # remember to take into account the full length of the shows
                # and how much they overlap, or chop one short
                duration = int((prog.stop + config.TV_RECORD_PADDING ) - now - 10)
                if duration < 10:
                    return 

                if currently_recording:
                    # Hey, something is already recording!
                    if prog.start - 10 <= now:
                        # our new recording should start no later than now!
                        sr.removeProgram(currently_recording, 
                                         tv_util.getKey(currently_recording))
                        plugin.getbyname('RECORD').Stop()
                        time.sleep(5)
                        _debug_('CALLED RECORD STOP 1')
                    else:
                        # at this moment we must be in the pre-record padding
                        if currently_recording.stop - 10 <= now:
                            # The only reason we are still recording is because of
                            # the post-record padding.
                            # Therefore we have overlapping paddings but not
                            # real stop / start times.
                            overlap = (currently_recording.stop + \
                                       config.TV_RECORD_PADDING) - \
                                      (prog.start - config.TV_RECORD_PADDING)
                            if overlap <= (config.TV_RECORD_PADDING/2):
                                sr.removeProgram(currently_recording, 
                                                 tv_util.getKey(currently_recording))
                                plugin.getbyname('RECORD').Stop()
                                time.sleep(5)
                                _debug_('CALLED RECORD STOP 2')
                            else: 
                                delay_recording = TRUE
                        else: 
                            delay_recording = TRUE
                             
                        
                if delay_recording:
                    _debug_('delaying: %s' % String(prog))
                else:
                    _debug_('going to record: %s' % String(prog))
                    prog.isRecording = TRUE
                    prog.rec_duration = duration
                    prog.filename = tv_util.getProgFilename(prog)
                    rec_prog = prog


        for prog in progs.values():
            # If the program is over remove the entry.
            if ( prog.stop + config.TV_RECORD_PADDING) < now:
                _debug_('found a program to clean')
                cleaned = TRUE
                del progs[tv_util.getKey(prog)]

        if rec_prog or cleaned:
            sr.setProgramList(progs)
            self.saveScheduledRecordings(sr)

        if rec_prog:
            _debug_('start recording')
            self.record_app = plugin.getbyname('RECORD')

            if not self.record_app:
                print_plugin_warning()
                print 'ERROR:  Recording %s failed.' % String(rec_prog.title)
                self.removeScheduledRecording(rec_prog)
                return

            self.record_app.Record(rec_prog)


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
        (status, me) = self.getFavorite(favname)
        oldprio = int(me.priority)
        newprio = oldprio + mod
    
        _debug_('ap: mod=%s\n' % mod)
       
        sr = self.getScheduledRecordings()
        favs = sr.getFavorites().values()
    
        sys.stderr.write('adjusting prio of '+favname+'\n')
        for fav in favs:
            fav.priority = int(fav.priority)
    
            if fav.name == me.name:
                _debug_('MATCH')
                fav.priority = newprio
                _debug_('moved prio of %s: %s => %s\n' % (fav.name, oldprio, newprio))
                continue
            if mod < 0:
                if fav.priority < newprio or fav.priority > oldprio:
                    _debug_('fp: %s, old: %s, new: %s\n' % (fav.priority, oldprio, newprio))
                    _debug_('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority + 1
                _debug_('moved prio of %s: %s => %s\n' % (fav.name, fav.priority-1, fav.priority))
                
            if mod > 0:
                if fav.priority > newprio or fav.priority < oldprio:
                    _debug_('skipping: %s\n' % fav.name)
                    continue
                fav.priority = fav.priority - 1
                _debug_('moved prio of %s: %s => %s\n' % (fav.name, fav.priority+1, fav.priority))
    
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
        return (TRUE, jellyToXML(self.getScheduledRecordings()))


    def xmlrpc_saveScheduledRecordings(self, scheduledRecordings=None):
        status = self.saveScheduledRecordings(scheduledRecordings)

        if status:
            return (status, 'saveScheduledRecordings::success')
        else:
            return (status, 'saveScheduledRecordings::failure')


    def xmlrpc_scheduleRecording(self, prog=None):
        if not prog:
            return (FALSE, 'RecordServer::scheduleRecording:  no prog')

        prog = unjellyFromXML(prog)

        (status, response) = self.scheduleRecording(prog)

        return (status, 'RecordServer::scheduleRecording: %s' % response)


    def xmlrpc_removeScheduledRecording(self, prog=None):
        if not prog:
            return (FALSE, 'RecordServer::removeScheduledRecording:  no prog')

        prog = unjellyFromXML(prog)

        (status, response) = self.removeScheduledRecording(prog)

        return (status, 'RecordServer::removeScheduledRecording: %s' % response)


    def xmlrpc_isProgScheduled(self, prog=None, schedule=None):
        if not prog:
            return (FALSE, 'removeScheduledRecording::failure:  no prog')

        prog = unjellyFromXML(prog)

        if schedule:
            schedule = unjellyFromXML(schedule)

        (status, response) = self.isProgScheduled(prog, schedule)

        return (status, 'RecordServer::isProgScheduled: %s' % response)


    def xmlrpc_findProg(self, chan, start):
        (status, response) = self.findProg(chan, start)

        if status:
            return (status, jellyToXML(response))
        else:
            return (status, 'RecordServer::findProg: %s' % response)


    def xmlrpc_findMatches(self, find, movies_only):
        (status, response) = self.findMatches(find, movies_only)

        if status:
            return (status, jellyToXML(response))
        else:
            return (status, 'RecordServer::findMatches: %s' % response)


    def xmlrpc_echotest(self, blah):
        return (TRUE, 'RecordServer::echotest: %s' % blah)


    def xmlrpc_addFavorite(self, name, prog, exactchan=FALSE, exactdow=FALSE, exacttod=FALSE):
        prog = unjellyFromXML(prog)
        (status, response) = self.addFavorite(name, prog, exactchan, exactdow, exacttod)

        return (status, 'RecordServer::addFavorite: %s' % response)


    def xmlrpc_addEditedFavorite(self, name, title, chan, dow, mod, priority):
        (status, response) = \
            self.addEditedFavorite(unjellyFromXML(name), \
            unjellyFromXML(title), chan, dow, mod, priority)

        return (status, 'RecordServer::addEditedFavorite: %s' % response)


    def xmlrpc_removeFavorite(self, name=None):
        (status, response) = self.removeFavorite(name)

        return (status, 'RecordServer::removeFavorite: %s' % response)


    def xmlrpc_clearFavorites(self):
        (status, response) = self.clearFavorites()

        return (status, 'RecordServer::clearFavorites: %s' % response)


    def xmlrpc_getFavorites(self):
        return (TRUE, jellyToXML(self.getScheduledRecordings().getFavorites()))


    def xmlrpc_getFavorite(self, name):
        (status, response) = self.getFavorite(name)

        if status:
            return (status, jellyToXML(response))
        else:
            return (status, 'RecordServer::getFavorite: %s' % response)


    def xmlrpc_adjustPriority(self, favname, mod=0):
        (status, response) = self.adjustPriority(favname, mod)

        return (status, 'RecordServer::adjustPriority: %s' % response)


    def xmlrpc_isProgAFavorite(self, prog, favs=None):
        prog = unjellyFromXML(prog)
        if favs:
            favs = unjellyFromXML(favs)

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


    def create_fxd(self, rec_prog):
        from util.fxdimdb import FxdImdb, makeVideo
        fxd = FxdImdb()

        (filebase, fileext) = os.path.splitext(rec_prog.filename)
        fxd.setFxdFile(filebase, overwrite = True)

        video = makeVideo('file', 'f1', os.path.basename(rec_prog.filename))
        fxd.setVideo(video)
        fxd.info['tagline'] = fxd.str2XML(rec_prog.sub_title)
        fxd.info['plot'] = fxd.str2XML(rec_prog.desc)
        fxd.info['runtime'] = None
        fxd.info['year'] = time.strftime('%m-%d ' + config.TV_TIMEFORMAT, 
                                         time.localtime(rec_prog.start))
        fxd.title = rec_prog.title 
        fxd.writeFxd()
            

    def startMinuteCheck(self):
        next_minute = (int(time.time()/60) * 60 + 60) - int(time.time())
        _debug_('top of the minute in %s seconds' % next_minute)
        reactor.callLater(next_minute, self.minuteCheck)
        
    def minuteCheck(self):
        next_minute = (int(time.time()/60) * 60 + 60) - int(time.time())
        if next_minute != 60:
            # Compensate for timer drift 
            if config.DEBUG:
                log.debug('top of the minute in %s seconds' % next_minute)
            reactor.callLater(next_minute, self.minuteCheck)
        else:
            reactor.callLater(60, self.minuteCheck)

        self.checkToRecord()


    def eventNotice(self):
        #print 'RECORDSERVER GOT EVENT NOTICE'
        # Use callLater so that handleEvents will get called the next time
        # through the main loop.
        reactor.callLater(0, self.handleEvents) 


    def handleEvents(self):
        #print 'RECORDSERVER HANDLING EVENT'
        event = rc_object.get_event()

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

            elif event == RECORD_START:
                #print 'Handling event RECORD_START'
                prog = event.arg
                open(tv_lock_file, 'w').close()
                self.create_fxd(prog)
                if config.VCR_PRE_REC:
                    util.popen3.Popen3(config.VCR_PRE_REC)

            elif event == RECORD_STOP:
                #print 'Handling event RECORD_STOP'
                os.remove(tv_lock_file)
                prog = event.arg
                try:
                    snapshot(prog.filename)
                except:
                    # If automatic pickling fails, use on-demand caching when
                    # the file is accessed instead. 
                    os.rename(vfs.getoverlay(prog.filename + '.raw.tmp'),
                              vfs.getoverlay(os.path.splitext(prog.filename)[0] + '.png'))
                    pass
                if config.VCR_POST_REC:
                    util.popen3.Popen3(config.VCR_POST_REC)

            else:
                print 'not handling event %s' % str(event)
                return
        else:
            print 'no event to get' 


def main():
    app = Application("RecordServer")
    rs = RecordServer()
    if (config.DEBUG == 0):
        app.listenTCP(config.TV_RECORD_SERVER_PORT, server.Site(rs, logPath='/dev/null'))
    else:
        app.listenTCP(config.TV_RECORD_SERVER_PORT, server.Site(rs))
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
            break
        except:
            traceback.print_exc()
            if start + 10 > time.time():
                print 'server problem, sleeping 1 min'
                time.sleep(60)

