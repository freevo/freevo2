#if 0 /*
#  -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   To activate the idle bar, put the following in your local_conf.py. The
#   plugins inside the idlebar are sorted based on the level (except the
#   clock, it's always on the right side)
#
#   plugin.activate('idlebar')
#   
#   plugin.activate('idlebar.mail',    level=10, args=('/var/spool/mail/dmeyer', ))
#
#   plugin.activate('idlebar.tv',      level=20, args=(listings_threshold, ))
#     listings_threshold must be a number in hours.  For example if you put
#     args=(12, ) then 12 hours befor your xmltv listings run out the tv icon
#     will present a warning.  Once your xmltv data is expired it will present
#     a more severe warning.  If no args are given then no warnings will be
#     given.
#
#   plugin.activate('idlebar.weather', level=30, args=('4-letter code', ))
#     For weather station codes see: http://www.nws.noaa.gov/tg/siteloc.shtml
#     You can also set the unit as second parameter in args ('C', 'F', or 'K')
#
#   plugin.activate('idlebar.sensors', level=40, args=('cpusensor', 'casesensor', 'meminfo'))
#     cpu and case sensor are the corresponding lm_sensors : this should be
#     temp1, temp2 or temp3. defaults to temp3 for cpu and temp2 for case
#     meminfo is the memory info u want, types ar the same as in /proc/meminfo :
#     MemTotal -> SwapFree.
#     casesensor and meminfo can be set to None if u don't want them
#     This requires a properly configure lm_sensors! If the standard sensors frontend
#     delivered with lm_sensors works your OK.
#   
#   plugin.activate('idlebar.clock',   level=50)
#   plugin.activate('idlebar.cdstatus', level=30)
#   plugin.activate('idlebar.clock',    level=50)
#   
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.37  2003/08/24 19:59:43  outlyer
# Fixed this to be endian independent, as required by Python 2.3 (prevents
# another warning)
#
# Here's the warning in case anyone is curious:
# /usr/local/freevo/src/plugins/idlebar.py:115: FutureWarning: hex/oct
# constants > sys.maxint will return positive values in Python 2.4 and up
#
# Revision 1.36  2003/08/24 19:56:38  outlyer
# Adjust to the renamed 'type' of empty cdrom drives.
#
# Revision 1.35  2003/08/24 10:16:26  dischi
# do not use osd.OSDFont, xml_font has the font as font.font in it
#
# Revision 1.34  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
#
# Revision 1.33  2003/08/22 05:56:56  gsbarbieri
# Better alignment and horizontal expansion.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ----------------------------------------------------------------------- */
#endif


import time
import os
import config
import sys
import string
import mailbox
import skin
import tv_util

import plugin

import pymetar

import re

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0


class PluginInterface(plugin.DaemonPlugin):
    """
    global idlebar plugin.
    """
    def __init__(self):
        """
        init the idlebar
        """
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 300
        self.plugins = None
        plugin.register(self, 'idlebar')
        self.visible = TRUE
        
    def draw(self, (type, object), osd):
        """
        draw a background and all idlebar plugins
        """
        osd.drawroundbox(0, 0, osd.width + 2 * osd.x, osd.y + 60, (0x80000000L, 0, 0, 0))
        if not self.plugins:
            self.plugins = plugin.get('idlebar')
        x = osd.x + 10
        for p in self.plugins:
            add_x = p.draw((type, object), x, osd)
            if add_x:
                x += add_x + 20

    def eventhandler(self, event, menuw=None):
        """
        catch the IDENTIFY_MEDIA event to redraw the skin (maybe the cd status
        plugin wants to redraw)
        """
        if plugin.isevent(event) == 'IDENTIFY_MEDIA':
            skin.get_singleton().redraw()
        return FALSE
    
    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        skin.get_singleton().redraw()
        



class IdleBarPlugin(plugin.Plugin):
    """
    parent for all idlebar plugins
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type = 'idlebar'
        
    def draw(self, (type, object), x, osd):
        return


class clock(IdleBarPlugin):
    """
    show the current time
    """
    def __init__(self, format='%a %I:%M %P'):
        IdleBarPlugin.__init__(self)
        self.timeformat = format
        
    def draw(self, (type, object), x, osd):
        clock = time.strftime(self.timeformat)
        font  = osd.get_font('clock')
        pad_x = 10
        idlebar_height = 60
        
        w = font.font.stringsize( clock )
        h = font.font.height
        if h > idlebar_height:
            h = idlebar_height
        osd.write_text( clock, font, None,
                       ( osd.x + osd.width - w -pad_x ),
                       ( osd.y + ( idlebar_height - h ) / 2 ),
                       ( w + 1 ), h , 'right', 'center')
        return 0
    

class cdstatus(IdleBarPlugin):
    """
    show the status of all rom drives
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
        icondir = os.path.join(config.ICON_DIR, 'status')
        self.cdimages ={}
        self.cdimages ['audio']       = os.path.join(icondir, 'cd_audio.png')
        self.cdimages ['empty_cdrom'] = os.path.join(icondir, 'cd_inactive.png')
        self.cdimages ['images']      = os.path.join(icondir, 'cd_photo.png')
        self.cdimages ['video']       = os.path.join(icondir, 'cd_video.png')
        self.cdimages ['burn']        = os.path.join(icondir, 'cd_burn.png')
        self.cdimages ['cdrip']       = os.path.join(icondir, 'cd_rip.png')
        self.cdimages ['mixed']       = os.path.join(icondir, 'cd_mixed.png')

    def draw(self, (type, object), x, osd):
        image = self.cdimages['empty_cdrom']
        width = 0
        for media in config.REMOVABLE_MEDIA:
            image = self.cdimages['empty_cdrom']
            if hasattr(media.info,'type') and hasattr(media.info,'handle_type'):
                if media.info.type == 'empty_cdrom':
                    image = self.cdimages['empty_cdrom']
                elif not media.info.handle_type and media.info.type:
                    image = self.cdimages['mixed']
                elif media.info.handle_type: 
                    image = self.cdimages[media.info.handle_type]
            width += osd.draw_image(image, (x+width, osd.y + 10, -1, -1))[0] + 10
        if width:
            width -= 10
        return width


class mail(IdleBarPlugin):
    """
    show if new mail is in the mailbox
    """
    def __init__(self, mailbox):
        IdleBarPlugin.__init__(self)
        self.NO_MAILIMAGE = os.path.join(config.ICON_DIR, 'status/newmail_dimmed.png')
        self.MAILIMAGE = os.path.join(config.ICON_DIR, 'status/newmail_active.png')
        self.MAILBOX = mailbox

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

    def draw(self, (type, object), x, osd):
        if self.checkmail() > 0:
            return osd.draw_image(self.MAILIMAGE, (x, osd.y + 10, -1, -1))[0]
        else:
            return osd.draw_image(self.NO_MAILIMAGE, (x, osd.y + 10, -1, -1))[0] 




class tv(IdleBarPlugin):
    """
    show if the tv is locked or not
    """
    def __init__(self, listings_threshold=-1):
        IdleBarPlugin.__init__(self)

        self.listings_threshold = listings_threshold
        self.next_guide_check = 0
        self.listings_expire = 0
        self.tvlockfile = config.FREEVO_CACHEDIR + '/record'
        icondir = os.path.join(config.ICON_DIR, 'status')
        self.TVLOCKED     = os.path.join(icondir, 'television_active.png')
        self.TVFREE       = os.path.join(icondir, 'television_inactive.png')
        self.NEAR_EXPIRED = os.path.join(icondir, 'television_near_expired.png')
        self.EXPIRED      = os.path.join(icondir, 'television_expired.png')
        
    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0

    def draw(self, (type, object), x, osd):

        if self.checktv() == 1:
            return osd.draw_image(self.TVLOCKED, (x, osd.y + 10, -1, -1))[0]

        if self.listings_threshold != -1:
            now = time.time()

            if now > self.next_guide_check:
                if DEBUG: print 'TV: checking guide'
                self.listings_expire = tv_util.when_listings_expire()
                if DEBUG: print 'TV: listings expire in %s hours' % self.listings_expire
                # check again in 10 minutes
                self.next_guide_check = now + 10*60

            if self.listings_expire == 0:
                return osd.draw_image(self.EXPIRED, (x, osd.y + 10, -1, -1))[0]
            elif self.listings_expire <= self.listings_threshold:
                return osd.draw_image(self.NEAR_EXPIRED, (x, osd.y + 10, -1, -1))[0]

        return osd.draw_image(self.TVFREE, (x, osd.y + 10, -1, -1))[0]



class weather(IdleBarPlugin):
    """
    show the current weather
    """
    def __init__(self, zone='CYYZ', units='C'):
        IdleBarPlugin.__init__(self)
        self.TEMPUNITS = units
        self.METARCODE = zone
        self.WEATHERCACHE = config.FREEVO_CACHEDIR + '/weather'


    def checkweather(self):
        # We don't want to do this every 30 seconds, so we need
        # to cache the date somewhere. 
        # 
        # First check the age of the cache.
        #
        if (os.path.isfile(self.WEATHERCACHE) == 0 or \
            (abs(time.time() - os.path.getmtime(self.WEATHERCACHE)) > 3600)):
            weather = pymetar.MetarReport()
            try:
                weather.fetchMetarReport(self.METARCODE)
                if (weather.getTemperatureCelsius()):
                    if self.TEMPUNITS == 'F':
                        ctemp = weather.getTemperatureCelsius()
                        ftemp = ((ctemp + 40) * 9 / 5) - 40
                        temperature = '%2d' % ftemp
                    elif self.TEMPUNITS == 'K':
                        ktemp = weather.getTemperatureCelsius() + 273
                        temperature = '%3d' % ktemp
                    else:
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
            except:
                # HTTP Problems, use cache. Wait till next try.
                try:
                    cachefile = open(self.WEATHERCACHE,'r')
                    newlist = map(string.rstrip, cachefile.readlines())
                    temperature,icon = newlist
                    cachefile.close()
                except IOError:
                    print 'WEATHER: error reading cache. Using fake weather.'
                    return '0', 'sun.png'

        else:
            cachefile = open(self.WEATHERCACHE,'r')
            newlist = map(string.rstrip, cachefile.readlines())
            temperature,icon = newlist
            cachefile.close()
        return temperature, icon

    def draw(self, (type, object), x, osd):
        temp,icon = self.checkweather()
        font  = osd.get_font('weather')
        osd.draw_image(os.path.join(config.ICON_DIR, 'weather/' + icon),
                        (x, osd.y + 15, -1, -1))
        temp = '%s°' % temp
        width = font.font.stringsize(temp)
        osd.write_text(temp, font, None, x + 15, osd.y + 55 - font.h, width, font.h,
                       'left', 'top')
        return width + 15
        

class holidays(IdleBarPlugin):
    """
    This class checks if the current date is a holiday and will
    display a user specified icon for that holiday.    
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
   
    def get_holiday_icon(self):
        if not config.HOLIDAYS:
            return 0    
        else:
           # Creates a string which looks like "07-04" meaning July 04
            todays_date = time.strftime('%m-%d')
            
            for i in config.HOLIDAYS:                        
                holiday, icon = i
                if todays_date == holiday:
                    return os.path.join(config.ICON_DIR, 'holidays', icon)

    def draw(self, (type, object), x, osd):
        icon = self.get_holiday_icon()
        if icon:
            return osd.draw_image(icon, (x, osd.y + 10, -1, -1))[0]
            
            
#----------------------------------- SENSOR --------------------------------

class sensors(IdleBarPlugin):
    """
    read lm_sensors data for cpu temperature
    """
    class sensor:
        """
        small class defining a temperature sensor
        """
        def __init__(self, sensor, hotstack):
            self.initpath = "/proc/sys/dev/sensors/"
            self.senspath = self.getSensorPath()
            self.sensor = sensor
            self.hotstack = hotstack
            self.washot = FALSE
            
        def temp(self):
            if self.senspath == -1 or not self.senspath:
                return "?"        
            
            file = os.path.join( self.senspath, self.sensor )
            f = open(file)
            data = f.read()
            f.close()
            
            temp = int(float(string.split(data)[2]))
            hot = int(float(string.split(data)[0]))
            if temp > hot:
                if self.washot == FALSE:
                    self.hotstack = self.hotstack + 1
                    self.washot == TRUE
                    print temp
            else:
                if self.washot == TRUE:
                    self.hotstack = self.hotstack - 1
                    self.washot = FALSE
                
            return "%s°" % temp
            
        def getSensorPath(self):
            if not os.path.exists(self.initpath):
                print "LM_Sensors proc data not available? Did you load i2c-proc"
                print "and configured lm_sensors?"
                print "temperatures will be bogus"
                return -1 #failure
                
            for senspath in os.listdir(self.initpath):
                testpath = os.path.join(self.initpath , senspath)
                if os.path.isdir(testpath): 
                    return testpath
                    
    
    
    def __init__(self, cpu='temp3', case='temp2' , ram='MemTotal'):
        IdleBarPlugin.__init__(self)
        
        import re
        
        self.hotstack = 0
        self.case = None
    
        self.cpu = self.sensor(cpu, self.hotstack)
        if case: 
            self.case = self.sensor(case, self.hotstack)

        self.ram = ram
        self.retwidth = 0

        
    def getRamStat(self):

        f = open('/proc/meminfo')
        data = f.read()
        f.close()
        rxp_ram = re.compile('^%s' % self.ram)
        
        for line in data.split("\n"):
            m = rxp_ram.match(line)
            if m :
                return "%sM" % (int(string.split(line)[1])/1024)
        
    
    def draw(self, (type, object), x, osd):
        casetemp = None
        widthcase = 0
        widthram  = 0

        font  = osd.get_font('weather')
        if self.hotstack != 0:
            font.color = 0xff0000
        elif font.color == 0xff0000 and self.hotstack == 0:
            font.color = 0xffffff
        
        cputemp = self.cpu.temp()        
        widthcpu = font.font.stringsize(cputemp)
        osd.draw_image(os.path.join(config.ICON_DIR, 'misc/cpu.png'),
                       (x, osd.y + 8, -1, -1))    
        osd.write_text(cputemp, font, None, x + 15, osd.y + 55 - font.h, widthcpu, font.h,
                       'left', 'top')
        widthcpu = max(widthcpu, 32) + 10
        
        if self.case:
            casetemp = self.case.temp()
            
            widthcase = font.font.stringsize(casetemp)
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/case.png'),
                                        (x + 15 + widthcpu, osd.y + 7, -1, -1))
            osd.write_text(casetemp, font, None, x + 40 + widthcpu,
                           osd.y + 55 - font.h, widthcase, font.h,
                           'left', 'top')
            widthcase = max(widthcase, 32) + 10
            
        if self.ram:
            text = self.getRamStat()
            widthram = font.font.stringsize(text)
            if casetemp:
                img_width = x + 15 + widthcpu + widthcase + 15
            else:
                img_width = x + 15 + widthcpu
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/memory.png'),
                           (img_width, osd.y + 7, -1, -1))
            osd.write_text(text, font, None, img_width + 15, osd.y + 55 - font.h,
                           widthram, font.h, 'left', 'top')
                       
        if self.retwidth == 0:
            self.retwidth = widthcpu + 15
            if self.case: 
                self.retwidth = self.retwidth + widthcase + 12
            if self.ram:
                self.retwidth = self.retwidth + 15 + widthram
                
        return self.retwidth
