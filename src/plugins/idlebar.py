#if 0 /*
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   To activate the idle bar, put the following in your local_config.py. The
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
#     plugin.activate('idlebar.clock',   level=50)
#
#   plugin.activate('idlebar.cdstatus', level=30)
#   plugin.activate('idlebar.clock',    level=50)
#   
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.25  2003/07/24 00:01:19  rshortt
# Extending the idlebar.tv plugin with the help (and idea) of Mike Ruelle.
# Now you may add args=(number,) to the plugin.activate for this plugin and
# it will warn you that number of hours before your xmltv data is invalid and
# present a more sever warning when your xmltv data is expired.
#
# The new icons are kind of lame so anyone feel free to spruce them up.
#
# Revision 1.24  2003/07/20 18:22:35  dischi
# added patch for different temp units from Michael Ruelle
#
# Revision 1.23  2003/07/18 03:47:34  outlyer
# Nasty bug that would cause a crash if you hit any remote button not used
# by the plugin you were in. It expected menuw to be defined, else it crashed
# hard.
#
# Revision 1.22  2003/07/15 17:08:21  dischi
# o Add/update some docs
# o show all rom drives in the bar
# o update the bar on event IDENTIFY_MEDIA
#
# Revision 1.21  2003/07/12 18:52:22  dischi
# fixed overscan bug
#
# Revision 1.20  2003/07/12 17:29:58  dischi
# redraw when polling
#
# Revision 1.19  2003/07/12 17:17:27  dischi
# moved idlebar to a skin plugin
#
# Revision 1.18  2003/07/05 14:57:07  dischi
# the idlebar registers itself as idlebar to the plugin interface
#
# Revision 1.17  2003/07/04 20:14:04  outlyer
# Fixed some confusing logic. It's still confusing, but it works now. Probably
# need to clean this up.
#
# Revision 1.16  2003/07/04 19:48:18  outlyer
# Whoops, fix path.
#
# Revision 1.15  2003/07/04 19:46:51  outlyer
# Added Rich C's "holidays" plugin for the idlebar.
#
# Revision 1.14  2003/07/04 15:17:56  outlyer
# New cdstatus plugin. Only tested on my machine so use with caution.
#
# To use it:
# plugin.activate('idlebar.cdstatus', level=60)
#
# There are a couple of known problems:
#
#     o Only the 'last' drive is shown (last from ROM_DRIVES)
#     o The way that cdbackup tells us we are ripping isn't so nice
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

DEBUG = config.DEBUG

TRUE  = 1
FALSE = 0


class interface(plugin.DaemonPlugin):
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
        osd.drawroundbox(0, 0, osd.width + 2 * osd.x, osd.y + 60, (0x80000000, 0, 0, 0))
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
    def __init__(self):
        IdleBarPlugin.__init__(self)
    
    def draw(self, (type, object), x, osd):
        clock = time.strftime('%a %I:%M %P')
        font  = osd.get_font('clock')
        osd.write_text(clock, font, None, osd.x + osd.width-200, osd.y + 10, 190,
                       40, 'right', 'center')
        return 0
    

class cdstatus(IdleBarPlugin):
    """
    show the status of all rom drives
    """
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.cdimages ={}
        self.cdimages ['audio'] = 'skins/images/status/cd_audio.png'
        self.cdimages ['empty_cdrom'] = 'skins/images/status/cd_inactive.png'
        self.cdimages ['images'] = 'skins/images/status/cd_photo.png'
        self.cdimages ['video'] = 'skins/images/status/cd_video.png'
        self.cdimages ['burn'] ='skins/images/status/cd_burn.png'
        self.cdimages ['cdrip'] = 'skins/images/status/cd_rip.png'
        self.cdimages ['mixed'] = 'skins/images/status/cd_mixed.png'

    def draw(self, (type, object), x, osd):
        image = self.cdimages['empty_cdrom']
        width = 0
        for media in config.REMOVABLE_MEDIA:
            image = self.cdimages['empty_cdrom']
            if hasattr(media.info,'type') and hasattr(media.info,'handle_type'):
                if not media.info.handle_type and media.info.type:
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
        self.NO_MAILIMAGE = 'skins/images/status/newmail_dimmed.png'
        self.MAILIMAGE = 'skins/images/status/newmail_active.png'
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
        self.TVLOCKED = 'skins/images/status/television_active.png'
        self.TVFREE = 'skins/images/status/television_inactive.png'
        self.NEAR_EXPIRED = 'skins/images/status/television_near_expired.png'
        self.EXPIRED = 'skins/images/status/television_expired.png'
        
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
        self.CLOCKFONT = 'skins/fonts/Trebuchet_MS.ttf'
        if not os.path.isfile(self.CLOCKFONT):
            # XXX Get this from the skin, but for now this will allow it to work
            self.CLOCKFONT = config.OSD_DEFAULT_FONTNAME

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
        osd.draw_image('skins/icons/weather/' + icon, (x, osd.y + 15, -1, -1))
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
                    return icon

    def draw(self, (type, object), x, osd):
        icon = self.get_holiday_icon()
        if icon:
            return osd.draw_image('skins/images/holidays/' + icon, (x, osd.y + 10, -1, -1))[0]
