#!/usr/bin/env python

#changelog 2.0 - logo generation now works, 40 channels
# added, configuration is now saved in config file
#including the number of days to be fetched..
#more info see config file -- den_RDC

# changelog 1.31 - tvsite.be word teveblad.be -- den_RDC
# universal timezone generator included for tz generation

# changelog 1.3 (same as cvs version tag in freevo-cvs)
# middernachtprogrammas toegevoegd
# volgens de dtd is de tag desc en niet description

import re
import urllib
import getopt, sys
import ConfigParser
from string import replace, lower
from time import time
from time import localtime
from time import strftime
from time import altzone

version = '2.0'
locale = 'Latin-1'
TRUE=1
FALSE=0

def usage(dagen):
    """print help message"""
    print "xml_tv_be.py version %s" % version
    print "Usage :"
    print "  xml_tv_be.py > /tmp/TV.xml"    
    print "    Generate xml listing"
    print "  xml_tv_be.py --days=3    (current=%s)" % dagen
    print "    Sets number of days to fetch. Persistent."
    print "  xml_tv_be --help"
    print "    Display this message"
    print "xml_tv_be.config file contains the configuration"

def inttochar( match ):
     """Return the hex string for a decimal number"""
     f = re.compile(r'&#(\d+);')
     k = f.sub(r'\1', match.group())
     return chr(int(k))


def escape(s):
    """Replace special HTML chars and <br> tag"""
    s = replace(s,'&#146;','\x27')
    p = re.compile(r'&#(\d+);')
    s = p.sub(inttochar,s)
    s = replace(s,' & ',' &#38; ')
    #replace <br> tags, some of them can be in the desc field
    s = replace(s, '<br>', ' ')
    return s

def localtz():
    """returns timezone in "+xxxx" or "-xxxx"' format, daylight savings time aware
     will work everywhere, minute precision
     check if timezone is gmt + or gmt -
     will not work if system time is not local i think """
     
    if altzone <= 0:
        tz = "+"
    else:
        tz = "-"
    # insert first 2 digits of timezone (hour)
    if abs(altzone / 3600) < 10:
        tz = tz + "0" + str(abs(altzone / 3600))
    else:
        tz = tz + str(abs(altzone / 3600))
    #insert last 2 digits of timezone (minutes)
    if abs(altzone % 3600) < 10:
        tz = tz + "0" + str(abs(altzone % 3600))
    else:
        tz = tz + str(abs(altzone % 3600))
    return tz

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
            if state == 0:              # looking for first <starttime>
                r = re.search("<td class='tvnucontent' valign='top'>(.+)\.(.+)</td>",l)
                if r != None:
                    self.start_h = r.group(1)
                    self.start_m = r.group(2)
                    state = 1

            elif state == 1:
                r = re.search("<td class='tvnucontent' valign='top'>(.+)\.(.+)</td>",l)
                if r != None:
                    self.end_h = r.group(1)
                    self.end_m = r.group(2)
                    state = 2

            elif state == 2:
                r = re.search(".+ class=tvnu>(.+)</a>",l)
                if r != None:
                    self.title = escape(r.group(1))
                    state = 3

            elif state == 3:
                r = re.search("<td class='tvnuthema' align=right valign='top' nowrap>(.+)</td>",l)
                if r != None:
                    self.category = escape(r.group(1))
                    state = 4

            elif state == 4:
                r = re.search("<td width= '100%' valign='top' colspan=2 class=programmabeschrijving>(.+)<br>",l)
                if r != None:
                    self.description = escape(r.group(1))


    def xml(self,channel_id):
        if self.title != '':
          #veranderd terug nr zes, sommig proggies op ketnet beginne om 7u
          if self.start_h < '06':
              print "  <programme start=\"%s%s%s %s\" stop=\"%s%s%s %s\" channel=\"%s\">" % (self.tomorrow, self.start_h, self.start_m, localtz(), self.tomorrow, self.end_h, self.end_m, localtz(), channel_id)
          else:
            #programmas die vandaag beginnen mr morgen eindigen, aka hun einduur is kleiner dan het startuur
            if self.end_h < self.start_h:
                print "  <programme start=\"%s%s%s %s\" stop=\"%s%s%s %s\" channel=\"%s\">" % (self.today, self.start_h, self.start_m, localtz(), self.tomorrow, self.end_h, self.end_m, localtz(), channel_id)
            else:
                print "  <programme start=\"%s%s%s %s\" stop=\"%s%s%s %s\" channel=\"%s\">" % (self.today, self.start_h, self.start_m, localtz(), self.today, self.end_h, self.end_m, localtz(), channel_id)
          print "    <title lang=\"nl\">%s</title>" % self.title
          if self.category != '':
            print "    <category lang=\"nl\">%s</category>" % self.category
          if self.description != '':
            print "    <desc lang=\"nl\">%s</desc>" % self.description
          print "  </programme>"


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
          f=urllib.urlopen("http://www.teveblad.be/ndl/zender.asp?move=full&channel=%s&dag=%s"%(title,date))
          for l in f.read().splitlines():
            if state==0:        # looking for first <starttime>
                r = re.search("<td class='tvnucontent' valign='top'>.+</td>",l)
                if r != None:
                    block.append(l)
                    state = 1

            elif state == 1:    # looking for next <starttime>
                r = re.search("<td class='tvnucontent' valign='top' rowspan=2>.+",l)
                if r != None:
                    self.events.append(cEvent(block,l,today,tomorrow))
                    block=[]

                block.append(l)

            else:
                exit(1)

          self.events.append(cEvent(block,l,today,tomorrow))


    def xml(self,today = strftime("%Y/%m/%d",localtime(time())),tomorrow = strftime("%Y/%m/%d",localtime(time()+86400))):

        print "  <channel id=\"%s\">" % self.id
        print "    <display-name lang=\"nl\">%s</display-name>" % self.title
        print "    <icon src=\"http://www.teveblad.be/gfx/logos/%s.gif\" />" % self.title
        print "  </channel>"
        for event in self.events:
            event.xml(self.id)


def main():

  config = ConfigParser.ConfigParser()
  
  #try to open config file and load the settings
  try:
    configfile = open('xml_tv_be.config', 'r+')
  except IOError:
    sys.stderr.write( 'Cannot open xml_tv_be.config. Does this file exist?\n')
    sys.exit()    
  
  config.readfp(configfile)
  dagen = config.getint('settings', 'days')
  
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help", "days="])
  except getopt.GetoptError:
    # print help information and exit:
    sys.stderr.write('Invalid command line options. Try --help for more info.\n')
    sys.exit(2)
  
  for o, a in opts:
    if o in ("-h", "--help"):
       #print "help"
       usage(dagen)
       sys.exit()
       
    if o in ("-d", "--days"):
       dagen = int(a)
       config.set('settings', 'days' , a)
       config.write(configfile)
       print "New value written to config file."
       sys.exit()
       
  print "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>"
  print "<tv generator-info-name=\"Script by Bart Heremans and den_RDC\">"

  for channel in config.options('channels'):
    if config.getint('channels', channel) == TRUE:
       cChannel(lower(channel), channel, dagen).xml()
  
  print "</tv>"

if __name__ == "__main__":
  main()

