#!/usr/bin/python
#
import xmltv
import config
import os

x = xmltv.read_channels(open(config.XMLTV_FILE))

for i in x:
	try:
		imgsrc = i['icon'][0]['src']
	except KeyError:
		imgsrc = None
	channel = i['id']
	#print '%s - %s' % (imgsrc,channel)
	if imgsrc != None:
		print 'curl %s | convert - \'%s.png\'' % (imgsrc,channel)

	
