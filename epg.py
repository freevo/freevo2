#
# epg.py
#
# This is the Freevo Electronic Program Guide module. 
#

import sys
import time, os

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mpg123 application
import mpg123

# Set to 1 for debug output
DEBUG = 1

TRUE = 1
FALSE = 0

class Dummy:
    pass

cached_guide = None


#
# Check if there's a recently cached guide, if not get a newer one
#
def get_guide():
    global cached_guide

    cached_guide = download_guide()

    return cached_guide


def cmp_channel_nums(channelnum, program):
    if program[0] == channelnum:
        return 1
    else:
        return 0
    

def filter_guide(programs):
    all_channels = []
    for chan in config.TV_CHANNELS:
        f = lambda prog, c=int(chan): cmp_channel_nums(c, prog)
        chan_progs = filter(f, programs)

        if not chan_progs:
            all_channels += [[(int(chan), '???', '???', 0)]]
            continue
        
        tmp = []
        chan_progs.reverse()
        for p in chan_progs:
            tmp += [p]
            if p[3] <= time.time():
                break

        tmp.reverse()

        if not tmp:
            tmp = (chan, chan_progs[0][1], 'No schedule', 0)
            
        all_channels += [tmp]
        
    return all_channels

        
def download_guide():
    if os.path.isfile('/tmp/freevo_epg.html'):
        if os.path.getmtime('/tmp/freevo_epg.html') < (time.time() - 3600):
            # Use wget to get an EPG from somewhere
            os.system('%s "%s"' % ('wget -q -O /tmp/freevo_epg.html', config.EPG_URL))
    else:
        # Use wget to get an EPG from somewhere
        os.system('%s "%s"' % ('wget -q -O /tmp/freevo_epg.html', config.EPG_URL))

    rawlines = open('/tmp/freevo_epg.html').readlines()

    lines = []
    for i in range(len(rawlines)):
        if rawlines[i].find('<A ') != -1:
            anchor = rawlines[i].strip() + rawlines[i+1].strip()
            if anchor.find('progutn') != -1:
                lines.append(get_info(anchor))
                get_info(anchor)

    guide = Dummy()
    guide.timestamp = os.path.getmtime('/tmp/freevo_epg.html')
    guide.programs = filter_guide(lines)

    return guide
    
    

def get_info(str):
    name, nr = get_channel(str)
    start = get_starttime(str)
    progname = get_progname(str)
    ts = time.asctime(time.localtime(start))
    #print '%3d: Channel: %-10s  Program: %-40s Time: %s' % (nr, name, progname, ts)
    return (nr, name, progname, start)


def get_channel(str):
    start_pos = str.find('chname=')

    if start_pos == -1:
        return 'UNKNOWN'
    else:
        start_pos += len('chname=')
        
    middle_pos = str[start_pos:].find('+')

    if middle_pos == -1:
        return 'UNKNOWN'

    end_pos = str[start_pos:].find('&')

    if end_pos == -1:
        return 'UNKNOWN'

    name = str[start_pos:start_pos+middle_pos].replace('%26', '&')
    nr = int(str[start_pos+middle_pos+1:start_pos+end_pos])
    
    return (name, nr)


def get_starttime(str):
    start_pos = str.find('progutn=')

    if start_pos == -1:
        return 0
    else:
        start_pos += len('progutn=')
        
    end_pos = str[start_pos:].find('&')

    if end_pos == -1:
        return 0

    start_time = int(str[start_pos:start_pos+end_pos])
    
    return start_time


def get_progname(str):

    # Cut out the part inside the anchor tag
    progname = str[str.rfind('>', 0, -4)+1:-4]
    
    return progname


if __name__ == '__main__':
    g = get_guide()

    print g.programs
    for channel in g.programs:
        for p in channel:
            print p
            hh = time.localtime(p[3])[3]
            mm = time.localtime(p[3])[4]
            print '%3d %-10s %-30.30s %2d.%02d' % (p[0], p[1], p[2], hh, mm)
        print
    

