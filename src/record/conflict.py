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

# notifier
import notifier

# objectcache
from util.objectcache import ObjectCache

# record imports
import recorder
from types import *

# get logging object
log = logging.getLogger('conflict')

# global variable to keep the notifier alive
call_notifier = 0

class Device:
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
        if self.rec[-1].status == RECORDING:
            # the recording is running right now, do not move it to
            # a new plugin
            if self.rec[-1].recorder[0] == self.plugin:
                # same recorder, everything ok
                return True
            else:
                # not possible to use this recorder
                return False
        if not self.plugin:
            # dummy recorder, it is always possible not record it
            return True
        if not self.rec[-1].channel in self.all_channels:
            # channel not supported
            return False
        if scan(self.rec, False):
            # conflict not possible
            # FIXME: maybe ok
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
        # overlapping padding gives minus points
        rating += rate_conflict(scan(d.rec, True)) - \
                  rate_conflict(scan(d.rec, False))


    if not devices[-1].rec:
        info = 'possible solution:\n'
        for d in devices[:-1]:
            info += 'device %s\n' % d.id
            for r in d.rec:
                info += '%s\n' % str(r)[:str(r).rfind(' ')]
        info += 'rating: %d\n' % rating
        log.debug(info)
    if rating > best_rating:
        # remember
        best_rating = rating

        for d in devices[:-1]:
            for r in d.rec:
                if r.status != RECORDING:
                    r.status = SCHEDULED
                    r.recorder = d.plugin, d.id
        for r in devices[-1].rec:
            r.status   = CONFLICT
            r.recorder = None, None
    return best_rating


def check(devices, fixed, to_check, best_rating):
    """
    Check all possible combinations from the recordings in to_check on all
    devives. Call recursive again.
    """
    if not to_check:
        return rate(devices, best_rating)

    global call_notifier
    call_notifier = (call_notifier + 1) % 1000
    if not call_notifier:
        notifier.step(False, False)

    c = to_check[0]
    for d in devices:
        d.rec.append(c)
        if d.is_possible():
            best_rating = check(devices, fixed + [ c ], to_check[1:],
                                best_rating)
        d.rec.remove(c)
    return best_rating


# interface

_conflict_cache = ObjectCache(30, 'conflict')

def resolve(recordings):
    """
    Find and resolve conflicts in recordings.
    """
    # sort by start time
    recordings.sort(lambda l, o: cmp(l.start,o.start))

    # make sure to call notifier.step from time to time
    global call_notifier
    call_notifier = 0

    conflicts = scan(recordings, True)
    if conflicts:
        # create 'devices'
        devices = [ Device() ]
        for p in recorder.plugins:
            for d in p.get_channel_list():
                devices.append(Device(([ p, ] + d)))
        devices.sort(lambda l, o: cmp(o.rating,l.rating))

        for c in conflicts:
            info = 'found conflict:\n'
            conflict_id = ''
            for r in c:
                info += '%s\n' % str(r)[:str(r).rfind(' ')]
                conflict_id += str(r)
            result = _conflict_cache[conflict_id]
            if result:
                log.info('use cache for conflict resolving')
                for r in c:
                    r.status, r.recorder = result[r.id]
                continue
            log.info(info)
            check(devices, [], c, 0)
            result = {}
            for r in c:
                result[r.id] = (r.status, r.recorder)
            info ='solved by setting:\n'
            for r in c:
                info += '%s\n' % str(r)
            log.info(info)
            # store cache result
            _conflict_cache[conflict_id] = result
    return True


def clear_cache():
    """
    Clear the global conflict resolve cache
    """
    global _conflict_cache
    _conflict_cache = ObjectCache(30, 'conflict')

