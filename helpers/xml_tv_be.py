#!/usr/bin/env python
# middernachtprogrammas toegevoegd
# volgens de dtd is de tag desc en niet description

import re
import urllib
import getopt, sys
from string import replace
from time import time
from time import localtime
from time import strftime

locale = 'Latin-1'

def usage():
     print "xml_tv_be.py --days=3 (default=2)"
     

def inttochar( match ):
     """Return the hex string for a decimal number"""
     f = re.compile(r'&amp;#(\d+);')
     k = f.sub(r'\1', match.group())
     return chr(int(k))


def escape(s):
    """Replace special HTML chars""" 
    s = replace(s,'&amp;#146;','\x27') 
    p = re.compile(r'&amp;#(\d+);')
    s = p.sub(inttochar,s)
    s = replace(s,' &amp; ',' &amp;#38; ')
    return s


class cEvent:
    start=''
    end=''
    title=''
    subtitle=''
    description=[]
    images=[]
    
    def __init__(self,block,line,today,tomorrow):
	self.start_h='00'
	self.start_m='00'
	self.end_h=''
	self.end_m=''
	self.title=''
	self.category=''
	self.description=''
	self.today = today
	self.tomorrow = tomorrow
	state = 0

	for l in block:
            if state == 0:		# looking for first &lt;starttime&gt;
		r = re.search("&lt;td class='tvnucontent' valign='top'&gt;(.+)\.(.+)&lt;/td&gt;",l)
		if r != None:
		    self.start_h = r.group(1)
		    self.start_m = r.group(2)
		    state = 1

            elif state == 1:
		r = re.search("&lt;td class='tvnucontent' valign='top'&gt;(.+)\.(.+)&lt;/td&gt;",l)
		if r != None:
		    self.end_h = r.group(1)
		    self.end_m = r.group(2)
                    state = 2

            elif state == 2:
		r = re.search(".+ class=tvnu&gt;(.+)&lt;/a&gt;",l)
		if r != None:
		    self.title = escape(r.group(1))
		    state = 3

            elif state == 3:
		r = re.search("&lt;td class='tvnuthema' align=right valign='top' nowrap&gt;(.+)&lt;/td&gt;",l)
		if r != None:
		    self.category = escape(r.group(1))
                    state = 4

            elif state == 4:
		r = re.search("&lt;td width= '100%' valign='top' colspan=2 class=programmabeschrijving&gt;(.+)&lt;br&gt;",l)
		if r != None:
		    self.description = escape(r.group(1))


    def xml(self,channel_id):
        if self.title != '': 
          #veranderd terug nr zes, sommig proggies op ketnet beginne om 7u
          if self.start_h &lt; '06':
              print "  &lt;programme start=\"%s%s%s +0000\" stop=\"%s%s%s +0000\" channel=\"%s\"&gt;" % (self.tomorrow, self.start_h, self.start_m, self.tomorrow, self.end_h, self.end_m, channel_id)
          else:
            #programmas die vandaag beginnen mr morgen eindigen, aka hun einduur is kleiner dan het startuur 
	    if self.end_h &lt; self.start_h:              
		print "  &lt;programme start=\"%s%s%s +0000\" stop=\"%s%s%s +0000\" channel=\"%s\"&gt;" % (self.today, self.start_h, self.start_m, self.tomorrow, self.end_h, self.end_m, channel_id)
            else:
                print "  &lt;programme start=\"%s%s%s +0000\" stop=\"%s%s%s +0000\" channel=\"%s\"&gt;" % (self.today, self.start_h, self.start_m, self.today, self.end_h, self.end_m, channel_id)
          print "    &lt;title lang=\"nl\"&gt;%s&lt;/title&gt;" % self.title
          if self.category != '':
            print "    &lt;category lang=\"nl\"&gt;%s&lt;/category&gt;" % self.category
          if self.description != '':
            print "    &lt;desc lang=\"nl\"&gt;%s&lt;/desc&gt;" % self.description
          print "  &lt;/programme&gt;"


class cChannel:
    title = ''
    events = []
    
    def __init__(self,id,title,days):
        self.id=id
        self.title=title
	self.events = []

        for x in range(days):

          block = []
          state = 0
          date = strftime("%m/%d/%Y",localtime(time()+(x*86400)))
          today = strftime("%Y%m%d",localtime(time()+(x*86400)))
          tomorrow = strftime("%Y%m%d",localtime(time()+(x*86400)+86400))
          f=urllib.urlopen("http://www.tvsite.be/ndl/zender.asp?move=full&amp;channel=%s&amp;dag=%s"%(title,date))
          for l in f.read().splitlines():
	    if state==0:	# looking for first &lt;starttime&gt;
		r = re.search("&lt;td class='tvnucontent' valign='top'&gt;.+&lt;/td&gt;",l)
		if r != None:
	            block.append(l)
	            state = 1

            elif state == 1:	# looking for next &lt;starttime&gt;
		r = re.search("&lt;td class='tvnucontent' valign='top' rowspan=2&gt;.+",l)
		if r != None:
                    self.events.append(cEvent(block,l,today,tomorrow))
		    block=[]

        	block.append(l)

	    else:
		exit(1)

          self.events.append(cEvent(block,l,today,tomorrow))


    def xml(self,today = strftime("%Y/%m/%d",localtime(time())),tomorrow = strftime("%Y/%m/%d",localtime(time()+86400))):

        print "  &lt;channel id=\"%s\"&gt;" % self.id
        print "    &lt;display-name lang=\"nl\"&gt;%s&lt;/display-name&gt;" % self.title
        print "    &lt;icon&gt;http://www.tvsite.be/gfx/logos/%s.gif&lt;/icon&gt;" % self.title
	print "  &lt;/channel&gt;"
        for event in self.events:
            event.xml(self.id)


def main():

  try:
    opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "days="])
  except getopt.GetoptError:
    # print help information and exit:
    usage()
    sys.exit(2)
  dagen = 2
  for o, a in opts:
    if o in ("-h", "--help"):
       print "help"
       usage()
       sys.exit()
    if o in ("-d", "--days"):
       dagen = int(a)
  print "&lt;?xml version=\"1.0\" encoding=\"ISO-8859-1\"?&gt;"
  print "&lt;tv generator-info-name=\"Script by Bart Heremans, fixes,testing and debuging by den_RDC\"&gt;"

  cChannel(1,'TV1',dagen).xml()
  cChannel(2,'Ketnet',dagen).xml()
  cChannel(3,'Canvas',dagen).xml()
  cChannel(4,'VTM',dagen).xml()
  cChannel(5,'Kanaal2',dagen).xml()
  cChannel(6,'VT4',dagen).xml()
  cChannel(7,'Vitaya',dagen).xml()
  #cChannel(8,'EventTV',dagen).xml() #LibertyTV
  #cChannel(9,'KanaalZ',dagen).xml()
  #cChannel(10,'NBC',dagen).xml()
  cChannel(11,'Ned1',dagen).xml()
  cChannel(12,'Ned2',dagen).xml()
  cChannel(13,'Ned3',dagen).xml()
  cChannel(14,'Eurosport',dagen).xml()
  #cChannel(15,'Canal+',dagen).xml()
  #cChannel(16,'Canal+Blauw',dagen).xml()
  cChannel(17,'RTBF1',dagen).xml()
  cChannel(18,'RTBF2',dagen).xml()

  print "&lt;/tv&gt;"

if __name__ == "__main__":
  main()
