#!/usr/bin/env python

# Module for fetching information about an audio compact disc and
# returning it in a format friendly to CDDB.

# If called from the command line, will print out disc info in a
# format identical to Robert Woodcock's 'cd-discid' program.

# Written 17 Nov 1999 by Ben Gertzfield <che@debian.org>
# This work is released under the GNU GPL, version 2 or later.

# Release version 1.2
# CVS ID: $Id$

import cdrom, sys

def cddb_sum(n):
    ret = 0
    
    while n > 0:
	ret = ret + (n % 10)
	n = n / 10

    return ret

def disc_id(device):
    (first, last) = cdrom.toc_header(device)

    track_frames = []
    checksum = 0
    
    for i in range(first, last + 1):
	(min, sec, frame) = cdrom.toc_entry(device, i)
	checksum = checksum + cddb_sum(min*60 + sec)
	track_frames.append(min*60*75 + sec*75 + frame)

    (min, sec, frame) = cdrom.leadout(device)
    track_frames.append(min*60*75 + sec*75 + frame)

    total_time = (track_frames[-1] / 75) - (track_frames[0] / 75)
	       
    discid = ((checksum % 0xff) << 24 | total_time << 8 | last)

    return [discid, last] + track_frames[:-1] + [ track_frames[-1] / 75 ]

if __name__ == '__main__':
    import os                           # because Linux wants O_RDONLY
                                        # | O_NONBLOCK

    dev = '/dev/cdrom'			# This is just a sane default;
					# Solaris likes /vol/dev/aliases/cdrom0

    if len(sys.argv) >= 2:
	dev = sys.argv[1]

    # Thanks to John Watson for pointing out that Linux wants audio-CD-
    # using programs to open in O_RDONLY | O_NONBLOCK mode.

    fd = os.fdopen(os.open(dev, os.O_RDONLY | os.O_NONBLOCK))

    disc_info = disc_id(fd)

    print ('%08lx' % disc_info[0]),

    for i in disc_info[1:]:
	print ('%d' % i),
