#if 0 /*
#  -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Documentation moved to the corresponding classes, so that the help
# interface returns something usefull.
# Available plugins:
#       idlebar
#       idlebar.clock
#       idlebar.cdstatus
#       idlebar.mail
#       idlebar.tv
#       idlebar.weather
#       idlebar.holidays
#       idlebar.procstats
#       idlebar.sensors
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.43  2003/10/14 18:11:22  dischi
# patches from Magus Schmidt
#
# Revision 1.42  2003/10/01 19:02:09  dischi
# add cpu usage patch from Viggo Fredriksen
#
# Revision 1.41  2003/09/21 13:19:00  dischi
# adjust poll intervall
#
# Revision 1.40  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.39  2003/09/12 20:32:49  dischi
# move holiday settings into the plugin
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
import types
import mailbox
import skin
import tv.tv_util as tv_util

import plugin

import pymetar

import re

class PluginInterface(plugin.DaemonPlugin):
    """
    global idlebar plugin.
    """
    def __init__(self):
        """
        init the idlebar
        """
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 3000
        self.plugins = None
        plugin.register(self, 'idlebar')
        self.visible = True
        
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
        return False
    
    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        skin.get_singleton().redraw()
        



class IdleBarPlugin(plugin.Plugin):
    """
    To activate the idle bar, put the following in your local_conf.py:
        plugin.activate('idlebar')
    You can then add various plugins. Plugins inside the idlebar are 
    sorted based on the level (except the clock, it's always on the 
    right side). Use "freevo plugins -l" to see all available plugins,
    and "freevo plugins -i idlebar.<plugin>" for a specific plugin.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type = 'idlebar'
        
    def draw(self, (type, object), x, osd):
        return


class clock(IdleBarPlugin):
    """
    Shows the current time.

    Activate with:
    plugin.activate('idlebar.clock',   level=50)
    Note: The clock will always be displayed on the right side of
    the idlebar.
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
    Show the status of all rom drives.

    Activate with:
    plugin.activate('idlebar.cdstatus')
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
    Shows if new mail is in the mailbox.
    
    Activate with:
    plugin.activate('idlebar.mail',    level=10, args=('path to mailbox', ))
    
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
    Informs you, when the xmltv-listings expires.

    Activate with:
    plugin.activate('idlebar.tv', level=20, args=(listings_threshold,))
    listings_threshold must be a number in hours.  For example if you put
    args=(12, ) then 12 hours befor your xmltv listings run out the tv icon
    will present a warning.  Once your xmltv data is expired it will present
    a more severe warning.  If no args are given then no warnings will be
    given.
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
                _debug_('TV: checking guide')
                self.listings_expire = tv_util.when_listings_expire()
                _debug_('TV: listings expire in %s hours' % self.listings_expire)
                # check again in 10 minutes
                self.next_guide_check = now + 10*60

            if self.listings_expire == 0:
                return osd.draw_image(self.EXPIRED, (x, osd.y + 10, -1, -1))[0]
            elif self.listings_expire <= self.listings_threshold:
                return osd.draw_image(self.NEAR_EXPIRED, (x, osd.y + 10, -1, -1))[0]

        return osd.draw_image(self.TVFREE, (x, osd.y + 10, -1, -1))[0]



class weather(IdleBarPlugin):
    """
    Shows the current weather.

    Activate with:
    plugin.activate('idlebar.weather', level=30, args=('4-letter code', ))

    For weather station codes see: http://www.nws.noaa.gov/tg/siteloc.shtml
    You can also set the unit as second parameter in args ('C', 'F', or 'K')
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
    Display some holidays in the idlebar
    
    This plugin checks if the current date is a holiday and will
    display a specified icon for that holiday. If no holiday is found,
    nothing will be displayed. If you use the idlebar, you should activate
    this plugin, most of the time you won't see it.

    You can customize the list of holidays with the variable HOLIDAYS in
    local_config.py. The default value is:

    [ ('01-01',  'newyear.png'),
      ('02-14',  'valentine.png'),
      ('05-07',  'freevo_bday.png'),
      ('07-03',  'usa_flag.png'),
      ('07-04',  'usa_flag.png'),
      ('10-30',  'ghost.png'),
      ('10-31',  'pumpkin.png'),
      ('12-21',  'snowman.png'),
      ('12-25',  'christmas.png')]
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
   
    def config(self):
        return [ ('HOLIDAYS', [ ('01-01',  'newyear.png'),
                                ('02-14',  'valentine.png'),
                                ('05-07',  'freevo_bday.png'),
                                ('07-03',  'usa_flag.png'),
                                ('07-04',  'usa_flag.png'),
                                ('10-30',  'ghost.png'),
                                ('10-31',  'pumpkin.png'),
                                ('12-21',  'snowman.png'),
                                ('12-25',  'christmas.png')],
                  'list of holidays this plugin knows') ]

    def get_holiday_icon(self):
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
            
            
#----------------------------------- PROCSTATS ----------------------------
class procstats(IdleBarPlugin):
    """
    Retrieves information from /proc/stat and shows them in the idlebar.
    This plugin can show semi-accurate cpu usage stats and free memory
    in megabytes (calculated approx. as MemFree+Cached?)

    Activate with 
       plugin.activate('idlebar.procstats',level=20) for defaults or
       plugin.activate('idlebar.procstats',level=20,args=(Mem,Cpu,Prec))
      where
       Mem:  Draw memfree  (default=1, -1 to disable)
       Cpu:  Draw cpuusage (default=1, -1 to disable)
       Prec: Precision used when drawing cpu usage (default=1)
    """
    def __init__(self,Mem=1,Cpu=1,Prec=1):
        IdleBarPlugin.__init__(self)
        self.drawCpu = Cpu
        self.drawMem = Mem
        self.precision = Prec
        self.time = 0
        self.lastused = 0
        self.lastuptime = 0

    def getStats(self):
        """
        Don't get the stats for each update
        as it gets annoying while navigating
        Update maximum every 10 seconds
        """
        if (time.time()-self.time)>10:
            self.time = time.time()

            if self.drawMem == 1:
                self.getMemUsage()

            if self.drawCpu == 1:
                self.getCpuUsage()

    def getMemUsage(self):
        """
        May not be correct, but i like to see
        total free mem as freemem+cached
        """
        free = 0
        f = open('/proc/meminfo')

        if f:
            meminfo = f.read()
            free = int(string.split(string.split(meminfo,'\n')[1])[3])

        f.close()
        self.currentMem = _('%iM') % (((free)/1024)/1024)

    def getCpuUsage(self):
        """
        This could/should maybe be an even more
        advanced algorithm, but it will suffice 
        for normal use.

        Note:
        cpu defined as 'cpu <user> <nice> <system> <idle>'
        at first line in /proc/stat
        """
        uptime = 0
        used = 0
        f = open('/proc/stat')

        if f:
            stat = string.split(f.readline())
            used = long(stat[1])+long(stat[2])+long(stat[3])
            uptime = used + long(stat[4])

        f.close()
        usage = (float(used-self.lastused)/float(uptime-self.lastuptime))*100
        self.lastuptime = uptime
        self.lastused = used
        self.currentCpu = _('%s%%') % round(usage,self.precision)
 
    def draw(self, (type, object), x, osd):
        font = osd.get_font('weather')
        self.getStats()
        widthmem = 0
        widthcpu = 0

        if self.drawCpu == 1:
            widthcpu = font.font.stringsize(self.currentCpu)
            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/cpu.png'),
                          (x, osd.y + 7, -1, -1))    
            osd.write_text(self.currentCpu, font, None, x + 15, osd.y + 55 - font.h,
                           widthcpu, font.h, 'left', 'top')

        if self.drawMem == 1:
            widthmem = font.font.stringsize(self.currentMem)

            osd.draw_image(os.path.join(config.ICON_DIR, 'misc/memory.png'),
                          (x + 15 + widthcpu, osd.y + 7, -1, -1))
            osd.write_text(self.currentMem, font, None, x + 40 + widthcpu, 
                           osd.y + 55 - font.h, widthmem, font.h, 'left', 'top')

        return widthmem + widthcpu + 15


#----------------------------------- SENSOR --------------------------------

class sensors(IdleBarPlugin):
    """
    Displays sensor temperature information (cpu,case) and memory-stats.

    Activate with:
       plugin.activate('idlebar.sensors', level=40, args=('cpusensor', 'casesensor', 'meminfo'))
       plugin.activate('idlebar.sensors', level=40, args=(('cpusensor','compute expression'), 
                                                          ('casesensor','compute_expression'),
                                                          'meminfo'))
    cpu and case sensor are the corresponding lm_sensors : this should be
    temp1, temp2 or temp3. defaults to temp3 for cpu and temp2 for case
    meminfo is the memory info u want, types ar the same as in /proc/meminfo :
    MemTotal -> SwapFree.
    casesensor and meminfo can be set to None if u don't want them
    This requires a properly configure lm_sensors! If the standard sensors frontend
    delivered with lm_sensors works your OK.
    Some sensors return raw-values, which have to be computed in order 
    to get correct values. This is normally stored in your /etc/sensors.conf.
    Search in the corresponding section for your chipset, and search the 
    compute statement, e.g. "compute temp3 @*2, @/2". Only the third
    argument is of interest. Insert this into the plugin activation line, e.g.: 
    "[...] args=(('temp3','@*2'),[...]". The @ stands for the raw value.
    The compute expression  works for the cpu- and casesensor.
    """
    class sensor:
        """
        small class defining a temperature sensor
        """
        def __init__(self, sensor, compute_expression, hotstack):
            self.initpath = "/proc/sys/dev/sensors/"
            self.senspath = self.getSensorPath()
            self.sensor = sensor
            self.compute_expression = compute_expression
            self.hotstack = hotstack
            self.washot = False
            
        def temp(self):
            def temp_compute (rawvalue):
                try:
                    temperature = eval(self.compute_expression.replace ("@",str(rawvalue)))
                except:
                    print "ERROR in idlebar.sensors: Compute expression does not evaluate"
                    temperature = rawvalue
                return int(temperature)

            if self.senspath == -1 or not self.senspath:
                return "?"        
            
            file = os.path.join( self.senspath, self.sensor )
            f = open(file)
            data = f.read()
            f.close()
            
            temp = int(temp_compute (float(string.split(data)[2])))
            hot = int(temp_compute (float(string.split(data)[0])))
            if temp > hot:
                if self.washot == False:
                    self.hotstack = self.hotstack + 1
                    self.washot == True
            else:
                if self.washot == True:
                    self.hotstack = self.hotstack - 1
                    self.washot = False
                
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
    
        if isinstance (cpu,types.StringType):
            self.cpu = self.sensor(cpu, '@', self.hotstack)
        else:
            self.cpu = self.sensor(cpu[0], cpu[1], self.hotstack)
    
        if case: 
            if isinstance (case,types.StringType):
                self.cpu = self.sensor(case, '@', self.hotstack)
            else:
                self.cpu = self.sensor(case[0], case[1], self.hotstack)


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
