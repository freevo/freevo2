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

def myversion():
    version = 'XMLTV Parser 1.2.4\n'
    version += 'Module Author: Aubin Paul\n'
    version += 'Uses xmltv Python parser by James Oakley\n'
    return version

def get_guide():

    if os.path.isfile(config.XMLTV_FILE):
    	rawlines = xmltv.read_programmes(open(config.XMLTV_FILE))
    
    	nowtime = time.localtime()

	lines = []
	for i in rawlines:
		if (nowtime >= (strptime.strptime(i['start'],xmltv.date_format))) and \
       		   (nowtime <= (strptime.strptime(i['stop'], xmltv.date_format))) :
			c = string.split(i['channel'])
			t = i['title'][0][0].encode('Latin-1')
			d = time.mktime(strptime.strptime(i['start'],xmltv.date_format))
			program = (int(c[0]),c[1],t,d)
			channel = program
		 	lines.append([channel])

	guide = Dummy()
	guide.timestamp = time.time()
	guide.programs = lines

    return guide
    
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
    

