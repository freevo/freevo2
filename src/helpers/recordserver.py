#if 0 /*
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.41  2004/06/18 12:12:02  outlyer
# Patch from Brian J.Murrel to compensate for timer drift. It will do nothing
# if your system doesn't suffer from this problem, so it should be safe. Any
# problems, please let me know.
#
# Revision 1.40  2004/06/10 02:32:17  rshortt
# Add RECORD_START/STOP events along with VCR_PRE/POST_REC commands.
#
# Revision 1.39  2004/05/30 18:27:53  dischi
# More event / main loop cleanup. rc.py has a changed interface now
#
# Revision 1.38  2004/04/18 14:39:19  mikeruelle
# fix missing self, priorities still really don't do anything but at least it looks like its doing something.
#
# Revision 1.37  2004/04/18 08:23:44  dischi
# fix unicode problem
#
# Revision 1.36  2004/03/13 22:36:44  dischi
# fix crashes on debug (unicode again)
#
# Revision 1.35  2004/03/13 03:28:32  outlyer
# Someone must have fixed the str2XML part internal to the FxdIMDB code, since
# I was getting
# &amp&amp; (double-escaped) so I'm removing this one.
#
# Revision 1.34  2004/03/08 19:15:49  dischi
# use our marmalade
#
# Revision 1.33  2004/03/05 20:49:11  rshortt
# Add support for searching by movies only.  This uses the date field in xmltv
# which is what tv_imdb uses and is really acurate.  I added a date property
# to TvProgram for this and updated findMatches in the record_client and
# recordserver.
#
# Revision 1.32  2004/03/04 05:10:54  rshortt
# Make it work with rc.py changes.
#
# Revision 1.31  2004/02/23 21:46:22  dischi
# start some unicode fixes, still not working every time
#
# Revision 1.30  2004/02/11 04:20:46  outlyer
# Yet another place where we aren't following the user's time format... fixed now.
#
# Revision 1.29  2004/02/05 02:33:00  outlyer
# <sigh> Escape ALL the text that goes into the FXD file.
#
# Revision 1.28  2004/01/31 01:52:53  mikeruelle
# at least be able to set another extension manually until we can do this more properly
#
# Revision 1.27  2004/01/14 02:28:22  outlyer
# We do call videothumb in the recording plugins so this note isn't needed.
#
# Revision 1.26  2004/01/13 15:17:02  outlyer
# Appending won't work in this case anyway, so skip the error message.
#
# Revision 1.25  2004/01/09 18:57:06  dischi
# stop on normal exit
#
# Revision 1.24  2004/01/09 06:30:49  outlyer
# Two fixes:
#
# o the 'str2XML' function is a method of the FxdImdb() class, so call it as
#     part of the object
# o Don't say "Image downloading failed" since an image url isn't always
#     provided. If it actually is provided and fails, show the message.
#
# Revision 1.23  2004/01/09 05:09:12  outlyer
# I know that the str2XML call is supposed to happen in fxdimdb, but I kept
# running into this problem when trying to record a show with an '&' in the
# title. Adding the call here seems to fix it.
#
# Revision 1.22  2004/01/09 02:07:05  rshortt
# Marmalade name and title for favorites.  Thanks Matthieu Weber.
#
# Revision 1.21  2004/01/08 17:38:59  outlyer
# Write an FXD file with some of the XMLTV info for recorded programs. I just
# wrote this and it's fairly simple, but please make sure it works on your end.
# I plan to remove the hardcoded stuff ASAP, but I wanted to get it out there
# for people to try.
#
# Revision 1.20  2003/11/30 16:30:58  rshortt
# Convert some tv variables to new format (TV_).
#
# Revision 1.19  2003/11/30 13:07:27  rshortt
# Make the search function check the sub_title of the programs.
#
# Revision 1.18  2003/11/24 01:59:59  rshortt
# Adding support for the padding of recordings with X minutes before and
# after the show.  Thanks to Eirik Meland for the initial patch.
#
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
from twisted.python import log

import config #config must always be the first freeevo module imported
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

# We won't be needing LD_PRELOAD.
os.environ['LD_PRELOAD'] = ''

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


class RecordServer(xmlrpc.XMLRPC):

    # note: add locking and r/rw options to get/save funs
    def getScheduledRecordings(self):
        file_ver = None
        scheduledRecordings = None

        if os.path.isfile(config.TV_RECORD_SCHEDULE):
            _debug_('GET: reading cached file (%s)' % config.TV_RECORD_SCHEDULE)
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
        f = open(config.TV_RECORD_SCHEDULE, 'w')
        jellyToXML(scheduledRecordings, f)
        f.close()
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

        # if prog.start <= now and prog.stop >= now and recording:
        if recording:
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

        _debug_('findProg: %s, %s' % (chan, start))

        if not chan or not start:
            return (FALSE, 'no chan or no start')

        self.updateGuide()

        for ch in guide.chan_list:
            if chan == ch.id:
                _debug_('CHANNEL MATCH')
                for prog in ch.programs:
                    if start == '%s' % prog.start:
                        _debug_('PROGRAM MATCH')
                        return (TRUE, prog.decode())

        return (FALSE, 'prog not found')


    def findMatches(self, find=None, movies_only=None):
        global guide

        _debug_('findMatches: %s' % find)
    
        matches = []

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
                    _debug_('PROGRAM MATCH: %s' % prog.decode())
                    if movies_only:
                        if hasattr(prog, 'date') and prog.date:
                            matches.append(prog.decode())
                    else:
                        # We should never get here if not find and not 
                        # movies_only.
                        matches.append(prog.decode())

        _debug_('return: %s' % str(matches))

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
                    return FALSE

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
            if DEBUG: log.debug('top of the minute in %s seconds' % next_minute)
            reactor.callLater(next_minute, self.minuteCheck)
        else:
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
                print 'Handling event RECORD_START'
                prog = event.arg
                open(tv_lock_file, 'w').close()
                self.create_fxd(prog)
                if config.VCR_PRE_REC:
                    util.popen3.Popen3(config.VCR_PRE_REC)

            elif event == RECORD_STOP:
                print 'Handling event RECORD_STOP'
                os.remove(tv_lock_file)
                prog = event.arg
                snapshot(prog.filename)
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

