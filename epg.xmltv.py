#
# epg.py
#
# This is the Freevo Electronic Program Guide module. 
#
# $Id$

import sys
import time, os, string, calendar

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The menu widget class
import menu

# The mpg123 application
import mpg123

# Use the alternate strptime module which seems to handle time zones
import strptime

# The XMLTV handler from openpvr.sourceforge.net
import xmltv

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

    if os.path.isfile(config.XMLTV_FILE):
    	rawlines = programs = xmltv.read_programmes(open(config.XMLTV_FILE))
    
    	nowtime = time.localtime()

	lines = []
	for i in rawlines:
		if (nowtime >= (strptime.strptime(i['start'],xmltv.date_format))) and \
       		   (nowtime <= (strptime.strptime(i['stop'], xmltv.date_format))) :
			c = string.split(i['channel'])
			t = i['title'][0][0].encode('Latin-1')
			d = calendar.timegm(strptime.strptime(i['start'],xmltv.date_format))
			program = (int(c[0]),c[1],t,d)
			channel = program
		 	lines.append([channel])

	guide = Dummy()
	guide.timestamp = time.time()
	guide.programs = lines

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
		#print p[3]
        	hh = time.localtime(p[3])[3]
        	mm = time.localtime(p[3])[4]
        	print '%3d %-10s %-30.30s %2d.%02d' % (p[0], p[1], p[2], hh, mm)
       	print
    

