__all__ = [ 'resolve' ]

import recorder
import notifier

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
        if self.rec[-1].status == 'recording':
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
        if scan(self.rec):
            # conflict not possible
            # FIXME: maybe ok
            return False
        return True
    
        
def scan(recordings):
    """
    Scan the schedule for conflicts. A conflict is a list of recordings
    with overlapping times.
    """
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

    return conflicts


def rate(devices, best_rating):
    rating = 0
    for d in devices[:-1]:
        for r in d.rec:
            rating += r.priority * d.rating
    if rating > best_rating:
        # remember
        best_rating = rating

        for d in devices[:-1]:
            # print d.id
            for r in d.rec:
                r.status   = 'scheduled'
                r.recorder = d.plugin, d.id
                # print ' ', r
        for r in devices[-1].rec:
            r.status   = 'conflict'
            r.recorder = None, None
    return best_rating


def check(devices, fixed, to_check, best_rating):
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

def resolve(recordings):
    # sort by start time
    recordings.sort(lambda l, o: cmp(l.start,o.start))

    # make sure to call notifier.step from time to time
    global call_notifier
    call_notifier = 0

    conflicts = scan(recordings)
    if conflicts:
        # create 'devices'
        devices = [ Device() ]
        for p in recorder.plugins:
            for d in p.get_channel_list():
                devices.append(Device(([ p, ] + d)))
        devices.sort(lambda l, o: cmp(o.rating,l.rating))

        for c in conflicts:
            print 'found conflict:'
            for r in c:
                print ' ', str(r)[:str(r).rfind(' ')]
            check(devices, [], c, 0)
            print 'solved by setting'
            for r in c:
                print ' ', r
            print
    return True
