#! /usr/bin/python

import re
import urllib
from time import time
from time import localtime
from time import strftime

class cEvent:
    start=''
    end=''
    title=''
    subtitle=''
    description=[]
    images=[]
    
    def __init__(self,block,line):
	self.start_h='00'
	self.start_m='00'
	self.end_h=''
	self.end_m=''
	self.title=''
	self.subtitle=''
	self.description=[]
	self.images=[]
	state = 0

	for l in block:
            if state == 0:		# looking for first <starttime>
		r = re.search('.+<starttime>(.+):(.+)</starttime>.+',l)
		if r != None:
		    self.start_h = r.group(1)
		    self.start_m = r.group(2)
		    state = 2
		else:
	            r = re.search('.+<starttime>(.+):(.+) -',l)
		    if r != None:
			self.start_h = r.group(1)
			self.start_m = r.group(2)
			state = 1

            elif state == 1:
		r = re.search('\240(.+):(.+)</starttime>.+',l)
		if r != None:
		    self.end_h = r.group(1)
		    self.end_m = r.group(2)
                    state = 2

	    elif state == 2:
		r = re.search('<td[^>]+>(.+)</td>',l)
		if r != None:
	            r2 = re.search('<img.+src=".+/(.+).gif"',r.group(1))
		    if r2 == None:
	        	r2 = re.search('<([^>]+)>(.+)</(.+)>',r.group(1))
			if r2 != None:
		            if r2.group(1)=='b':
	                	r3 = re.search('<a href="(.+)">(.+)</a>',r2.group(2))
				if r3 != None:
				    self.title = r3.group(2)
				else:
				    self.title = r2.group(2)
			    elif r2.group(1)=='i':
				self.subtitle = r2.group(2)
			    else:
				self.description.append(r2.group(2))
			else:
			    self.description.append(r.group(1))
		    else:
		        self.images.append(r2.group(1))
	
	if (self.end_h == ''):
	    r = re.search('.+<starttime>(.+):(.+)</starttime>.+',line)
	    if (r == None):
	        r = re.search('.+<starttime>(.+):(.+) -',l)
	    if (r != None):
		self.end_h = r.group(1)
		self.end_m = r.group(2)
	    else:
	    	self.end_h = self.start_h
		self.end_m = self.start_m


    def xml(self,channel_id,today):
        print "  <programme start=\"%s%s%s00 CET\" stop=\"%s%s%s00 CET\" channel=\"%s\">" % (today, self.start_h, self.start_m, today, self.end_h, self.end_m, channel_id)
	print "    <title lang=\"en\">%s</title>" % self.title    
	#print "    <desc lang=\"en\">"0
        #for l in self.description:
	#    if l != '': print l
	#print "    </desc>"
	print "  </programme>"


    def echo(self,full=0):
        print self.start_h, self.start_m, self.title
	if full==1:
	    if self.subtitle != '': print self.subtitle
	    for l in self.description:
	       if l != '': print l
    
    

class cChannel:
    title = ''
    events = []
    
    def __init__(self,id):
        self.title=''
	self.events = []
	self.id = id
	
	state = 0
	block = []

        f=urllib.urlopen("http://www.rtl.nl/active/tvview/index.xml?station=1&zender=%s&dag=1"%id)

	for l in f.read().splitlines():
	    if state==0:	# looking for channel title
		r = re.search('<td><font color="#333333"><b>(.+)</b>.+',l)
		if r != None:
		    self.title=r.group(1)
		    state = 11
		    
            elif state == 1:
	        r = re.search('</table>',l)
		if r != None:
		    state = 2
		    
            elif state == 2:
	        r = re.search('</table>',l)
		if r != None:
		    state = 3
		    
            elif state == 3:
	        r = re.search('.+<b>(.+)</b>.+',l)
		if r != None:
		    self.title=r.group(1)
		    state = 11
		    
            elif state == 11:	# looking for first <starttime>
		r = re.search('.+<starttime>.+',l)
		if r != None:
	            block.append(l)
	            state = 12

            elif state == 12:	# looking for next <starttime>
		r = re.search('.+<starttime>.+',l)
		if r != None:
                    self.events.append(cEvent(block,l))
		    block=[]

        	block.append(l)

	    else:
		exit(1)

	self.events.append(cEvent(block,l))
#	print id, state
	
    def xml(self,today = strftime("%Y%m%d",localtime(time()))):

        print "  <channel id=\"%s\">" % self.id
        print "    <display-name lang=\"en\">%s</display-name>" % self.title
	print "  </channel>"
        for event in self.events:
            event.xml(self.id,today)

    def echo(self,full=0):
	print "%s: %s" % (self.id, self.title)
        for event in self.events:
            event.echo(full)





#channels = []
#channels.append(cChannel( 'Nederland 1',	1 ))
#channels.append(cChannel( 'Nederland 2',	2 ))
#channels.append(cChannel( 'Nederland 3',	3 ))
#channels.append(cChannel( 'RTL4',		4 ))
#channels.append(cChannel( 'RTL5',		31 ))
#channels.append(cChannel( 'Yorin',		46 ))
#channels.append(cChannel( 'SBS6',		36 ))
#channels.append(cChannel( 'Net 5',		37 ))
#channels.append(cChannel( 'V8',			34 ))

print "<tv generator=\"nlprogs.py by Mark Hurenkamp\">"
#for c in range(1,88):
for c in range(1,4):
    cChannel(c).xml()
print "</tv>"
