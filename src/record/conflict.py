# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# conflict.py - resolve conflicts for the recordserver
# -----------------------------------------------------------------------------
# $Id$
#
# This module resolves conflicts by choosing cards for the different recordings
# to record as much as possible with the best combination.
#
# Recordings have priorities between 40 and 100 if the are low priority and
# around 500 for medium and between 1000 and 1100 for high priority
# recordings.
# As a default favorites get a priority of 50, manual records of 1000 to make
# sure they always win. Important favorites can be adjusted in the priority.
#
# Cards have a quality between 1 (poor) and 10 (best). The module will try
# to make sure the best card is used for the highest rated recording.
#
# A conflict only in start and stop padding gives minus points based on the
# number of involved programs and the rating of them.
#
# Algorithm:
# sum up recording prio * (devices priority * 0.1 + 1)
# meaning the devices have a priority between 1.1 and 2
# After that reduce the rating with the rating of the overlapping
# (see function rate_conflict for documentation)
#
# Note: The algorithm isn't perfect. In fact, it can't be perfect because
# people have a different oppinion what is the correct way to resolve the
# conflict. Maybe it should also contain the number of seconds in a recording.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------


__all__ = [ 'resolve', 'clear_cache' ]

# python imports
import logging
import time

# objectcache
from util.objectcache import ObjectCache

# record imports
import recorder
from record_types import *

# get logging object
log = logging.getLogger('conflict')


class Device(object):
    def __init__(self, information=None):
        self.plugin       = None
        self.id           = 'null'
        self.rating       = 0
        self.listing      = []
        self.all_channels = []
        self.rec          = []
        if information:
            self.plugin, self.id, self.rating, self.listing = information
            for l in self.listing:
                for c in l:
                    if not c in self.all_channels:
                        self.all_channels.append(c)


    def is_possible(self):
        latest = self.rec[-1]
        latest.conflict_padding = []
        if latest.status == RECORDING:
            # the recording is running right now, do not move it to
            # a new plugin
            if latest.recorder[0] == self.plugin:
                # same recorder, everything ok
                return True
            else:
                # not possible to use this recorder
                return False
        if not self.plugin:
            # dummy recorder, it is always possible not record it
            return True
        if not latest.channel in self.all_channels:
            # channel not supported
            return False
        conflict = scan(self.rec, True)
        if not conflict:
            # possible without conflict
            return True
        # we now know that it is a conflict, maybe removing the padding
        # helps to solve it. The conflict list only contains one item (!)
        # Note: the recordings are sorted by time
        conflict = conflict[0]
        for c in conflict:
            if c == latest:
                continue
            if c.stop + c.stop_padding < latest.start - latest.start_padding:
                continue
            if c.stop <= latest.start:
                # works when removing padding
                latest.conflict_padding.append(c)
            else:
                # will never work
                return False
        return True


def scan(recordings, include_padding):
    """
    Scan the schedule for conflicts. A conflict is a list of recordings
    with overlapping times.
    """
    if include_padding:
        for r in recordings:
            r.start -= r.start_padding
            r.stop  += r.stop_padding
    # Sort by start time
    recordings.sort(lambda l, o: cmp(l.start,o.start))

    # all conflicts found
    conflicts = []

    # recordings already scanned
    scanned   = []

    # get current time
    ctime = time.time()
    
    # Check all recordings in the list for conflicts
    for r in recordings:
        if r in scanned:
            # Already marked as conflict
            continue
        current = []
        # Set stop time for the conflict area to current stop time. The
        # start time doesn't matter since the recordings are sorted by
        # start time and this is the first
        stop = r.stop
        while True:
            for c in recordings[recordings.index(r)+1:]:
                # Check all recordings after the current 'r' if the
                # conflict
                if c in scanned:
                    # Already marked as conflict
                    continue
                if c.start < stop:
                    # Found a conflict here. Mark the item as conflict and
                    # add to the current conflict list
                    current.append(c)
                    scanned.append(c)
                    # Get new stop time and repeat the scanning with it
                    # starting from 'r' + 1
                    stop = max(stop, c.stop)
                    break
            else:
                # No new conflicts found, the while True is done
                break
        if current:
            # Conflict found. Mark the current 'r' as conflict and
            # add it to the conflict list. 'current' will be reset to
            # [] for the next scanning to get groups of conflicts
            conflicts.append([ r ] + current)

    if include_padding:
        for r in recordings:
            r.start += r.start_padding
            r.stop  -= r.stop_padding
    return conflicts


def rate_conflict(clist):
    """
    Rate a conflict list created by 'scan'. Result is a negative value
    about the conflict lists.
    """
    number   = 0
    prio     = 0
    ret      = 0
    if not clist:
        return 0
    for c in clist:
        for pos, r1 in enumerate(c[:-1]):
          # check all pairs of conflicts (stop from x with start from x + 1)
          # next recording
          r2 = c[pos+1]
          # overlapping time in seconds
          time_diff = r1.stop + r1.stop_padding - r2.start - r2.start_padding
          # min priority of the both recordings
          min_prio = min(r1.priority, r2.priority)
          # average priority of the both recordings
          average_prio = (r1.priority + r2.priority) / 2

          # Algorithm for the overlapping rating detection:
          # min_prio / 2 (difference between 5 card types) +
          # average_prio / 100 (low priority in algorithm) +
          # number of overlapping minutes
          ret -= min_prio / 2 + average_prio / 100 + time_diff / 60
    return ret


def rate(devices, best_rating):
    """
    Rate device/recording settings. If the rating is better then best_rating,
    store the choosen recorder in the recording item.
    """
    rating = 0
    for d in devices[:-1]:
        for r in d.rec:
            rating += (0.1 * d.rating + 1) * r.priority
            if len(r.conflict_padding):
                rating += rate_conflict([[ r ] + r.conflict_padding])

    if rating > best_rating:
        # remember
        best_rating = rating

        for d in devices[:-1]:
            for r in d.rec:
                if r.status != RECORDING:
                    r.status = SCHEDULED
                    r.recorder = d.plugin, d.id
                    r.respect_start_padding = True
                    r.respect_stop_padding = True
                    if r.conflict_padding:
                        # the start_padding conflicts with the stop paddings
                        # the recordings in r.conflict_padding. Fix it by
                        # removing the padding
                        # FIXME: maybe start != stop
                        r.respect_start_padding = False
                        for c in r.conflict_padding:
                            c.respect_stop_padding = False
        for r in devices[-1].rec:
            r.status   = CONFLICT
            r.recorder = None, None
    return best_rating



def check(devices, fixed, to_check, best_rating, dropped=1000):
    """
    Check all possible combinations from the recordings in to_check on all
    devices. Call recursive again.
    """
    if not dropped and len(devices[-1].rec):
        # There was a solution without any recordings dropped.
        # It can't get better because devices[-1].rec already contains
        # at least one recording
        return best_rating, dropped

    if not to_check:
        return rate(devices, best_rating), len(devices[-1].rec)

    c = to_check[0]
    for d in devices:
        d.rec.append(c)
        if d.is_possible():
            best_rating, dropped = check(devices, fixed + [ c ], to_check[1:],
                                         best_rating, dropped)
        d.rec.remove(c)
    return best_rating, dropped


# internal cache
_conflict_cache = ObjectCache(30, 'conflict')

# list of devices
_devices          = []

def resolve(recordings):
    """
    Find and resolve conflicts in recordings.
    """
    t1 = time.time()
    if not _devices:
        # create 'devices'
        _devices.append(Device())
        for p in recorder.recorder:
            for d in p.get_channel_list():
                _devices.append(Device(([ p, ] + d)))
        _devices.sort(lambda l, o: cmp(o.rating,l.rating))

    # sort recordings
    recordings.sort(lambda l, o: cmp(l.start,o.start))

    # resolve recordings
    conflicts = scan(recordings, True)
    for c in conflicts:
        info = 'found conflict:\n'
        conflict_id = ''
        for r in c:
            info += '%s\n' % str(r)[:str(r).rfind(' ')]
            conflict_id += str(r)
        result = _conflict_cache[conflict_id]
        if result:
            for r in c:
                r.status, r.recorder = result[r.id]
            continue
        log.debug(info)
        check(_devices, [], c, 0)
        result = {}
        for r in c:
            result[r.id] = (r.status, r.recorder)
        info ='solved by setting:\n'
        for r in c:
            info += '%s\n' % str(r)
        log.debug(info)
        # store cache result
        _conflict_cache[conflict_id] = result
    t2 = time.time()
    log.info('resolve conflict took %s secs' % (t2-t1))


def clear_cache():
    """
    Clear the global conflict resolve cache
    """
    global _conflict_cache
    global _devices
    _conflict_cache = ObjectCache(30, 'conflict')
    _devices = []
