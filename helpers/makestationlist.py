#!/usr/bin/python
#
# Generates stationlist.xml for use with tvtime
#
# call it as ./helpers/makestationlist.py
#
# TODO:
#       Map the various frequencies from freevo.conf ot the frequencies for tv time.
#
import sys
sys.path.append('./src/')
import config
import cgi

norm = "US-Cable"

fp = open('/tmp/stationlist.xml','w')

fp.write('<?xml version="1.0"?>\n')
fp.write('<!DOCTYPE stationlist PUBLIC "-//tvtime//DTD stationlist 1.0//EN" "http://tvtime.sourceforge.net/DTD/stationlist1.dtd">\n')
fp.write('<stationlist xmlns="http://tvtime.sourceforge.net/DTD/">\n')
fp.write('  <list norm="NTSC" frequencies="%s">\n' % (norm))

c = 0
for m in config.TV_CHANNELS:
    fp.write('    <station name="%s" active="1" position="%s" band="US Cable" channel="%s"/>\n' % (cgi.escape(m[1]),c,m[2]))
    c = c + 1

fp.write('  </list>\n')
fp.write('</stationlist>\n')
fp.close()
