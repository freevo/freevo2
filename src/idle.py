import mailbox
import osd
import time
import os
import sys
import string
import config

sys.path.append('plugins/weather')
import pymetar

osd  = osd.get_singleton()

class IdleTool:
    
    def __init__(self):
        self.idlecount = 0
        osd.drawbox(0,0,768,75,color=0x80000000,width=-1)
        self.toolbar_surface = osd.getsurface(0,0,768,75)
        self.MAILBOX = '/var/mail/aubin'
        if not os.path.isfile(self.MAILBOX):
            # Try the mail environment; this might not work if the user runs this
            # as root, if he starts with 'sudo' it will though.
            if 'MAIL' in os.environ:
                self.MAILBOX = os.environ['MAIL']
            else:
                self.MAILBOX = ''
        self.CLOCKFONT = 'skins/fonts/Trebuchet_MS.ttf'
        if not os.path.isfile(self.CLOCKFONT):
            # XXX Get this from the skin, but for now this will allow it to work
            self.CLOCKFONT = config.OSD_DEFAULT_FONTNAME
        self.NO_MAILIMAGE = 'skins/images/status/newmail_dimmed.png'
        self.MAILIMAGE = 'skins/images/status/newmail_active.png'
        self.TVLOCKED = 'skins/images/status/television_active.png'
        self.TVFREE = 'skins/images/status/television_inactive.png'
        self.METARCODE = 'CYYZ'
        self.WEATHERCACHE = '/var/cache/freevo/weather'
        self.interval = 300
        self.tvlockfile = '/var/cache/freevo/record'


    def refresh(self):
        osd.putsurface(self.toolbar_surface,0,0)
        self.drawclock()
        self.drawmail()
        self.drawtv()
        self.drawweather()
        rect = (0,0,768,75)
        osd.update(rect)
        self.idlecount = -1

    def checkmail(self):
        if not self.MAILBOX:
            return 0
        if os.path.isfile(self.MAILBOX):
            mb = mailbox.UnixMailbox (file(self.MAILBOX,'r'))
            msg = mb.next()
            count = 0
            while msg is not None:
                count = count + 1
                msg = mb.next()
            return count
        else:
            return 0

    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0

    def checkweather(self):
        # We don't want to do this every 30 seconds, so we need
        # to cache the date somewhere. 
        # 
        # First check the age of the cache.
        #
        if (os.path.isfile(self.WEATHERCACHE) == 0 or (abs(time.time() - os.path.getmtime(self.WEATHERCACHE)) > 3600)):
            weather = pymetar.MetarReport()
            weather.fetchMetarReport(self.METARCODE)
            if (weather.getTemperatureCelsius()):
                temperature = '%2d' % weather.getTemperatureCelsius()
            else:
                temperature = '0'  # Make it a string to match above.
            if weather.getPixmap():
                icon = weather.getPixmap() + '.png'
            else:
                icon = 'sun.png'
            cachefile = open(self.WEATHERCACHE,'w+')
            cachefile.write(temperature + '\n')
            cachefile.write(icon + '\n')
            cachefile.close()
        else:
            cachefile = open(self.WEATHERCACHE,'r')
            newlist = map(string.rstrip, cachefile.readlines())
            temperature,icon = newlist
            cachefile.close()
        return temperature, icon

    def drawtv(self):
        if self.checktv() == 1:
            osd.drawbitmap(self.TVLOCKED,100,25)
        else:
            osd.drawbitmap(self.TVFREE,100,25)

    def drawweather(self):
        temp,icon = self.checkweather()
        osd.drawbitmap('plugins/weather/icons/' + icon,160,30)
        osd.drawstring(temp,175,50,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=14)
        osd.drawstring('o',192,47,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=10)
        
    def drawclock(self):
        clock = time.strftime('%a %I:%M %P')
        osd.drawstring(clock,580,40,fgcolor=0xffffff,font=self.CLOCKFONT,ptsize=12)

    def drawmail(self):
        if self.checkmail() > 0:
            osd.drawbitmap(self.MAILIMAGE,25,25)
        else:
            osd.drawbitmap(self.NO_MAILIMAGE,25,25) 

    def poll(self):
        self.idlecount = self.idlecount + 1
        if (self.idlecount%self.interval) == 0:
            self.refresh()
            self.idlecount = 0
