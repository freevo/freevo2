#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# record_server.py - A network aware TV recording server.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.11  2004/11/04 19:55:49  dischi
# make it possible to schedule recordings for testing
#
# Revision 1.10  2004/11/04 19:14:08  dischi
# add mbus parameter parsing
#
# Revision 1.9  2004/11/04 17:37:55  dischi
# update to new mcomm interface
#
# Revision 1.8  2004/11/02 20:15:50  dischi
# replace recordserver with mbus test code
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


import notifier

import sysconfig
import util.cache
import mcomm

VERSION = 1

class RecordServer(mcomm.RPCServer):
    def __init__(self):
        mcomm.RPCServer.__init__(self)
        self.cachefile = sysconfig.cachefile('recordserver.dump')
        self.load()
        

    def load(self):
        c = util.cache.load(self.cachefile, VERSION)
        print c
        if c:
            self.next_id, self.recordings = c
        else:
            self.recordings = {}
            self.next_id = 0

        print self.next_id
        print self.recordings


    def save(self):
        print (self.next_id, self.recordings)
        util.cache.save(self.cachefile, (self.next_id, self.recordings), VERSION)

        
    def __rpc_recording_list__(self, addr, val):
        self.parse_parameter(val, () )
        ret = []
        for id in self.recordings:
            name, channel, prio, start, stop, info = self.recordings[id]
            ret.append((id, channel, prio, start, stop))
        return mcomm.RPCReturn(ret)


    def __rpc_recording_add__(self, addr, val):
        name, channel, prio, start, stop, info = \
              self.parse_parameter(val, ( unicode, unicode, int, int, int, dict ) )
        print 'RecordRequest: %s' % String(name)
        self.recordings[self.next_id] = (name, channel, prio, start, stop, info)
        self.next_id += 1
        self.save()
        return mcomm.RPCReturn()

        
#     def saveScheduledRecordings(self, scheduledRecordings=None):
#         pass

 
#     def scheduleRecording(self, prog=None):
#         if not prog:
#             return mcomm.error('no program given')
    
#         if prog.stop < time.time():
#             return mcomm.error('cannot record it if it is over')
            
#         for chan in get_channels().get_all():
#             if prog.channel_id == chan.id:
#                 _debug_(('scheduleRecording: prog.channel_id="%s" chan.id="%s" ' +\
#                          'chan.epg.tunerid="%s"' % (prog.channel_id, chan.id,
#                                                     chan.epg.tunerid))
#                 prog.tunerid = chan.epg.tunerid
    
#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.addProgram(prog, tv_util.getKey(prog))
#         self.saveScheduledRecordings(scheduledRecordings)

#         # check, maybe we need to start right now
#         self.checkToRecord()

#         return (TRUE, 'recording scheduled')
    

#     def removeScheduledRecording(self, prog=None):
#         if not prog:
#             return (FALSE, 'no prog')

#         # get our version of 'prog'
#         # It's a bad hack, but we can use isRecording than
#         sr = self.getScheduledRecordings()
#         progs = sr.getProgramList()

#         for saved_prog in progs.values():
#             if String(saved_prog) == String(prog):
#                 prog = saved_prog
#                 break
            

#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.removeProgram(prog, tv_util.getKey(prog))
#         self.saveScheduledRecordings(scheduledRecordings)
#         now = time.time()

#         if prog in self.current_recordings.values():
#             _debug_('stopping current recording')
#             self.stop_record(prog)
       
#         return (TRUE, 'recording removed')
   

#     def isProgScheduled(self, prog, schedule=None):
    
#         if schedule == {}:
#             return (FALSE, 'prog not scheduled')

#         if not schedule:
#             schedule = self.getScheduledRecordings().getProgramList()

#         for me in schedule.values():
#             if me.start == prog.start and me.channel_id == prog.channel_id:
#                 return (TRUE, 'prog is scheduled')

#         return (FALSE, 'prog not scheduled')


#     def findProg(self, chan=None, start=None):
#         _debug_('findProg: %s, %s' % (chan, start))

#         if not chan or not start:
#             return (FALSE, 'no chan or no start')

#         for ch in get_channels().get_all():
#             if chan == ch.id:
#                 _debug_('CHANNEL MATCH: %s' % ch.id)
#                 for prog in ch.epg.programs:
#                     if start == '%s' % prog.start:
#                         _debug_('PROGRAM MATCH: %s' % prog.title)
#                         return (TRUE, prog)

#         return (FALSE, 'prog not found')


#     def findMatches(self, find=None, movies_only=None):
#         _debug_('findMatches: %s' % find)
    
#         matches = []
#         max_results = 500

#         if not find and not movies_only:
#             _debug_('nothing to find')
#             return (FALSE, 'no search string')

#         pattern = '.*' + find + '\ *'
#         regex = re.compile(pattern, re.IGNORECASE)
#         now = time.time()

#         for ch in get_channels().get_all():
#             for prog in ch.epg.programs:
#                 if prog.stop < now:
#                     continue
#                 if not find or regex.match(prog.title) or regex.match(prog.desc) \
#                    or regex.match(prog.sub_title):
#                     if movies_only:
#                         # We can do better here than just look for the MPAA 
#                         # rating.  Suggestions are welcome.
#                         if 'MPAA' in prog.getattr('ratings').keys():
#                             matches.append(prog)
#                             _debug_('PROGRAM MATCH: %s' % prog)
#                     else:
#                         # We should never get here if not find and not 
#                         # movies_only.
#                         matches.append(prog)
#                         _debug_('PROGRAM MATCH: %s' % prog)
#                 if len(matches) >= max_results:
#                     break

#         _debug_('Found %d matches.' % len(matches))

#         if matches:
#             return (TRUE, matches)
#         else:
#             return (FALSE, 'no matches')


#     def checkToRecord(self):
#         _debug_('in checkToRecord')
#         rec_cmd = None
#         rec_prog = None
#         cleaned = None
#         delay_recording = FALSE
#         total_padding = 0

#         sr = self.getScheduledRecordings()
#         progs = sr.getProgramList()

#         currently_recording = None
#         # for p in self.current_rcordings.values()
#         for prog in progs.values():
#             try:
#                 recording = prog.isRecording
#             except:
#                 recording = FALSE

#             if recording:
#                 currently_recording = prog

#         now = time.time()
#         for prog in progs.values():
#             _debug_('checkToRecord: progloop = %s' % String(prog))

#             try:
#                 recording = prog.isRecording
#             except:
#                 recording = FALSE

#             if (prog.start - config.TV_RECORD_PADDING) <= now \
#                    and (prog.stop + config.TV_RECORD_PADDING) >= now \
#                    and recording == FALSE:
#                 # just add to the 'we want to record this' list
#                 # then end the loop, and figure out which has priority,
#                 # remember to take into account the full length of the shows
#                 # and how much they overlap, or chop one short
#                 duration = int((prog.stop + config.TV_RECORD_PADDING ) - now - 10)
#                 if duration < 10:
#                     return 

#                 if currently_recording:
#                     # Hey, something is already recording!
#                     if prog.start - 10 <= now:
#                         # our new recording should start no later than now!
#                         sr.removeProgram(currently_recording, 
#                                          tv_util.getKey(currently_recording))
#                         self.stop_record(prog)

#                         # XXX:  Don't sleep (block) if we don't have to.
#                         #       Keep an eye on this.
#                         # time.sleep(5)

#                         _debug_('CALLED RECORD STOP 1')
#                     else:
#                         # at this moment we must be in the pre-record padding
#                         if currently_recording.stop - 10 <= now:
#                             # The only reason we are still recording is because of
#                             # the post-record padding.
#                             # Therefore we have overlapping paddings but not
#                             # real stop / start times.
#                             overlap = (currently_recording.stop + \
#                                        config.TV_RECORD_PADDING) - \
#                                       (prog.start - config.TV_RECORD_PADDING)
#                             if overlap <= (config.TV_RECORD_PADDING/2):
#                                 sr.removeProgram(currently_recording, 
#                                                  tv_util.getKey(currently_recording))
#                                 self.stop_record(prog)
#                                 # time.sleep(5)
#                                 _debug_('CALLED RECORD STOP 2')
#                             else: 
#                                 delay_recording = TRUE
#                         else: 
#                             delay_recording = TRUE
                             
                        
#                 if delay_recording:
#                     _debug_('delaying: %s' % String(prog))
#                 else:
#                     _debug_('going to record: %s' % String(prog))
#                     prog.isRecording = TRUE
#                     prog.rec_duration = duration
#                     prog.filename = tv_util.getProgFilename(prog)
#                     rec_prog = prog


#         for prog in progs.values():
#             # If the program is over remove the entry.
#             if ( prog.stop + config.TV_RECORD_PADDING) < now:
#                 _debug_('found a program to clean')
#                 cleaned = True
#                 del progs[tv_util.getKey(prog)]

#         if rec_prog or cleaned:
#             sr.setProgramList(progs)
#             self.saveScheduledRecordings(sr)

#         if rec_prog:
#             _debug_('start recording')
#             self.record_app = True

#             # XXX: make a good list of recordserver events, maybe use one to
#             #      notify if we aren't really recording something so we can
#             #      clear it from the schedule.

#             if not self.record_app:
#                 print_plugin_warning()
#                 print 'ERROR:  Recording %s failed.' % String(rec_prog.title)
#                 self.removeScheduledRecording(rec_prog)
#                 return

#             self.record(rec_prog)


#     def record(self, prog):
#         post_to = None
#         # expect types to be ordered by priority
#         types = get_settings_by_id(prog.channel_id)

#         for which in types:
#             if is_locked(which):
#                 _debug_('Cannot record on %s, it is busy.' % which)
#                 continue

#             else:
#                 post_to = which
#                 break

#         if post_to:
#             eh.post(Event('RECORD', arg=(prog, which)))
#         else:
#             # TODO: instead of removing it retry later.
#             self.removeScheduledRecording(prog)


#     def stop_record(self, prog):
#         for t, p in self.current_recordings.items():
#             if prog == p:
#                 eh.post(Event('STOP_RECORDING', arg=(p, t)))


#     def addFavorite(self, name, prog, exactchan=FALSE, exactdow=FALSE, exacttod=FALSE):
#         if not name:
#             return (FALSE, 'no name')
    
#         (status, favs) = self.getFavorites()
#         priority = len(favs) + 1
#         fav = tv.record_types.Favorite(name, prog, exactchan, exactdow, exacttod, priority)
    
#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.addFavorite(fav)
#         self.saveScheduledRecordings(scheduledRecordings)
#         self.addFavoriteToSchedule(fav)

#         return (TRUE, 'favorite added')
    
    
#     def addEditedFavorite(self, name, title, chan, dow, mod, priority):
#         fav = tv.record_types.Favorite()
    
#         fav.name = name
#         fav.title = title
#         fav.channel = chan
#         fav.dow = dow
#         fav.mod = mod
#         fav.priority = priority
    
#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.addFavorite(fav)
#         self.saveScheduledRecordings(scheduledRecordings)
#         self.addFavoriteToSchedule(fav)

#         return (TRUE, 'favorite added')
    
    
#     def removeFavorite(self, name=None):
#         if not name:
#             return (FALSE, 'no name')
       
#         (status, fav) = self.getFavorite(name)
#         self.removeFavoriteFromSchedule(fav)
#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.removeFavorite(name)
#         self.saveScheduledRecordings(scheduledRecordings)

#         return (TRUE, 'favorite removed')
       
    
#     def clearFavorites(self):
#         scheduledRecordings = self.getScheduledRecordings()
#         scheduledRecordings.clearFavorites()
#         self.saveScheduledRecordings(scheduledRecordings)

#         return (TRUE, 'favorites cleared')
    
    
#     def getFavorites(self):
#         return (TRUE, self.getScheduledRecordings().getFavorites())
    
    
#     def getFavorite(self, name):
#         (status, favs) = self.getFavorites()
    
#         if favs.has_key(name):
#             fav = favs[name] 
#             return (TRUE, fav)
#         else:
#             return (FALSE, 'not a favorite')
    
    
#     def adjustPriority(self, favname, mod=0):
#         save = []
#         mod = int(mod)
#         (status, me) = self.getFavorite(favname)
#         oldprio = int(me.priority)
#         newprio = oldprio + mod
    
#         _debug_('ap: mod=%s\n' % mod)
       
#         sr = self.getScheduledRecordings()
#         favs = sr.getFavorites().values()
    
#         sys.stderr.write('adjusting prio of '+favname+'\n')
#         for fav in favs:
#             fav.priority = int(fav.priority)
    
#             if fav.name == me.name:
#                 _debug_('MATCH')
#                 fav.priority = newprio
#                 _debug_('moved prio of %s: %s => %s\n' % (fav.name, oldprio, newprio))
#                 continue
#             if mod < 0:
#                 if fav.priority < newprio or fav.priority > oldprio:
#                     _debug_('fp: %s, old: %s, new: %s\n' % (fav.priority, oldprio, newprio))
#                     _debug_('skipping: %s\n' % fav.name)
#                     continue
#                 fav.priority = fav.priority + 1
#                 _debug_('moved prio of %s: %s => %s\n' % (fav.name, fav.priority-1, fav.priority))
                
#             if mod > 0:
#                 if fav.priority > newprio or fav.priority < oldprio:
#                     _debug_('skipping: %s\n' % fav.name)
#                     continue
#                 fav.priority = fav.priority - 1
#                 _debug_('moved prio of %s: %s => %s\n' % (fav.name, fav.priority+1, fav.priority))
    
#         sr.setFavoritesList(favs)
#         self.saveScheduledRecordings(sr)

#         return (TRUE, 'priorities adjusted')
    
    
#     def isProgAFavorite(self, prog, favs=None):
#         if not favs:
#             (status, favs) = self.getFavorites()
    
#         lt = time.localtime(prog.start)
#         dow = '%s' % lt[6]
#         # tod = '%s:%s' % (lt[3], lt[4])
#         # mins_in_day = 1440
#         min_of_day = '%s' % ((lt[3]*60)+lt[4])
    
#         for fav in favs.values():
    
#             if prog.title == fav.title:    
#                 if fav.channel == tv_util.get_chan_displayname(prog.channel_id) \
#                    or fav.channel == 'ANY':
#                     if fav.dow == dow or fav.dow == 'ANY':
#                         if fav.mod == min_of_day or fav.mod == 'ANY':
#                             return (TRUE, fav.name)
#                         elif abs(int(fav.mod) - int(min_of_day)) <= 8:
#                             return (TRUE, fav.name)
    
#         # if we get this far prog is not a favorite
#         return (FALSE, 'not a favorite')
    
    
#     def removeFavoriteFromSchedule(self, fav):
#         # TODO: make sure the program we remove is not
#         #       covered by another favorite.
    
#         tmp = {}
#         tmp[fav.name] = fav
    
#         scheduledRecordings = self.getScheduledRecordings()
#         progs = scheduledRecordings.getProgramList()
#         for prog in progs.values():
#             (isFav, favorite) = self.isProgAFavorite(prog, tmp)
#             if isFav:
#                 self.removeScheduledRecording(prog)

#         return (TRUE, 'favorite unscheduled')
    
    
#     def addFavoriteToSchedule(self, fav):
#         favs = {}
#         favs[fav.name] = fav

#         for ch in get_channels().get_all():
#             for prog in ch.epg.programs:
#                 (isFav, favorite) = self.isProgAFavorite(prog, favs)
#                 if isFav:
#                     prog.isFavorite = favorite
#                     self.scheduleRecording(prog)

#         return (TRUE, 'favorite scheduled')
    
    
#     def updateFavoritesSchedule(self):
#         #  TODO: do not re-add a prog to record if we have
#         #        previously decided not to record it.

#         # First get the timeframe of the guide.
#         last = 0
#         for ch in get_channels().get_all():
#             for prog in ch.epg.programs:
#                 if prog.start > last: last = prog.start
    
#         scheduledRecordings = self.getScheduledRecordings()
    
#         (status, favs) = self.getFavorites()

#         if not len(favs):
#             return (FALSE, 'there are no favorites to update')
       
    
#         # Then remove all scheduled favorites in that timeframe to
#         # make up for schedule changes.
#         progs = scheduledRecordings.getProgramList()
#         for prog in progs.values():
    
#             # try:
#             #     favorite = prog.isFavorite
#             # except:
#             #     favorite = FALSE
    
#             # if prog.start <= last and favorite:
#             (isFav, favorite) = self.isProgAFavorite(prog, favs)
#             now = time.time()
#             if prog.start <= last and isFav and \
#                not (prog.start <= now and prog.stop > now):
#                 self.removeScheduledRecording(prog)
    
#         for ch in get_channels().get_all():
#             for prog in ch.epg.programs:
#                 (isFav, favorite) = self.isProgAFavorite(prog, favs)
#                 if isFav:
#                     prog.isFavorite = favorite
#                     self.scheduleRecording(prog)

#         return (TRUE, 'favorites schedule updated')
#     #################################################################
#     #  End XML-RPC published methods.                               #
#     #################################################################


#     def create_fxd(self, rec_prog):
#         from util.fxdimdb import FxdImdb, makeVideo
#         fxd = FxdImdb()

#         (filebase, fileext) = os.path.splitext(rec_prog.filename)
#         fxd.setFxdFile(filebase, overwrite = True)

#         video = makeVideo('file', 'f1', os.path.basename(rec_prog.filename))
#         fxd.setVideo(video)
#         fxd.info['tagline'] = fxd.str2XML(rec_prog.sub_title)
#         fxd.info['plot'] = fxd.str2XML(rec_prog.desc)
#         fxd.info['runtime'] = None
#         fxd.info['recording_timestamp'] = str(time.time())
#         fxd.info['year'] = time.strftime('%m-%d ' + config.TV_TIMEFORMAT, 
#                                          time.localtime(rec_prog.start))
#         fxd.title = rec_prog.title 
#         fxd.writeFxd()
            

#     def startup(self):
#         self.startMinuteCheck()
#         self.startPlugins()
#         self.handleEvents()
            

#     def startMinuteCheck(self):
#         next_minute = (int(time.time()/60) * 60 + 60) - int(time.time())
#         _debug_('top of the minute in %s seconds' % next_minute)
#         reactor.callLater(next_minute, self.minuteCheck)
        

#     def minuteCheck(self):
#         next_minute = (int(time.time()/60) * 60 + 60) - int(time.time())
#         if next_minute != 60:
#             # Compensate for timer drift 
#             _debug_('top of the minute in %s seconds' % next_minute)
#             reactor.callLater(next_minute, self.minuteCheck)
#         else:
#             reactor.callLater(60, self.minuteCheck)

#         self.checkToRecord()


#     def poll_plugin(self, plugin):
#         # _debug_('polling %s' % plugin.plugin_name)
#         plugin.poll()
#         reactor.callLater(plugin.poll_interval*0.1, self.poll_plugin, plugin)


#     def startPlugins(self):
#         for p in plugin.get('daemon_poll'):
#             _debug_('found a poll plugin: %s' % p.plugin_name)
#             reactor.callLater(0.1, self.poll_plugin, p)


#     def handleEvents(self):

#         if not len(eh.queue):
#             # No event, check again really soon.
#             reactor.callLater(0.1, self.handleEvents) 
#             return

#         event = eh.queue[0]
#         del eh.queue[0]
#         # If we got an event then call this function in the next iteration
#         # of the main loop to exhaust the queue quickly without blocking as
#         # if we clear them all at the same time.
#         reactor.callLater(0, self.handleEvents) 

#         _debug_('handling event %s' % str(event))

#         #  XXX:  Here we're ripping off code from the 'freevo main' event loop.
#         #        I think eventhandler.handle() is made for freevo main and we
#         #        need something different (like below) for recordserver.
#         #        Freevo main plugins register callbacks that get called from
#         #        its MainLoop.  Again, recordserver is different and the old
#         #        style of poll()/plugin.eventhandler() works well here.
#         #        Comments welcome.

#         if eh.eventhandler_plugins == None:
#             import plugin
#             _debug_('init')
#             eh.eventhandler_plugins  = []
#             eh.eventlistener_plugins = []

#             for p in plugin.get('daemon_eventhandler'):
#                 if hasattr(p, 'event_listener') and p.event_listener:
#                     eh.eventlistener_plugins.append(p)
#                 else:
#                     eh.eventhandler_plugins.append(p)

#         for p in eh.eventlistener_plugins:
#             p.eventhandler(event=event)

#         if event == OS_EVENT_POPEN2:
#             # XXX TODO:  Test the Twisted process handling.

#             print 'popen %s' % event.arg[1]
#             event.arg[0].child = util.popen3.Popen3(event.arg[1])


#         # XXX TODO:  Change these for/sleep loops to be more non-blocking.
#         #            We could post another event or use reactor.callLater()
#         #            to call waitpid in a further itteration of the mail loop.

#         elif event == OS_EVENT_WAITPID:
#             pid = event.arg[0]
#             _debug_('waiting on pid %s' % pid)

#             for i in range(20):
#                 try:
#                     wpid = os.waitpid(pid, os.WNOHANG)[0]
#                 except OSError:
#                     # forget it
#                     continue
#                 if wpid == pid:
#                     break
#                 time.sleep(0.1)

#         elif event == OS_EVENT_KILL:
#             pid = event.arg[0]
#             sig = event.arg[1]

#             _debug_('killing pid %s with sig %s' % (pid, sig))
#             try:
#                 os.kill(pid, sig)
#             except OSError:
#                 pass

#             for i in range(20):
#                 try:
#                     wpid = os.waitpid(pid, os.WNOHANG)[0]
#                 except OSError:
#                     # forget it
#                     continue
#                 if wpid == pid:
#                     break
#                 time.sleep(0.1)

#             else:
#                 _debug_('force killing with signal 9')
#                 try:
#                     os.kill(pid, 9)
#                 except OSError:
#                     pass
#                 for i in range(20):
#                     try:
#                         wpid = os.waitpid(pid, os.WNOHANG)[0]
#                     except OSError:
#                         # forget it
#                         continue
#                     if wpid == pid:
#                         break
#                     time.sleep(0.1)
#             _debug_('recorderver: After wait()')

#         elif event == RECORD_START:
#             _debug_('Handling event RECORD_START')
#             prog = event.arg[0]
#             which = event.arg[1]

#             lock_device(which)
#             self.create_fxd(prog)

#             if config.VCR_PRE_REC:
#                 util.popen3.Popen3(config.VCR_PRE_REC)

#             self.current_recordings[which] = prog

#         elif event == RECORD_STOP:
#             _debug_('Handling event RECORD_STOP')
#             prog = event.arg[0]
#             which = event.arg[1]
#             unlock_device(which)
#             try:
#                 snapshot(prog.filename)
#             except:
#                 # If automatic pickling fails, use on-demand caching when
#                 # the file is accessed instead. 
#                 os.rename(vfs.getoverlay(prog.filename + '.raw.tmp'),
#                           vfs.getoverlay(os.path.splitext(prog.filename)[0] + '.png'))

#             if config.VCR_POST_REC:
#                 util.popen3.Popen3(config.VCR_POST_REC)

#             del self.current_recordings[which]

