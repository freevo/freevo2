#if 0 /*
# -----------------------------------------------------------------------
# rec_interface.py - An interface to the recording schedule.
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/01/29 05:29:34  krister
# Rob Shortts WWW server scripts for Freevo recording.
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
import epg_xmltv


# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0


#
#
# note: add locking and r/rw options to get/save funs
def getScheduledRecordings():
    file_ver = None
    scheduledRecordings = None

    if os.path.isfile(config.REC_SCHEDULE):
        print 'GET: reading cached file (%s)' % config.REC_SCHEDULE
        scheduledRecordings = pickle.load(open(config.REC_SCHEDULE, 'r'))

        try:
            file_ver = scheduledRecordings.TYPES_VERSION
        except AttributeError:
            print 'The cache does not have a version and must be recreated.'

        if file_ver != rec_types.TYPES_VERSION:
            print (('ScheduledRecordings version number %s is stale (new is %s), must ' +
                    'be reloaded') % (file_ver, rec_types.TYPES_VERSION))
        else:
            if DEBUG:
                print 'Got ScheduledRecordings (version %s).' % file_ver

    if scheduledRecordings == None:
        print 'GET: making a new ScheduledRecordings'
        scheduledRecordings = rec_types.ScheduledRecordings()

    print "ScheduledRecordings has %s items." % len(scheduledRecordings.programList)

    return scheduledRecordings


#
# function to save the schedule to disk
#
def saveScheduledRecordings(scheduledRecordings):

    if not scheduledRecordings or scheduledRecordings == None:
        print 'SAVE: making a new ScheduledRecordings'
        scheduledRecordings = rec_types.ScheduledRecordings()

    print 'SAVE: saving cached file (%s)' % config.REC_SCHEDULE
    print "SAVE: ScheduledRecordings has %s items." % len(scheduledRecordings.programList)
    pickle.dump(scheduledRecordings, open(config.REC_SCHEDULE, 'w'))
    

def getKey(prog=None):
    if not prog:
        return 'ERROR: no prog'

    return '%s:%s' % (prog.channel_id, prog.start)

  
def progRunning(prog=None):
    if not prog:
        return 'ERROR: no prog'

    now = time.time()
    if prog.start <= now and prog.stop >= now:
        return TRUE
    return FALSE


def scheduleRecording(prog=None):
    if not prog:
        print 'ERROR: no prog'
        return

    scheduledRecordings = getScheduledRecordings()
    scheduledRecordings.addProgram(prog, getKey(prog))
    saveScheduledRecordings(scheduledRecordings)


def removeScheduledRecording(prog=None):
    if not prog:
        print 'ERROR: no prog'
        return

    scheduledRecordings = getScheduledRecordings()
    scheduledRecordings.removeProgram(prog, getKey(prog))
    saveScheduledRecordings(scheduledRecordings)
   

def cleanScheduledRecordings():
    scheduledRecordings = getScheduledRecordings()

    progs = scheduledRecordings.getProgramList()

    # If the program is over remove the entry.
    now = time.time()
    for prog in progs.values():
        if prog.stop < now:
            del progs[getKey(prog)]

    scheduledRecordings.setProgramList(progs)
    saveScheduledRecordings(scheduledRecordings)


def findProg(chan=None, start=None):
    print 'findProg: %s, %s' % (chan, start)
    if not chan or not start:
        print 'no chan or no start'
        return None

    guide = epg_xmltv.get_guide()

    for ch in guide.chan_list:
        if chan == ch.id:
            print 'CHANNEL MATCH'
            for prog in ch.programs:
                if start == '%s' % prog.start:
                    print 'PROGRAM MATCH'
                    return prog


def findMatches(find=None):
    print 'findMatches: %s' % find

    matches = []

    if not find:
        print 'nothing to find'
        return []

    guide = epg_xmltv.get_guide()

    now = time.time()
    for ch in guide.chan_list:
        for prog in ch.programs:
            if prog.stop < now:
                continue
            if string.find(prog.title, find) != -1 or string.find(prog.desc, find) != -1:
                print 'PROGRAM MATCH: %s' % prog
                matches.append(prog)

    return matches


def checkToRecord():
    rec_cmd = None
    scheduledRecordings = getScheduledRecordings()

    progs = scheduledRecordings.getProgramList()

    now = time.time()
    for prog in progs.values():
        print 'checkToRecord: progloop = %s' % prog

        try:
            recording = prog.isRecording
        except:
            recording = FALSE

        if prog.start <= now and prog.stop >= now and recording == FALSE:
            duration = int(prog.stop - now)
            if duration < 10:
                return FALSE
            title = '%s--%s' % (prog.title, time.strftime('%Y-%m-%d-%H:%M', time.localtime(prog.start)))
            rec_cmd = '%s %s %s "%s"' % \
              (config.REC_CMD, string.split(prog.channel_id)[0], duration, title)
            print 'REC_CMD: %s' % rec_cmd
            prog.isRecording = TRUE

    scheduledRecordings.setProgramList(progs)
    saveScheduledRecordings(scheduledRecordings)
    return rec_cmd


def main():
    rec_cmd = checkToRecord()
    cleanScheduledRecordings()
    os.system(rec_cmd)


if __name__ == '__main__':
    main()
     

