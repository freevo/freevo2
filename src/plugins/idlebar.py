#if 0 /*
# -----------------------------------------------------------------------
# idlebar.py - IdleBar plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#   To activate the idle bar, put the following in your local_config.py
#
#   plugin.activate('idlebar.interface', 'daemon', 10, None)
#   
#   plugin.activate('idlebar.mail',    'idlebar', 10, ('/var/spool/mail/dmeyer', ))
#   plugin.activate('idlebar.tv',      'idlebar', 20, None)
#   plugin.activate('idlebar.weather', 'idlebar', 30, None)
#   plugin.activate('idlebar.clock',   'idlebar', 50, None)
#   
#
#
# Todo:        
#   Make it cleaner, right now coordinates and fonts are inside the skin
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/04/17 21:21:57  dischi
# Moved the idle bar to plugins and changed the plugin interface
#
#
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
        self.idlecount = 0
        self.interval = 300
        self.toolbar_surface = None
        self.plugins = plugin.get('idlebar')
        self.osd = 1

        
    def refresh(self):
        if not self.toolbar_surface:
            osd.drawbox(0,0,osd.width,75,color=0x80000000,width=-1)
            self.toolbar_surface = osd.getsurface(0,0,osd.width,75)
        osd.putsurface(self.toolbar_surface,0,0)
        for p in self.plugins:
            p.draw()
        rect = (0,0,osd.width,75)
        osd.update(rect)
        self.idlecount = -1


    def poll(self):
        self.idlecount = self.idlecount + 1
        if (self.idlecount%self.interval) == 0:
            self.refresh()
            self.idlecount = 0



class IdleBarPlugin(plugin.Plugin):
    def draw(self):
        return


class clock(IdleBarPlugin):
    def __init__(self):
        self.CLOCKFONT = 'skins/fonts/Trebuchet_MS.ttf'
        if not os.path.isfile(self.CLOCKFONT):
            # XXX Get this from the skin, but for now this will allow it to work
            self.CLOCKFONT = config.OSD_DEFAULT_FONTNAME
    
    def draw(self):
        clock = time.strftime('%a %I:%M %P')
        osd.drawstring(clock,580,40,fgcolor=0xffffff,font=self.CLOCKFONT,ptsize=12)



    
class mail(IdleBarPlugin):
    def __init__(self, mailbox):
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

    def draw(self):
        if self.checkmail() > 0:
            osd.drawbitmap(self.MAILIMAGE,25,25)
        else:
            osd.drawbitmap(self.NO_MAILIMAGE,25,25) 




class tv(IdleBarPlugin):
    def __init__(self):
        self.tvlockfile = '/var/cache/freevo/record'
        self.TVLOCKED = 'skins/images/status/television_active.png'
        self.TVFREE = 'skins/images/status/television_inactive.png'
        
    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0

    def draw(self):
        if self.checktv() == 1:
            osd.drawbitmap(self.TVLOCKED,100,25)
        else:
            osd.drawbitmap(self.TVFREE,100,25)



class weather(IdleBarPlugin):
    def __init__(self):
        self.METARCODE = 'CYYZ'
        self.WEATHERCACHE = '/var/cache/freevo/weather'
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

    def draw(self):
        temp,icon = self.checkweather()
        osd.drawbitmap('plugins/weather/icons/' + icon,160,30)
        osd.drawstring(temp,175,50,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=14)
        osd.drawstring('o',192,47,fgcolor=0xbbbbbb,font=self.CLOCKFONT,ptsize=10)
