# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# url_record.py - Freevo helper to record a stream from a URL to a file.
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Rob Shortt <rshortt@users.sourceforge.net>
# Maintainer:    Rob Shortt <rshortt@users.sourceforge.net>
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

import urllib
import time
import signal
import sys


CHUNKSIZE = 1024 * 128

data = None
save_file = None
URL = None
finished = False


def main():
    global data
    global save_file
    global URL
    global finished
    record_forever = False

    if len(sys.argv) < 3:
        print 'Usage: url_record <URL> <save file> <seconds to record>'
        print '       If <seconds to record> is ommitted it will record '
        print '       until interrupted.'
        sys.exit(0)

    URL = sys.argv[1]
    SAVE_FILE = sys.argv[2]
    try:
        LENGTH = int(sys.argv[3])
        stop = time.time() + LENGTH
    except:
        record_forever = True
        LENGTH = 'undetermined'

    data = urllib.urlopen(URL)

    save_file = open(SAVE_FILE, 'w')
    signal.signal(signal.SIGINT, finish)
    signal.signal(signal.SIGKILL, finish)
    signal.signal(signal.SIGSTOP, finish)
    signal.signal(signal.SIGTERM, finish)
    print 'Recording %s to %s for %s seconds.' % (URL, SAVE_FILE, LENGTH)


    try:
        while record_forever or time.time() < stop:
            buf = data.read(CHUNKSIZE)
            save_file.write(buf)
            save_file.flush()
    except:
        print 'recording interrupted'

    if not finished:
        finish(0)


def finish(signum=None, frame=None):
    global data
    global save_file
    global URL
    global finished

    print 'Finished recording %s with signal %s.' % (URL, signum)
    finished = True
    data.close()
    # save_file.flush()
    save_file.close()
    sys.exit(0)


if __name__ == '__main__':
    main()

