#if 0 /*
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   To activate the idle bar, put the following in your local_config.py
#
#   plugin.activate('idlebar.interface')
#   
#   plugin.activate('idlebar.mail',    level=10, args=('/var/spool/mail/dmeyer', ))
#   plugin.activate('idlebar.tv',      level=20)
#   plugin.activate('idlebar.weather', level=30, args=('4-letter code', ))
#   For weather station codes see: http://www.nws.noaa.gov/tg/siteloc.shtml
#   plugin.activate('idlebar.clock',   level=50)
#   
#
#
# Todo:        
#   Make it cleaner, right now coordinates and fonts are inside the skin
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.10  2003/06/04 23:36:35  rshortt
# Use the real cache dir and add a note about weather codes.
#
# Revision 1.9  2003/05/28 18:12:39  dischi
# pass object to draw to all sub-plugins
#
# Revision 1.8  2003/05/28 17:36:27  dischi
# make the weather zone a parameter
#
# Revision 1.7  2003/05/02 05:50:31  outlyer
# Stopgap to workaround a crash...
#
# Revision 1.6  2003/05/01 12:53:27  dischi
# added more information to plugin draw()
#
# Revision 1.5  2003/04/27 17:59:41  dischi
# use new poll interface
#
# Revision 1.4  2003/04/24 19:56:35  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.3  2003/04/19 21:25:00  dischi
# small changes at the plugin interface
#
# Revision 1.2  2003/04/18 10:22:07  dischi
# You can now remove plugins from the list and plugins know the list
# they belong to (can be overwritten). level and args are optional.
#
# Revision 1.1  2003/04/17 21:21:57  dischi
# Moved the idle bar to plugins and changed the plugin interface
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

import plugin

sys.path.append('plugins/weather')
import pymetar

import osd
osd  = osd.get_singleton()

TRUE  = 1
FALSE = 0


class interface(plugin.DaemonPlugin):
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval   = 300
        self.toolbar_surface = None
        self.plugins = None

        
    def draw(self, (type, object)):
        if not self.toolbar_surface:
            osd.drawbox(0,0,osd.width,75,color=0x80000000,width=-1)
            self.toolbar_surface = osd.getsurface(0,0,osd.width,75)
        if not self.plugins:
            self.plugins = plugin.get('idlebar')

        osd.putsurface(self.toolbar_surface,0,0)
        for p in self.plugins:
            p.draw((type, object))
        rect = (0,0,osd.width,75)
        osd.update(rect)


    def poll(self):
        # XXX This probably shouldn't be None,None, but at least it doesn't crash
        self.draw((None,None))


class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type = 'idlebar'
        
    def draw(self, (type, object)):
        return


class clock(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.CLOCKFONT = 'skins/fonts/Trebuchet_MS.ttf'
        if not os.path.isfile(self.CLOCKFONT):
            # XXX Get this from the skin, but for now this will allow it to work
            self.CLOCKFONT = config.OSD_DEFAULT_FONTNAME
    
    def draw(self, (type, object)):
        clock = time.strftime('%a %I:%M %P')
        osd.drawstring(clock,580,40,fgcolor=0xffffff,font=self.CLOCKFONT,ptsize=12)



    
class mail(IdleBarPlugin):
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

    def draw(self, (type, object)):
        if self.checkmail() > 0:
            osd.drawbitmap(self.MAILIMAGE,25,25)
        else:
            osd.drawbitmap(self.NO_MAILIMAGE,25,25) 




class tv(IdleBarPlugin):
    def __init__(self):
        IdleBarPlugin.__init__(self)
        self.tvlockfile = config.FREEVO_CACHEDIR + '/record'
        self.TVLOCKED = 'skins/images/status/television_active.png'
        self.TVFREE = 'skins/images/status/television_inactive.png'
        
    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0

    def draw(self, (type, object)):
        if self.checktv() == 1:
            osd.drawbitmap(self.TVLOCKED,100,25)
        else:
            osd.drawbitmap(self.TVFREE,100,25)



class weather(IdleBarPlugin):
    def __init__(self, zone='CYYZ'):
        IdleBarPlugin.__init__(self)
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
                cachefile = open(self.WEATHERCACHE,'r')
                newlist = map(string.rstrip, cachefile.readlines())
                temperature,icon = newlist
                cachefile.close()

        else:
            cachefile = open(self.WEATHERCACHE,'r')
            newlist = map(string.rstrip, cachefile.readlines())
            temperature,icon = newlist
            cachefile.close()
        return temperature, icon

    def draw(self, (type, object)):
        temp,icon = self.checkweather()
        osd.drawbitmap('plugins/weather/icons/' + icon,160,30)
        osd.drawstring(temp,175,50,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=14)
        osd.drawstring('o',192,47,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=10)
