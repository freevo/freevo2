import xmltv
import time

# Use the pure Python version until I can figure out
# why the "time" module's version won't understand the
# time zone part of XMLTV's date format. 
import strptime

programs = xmltv.read_programmes(open('/tmp/TV.xml'))
nowtime = time.localtime() 

for program in programs:
	if (nowtime >= (strptime.strptime(program['start'],xmltv.date_format))) and \
	   (nowtime <= (strptime.strptime(program['stop'], xmltv.date_format))) :
	   	print '%s: %s' % (program['channel'],program['title'][0][0].encode('latin-1'))
		# The title bit is messy, I know, but it's a tuple with a list with a tuple with unicode
		# this breaks on unicode titles though, and I have no idea why; outside of the unicode
		# it's ready to replace the existing epg code that reads yahoo.



