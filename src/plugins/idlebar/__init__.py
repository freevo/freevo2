# -*- coding: iso-8859-1 -*-
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
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.19  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.18  2004/06/24 08:37:20  dischi
# add speed warning
#
# Revision 1.17  2004/05/31 10:43:20  dischi
# redraw not only in main, redraw when skin is active
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


import time
import os
import sys
import string
import types
import mailbox
import re
import locale

import config
import plugin
import skin
import util.tv_util as tv_util
import util.pymetar as pymetar

from pygame import image,transform

class PluginInterface(plugin.DaemonPlugin):
    """
    global idlebar plugin.
    """
    def __init__(self):
        """
        init the idlebar
        """
        plugin.DaemonPlugin.__init__(self)
        self.poll_interval  = 3000
        self.poll_menu_only = False
        self.plugins = None
        plugin.register(self, 'idlebar')
        self.visible = True
        self.bar     = None
        self.barfile = ''

        # Getting current LOCALE
        try:
            locale.resetlocale()
        except:
            pass


    def draw(self, (type, object), osd):
        """
        draw a background and all idlebar plugins
        """
        w = osd.width + 2 * osd.x
        h = osd.y + 60

        f = skin.get_image('idlebar')

        if self.barfile != f:
            self.barfile = f
            try:
                self.bar = transform.scale(image.load(f).convert_alpha(), (w,h))
            except:
                self.bar = None
                
        # draw the cached barimage
        if self.bar:
            osd.drawimage(self.bar, (0, 0, w, h), background=True)

        if not self.plugins:
            self.plugins = plugin.get('idlebar')

        x = osd.x + 10
        for p in self.plugins:
            add_x = p.draw((type, object), x, osd)
            if add_x:
                x += add_x + 20
        self.free_space = x


    def eventhandler(self, event, menuw=None):
        """
        catch the IDENTIFY_MEDIA event to redraw the skin (maybe the cd status
        plugin wants to redraw)
        """
        if plugin.isevent(event) == 'IDENTIFY_MEDIA' and skin.active():
            skin.redraw()
        return False


    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        if skin.active():
            skin.redraw()




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
    def __init__(self, format=''):
        IdleBarPlugin.__init__(self)
	if format == '': # No overiding of the default value
	    if time.strftime('%P') =='':
                format ='%a %H:%M'
            else:
                format ='%a %I:%M %P'
        self.timeformat = format

    def draw(self, (type, object), x, osd):
        clock = time.strftime(self.timeformat)
        font  = osd.get_font('clock')
        pad_x = 10
        idlebar_height = 60

        w = font.stringsize( clock )
        h = font.font.height
        if h > idlebar_height:
            h = idlebar_height
        osd.write_text( clock, font, None,
                       ( osd.x + osd.width - w -pad_x ),
                       ( osd.y + ( idlebar_height - h ) / 2 ),
                       ( w + 1 ), h , 'right', 'center')
        self.clock_left_position = osd.x + osd.width - w - pad_x
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
        self.cdimages ['audiocd']       = os.path.join(icondir, 'cd_audio.png')
        self.cdimages ['empty_cdrom'] = os.path.join(icondir, 'cd_inactive.png')
        self.cdimages ['images']      = os.path.join(icondir, 'cd_photo.png')
        self.cdimages ['video']       = os.path.join(icondir, 'cd_video.png')
        self.cdimages ['dvd']         = os.path.join(icondir, 'cd_video.png')
        self.cdimages ['burn']        = os.path.join(icondir, 'cd_burn.png')
        self.cdimages ['cdrip']       = os.path.join(icondir, 'cd_rip.png')
        self.cdimages ['mixed']       = os.path.join(icondir, 'cd_mixed.png')

    def draw(self, (type, object), x, osd):
        image = self.cdimages['empty_cdrom']
        width = 0
        for media in config.REMOVABLE_MEDIA:
            image = self.cdimages['empty_cdrom']
            if media.type == 'empty_cdrom':
                image = self.cdimages['empty_cdrom']
            if media.type and self.cdimages.has_key(media.type):
                image = self.cdimages[media.type]
            else:
                image = self.cdimages['mixed']

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
        print
        print 'WARNING: the idlebar.weather plugin downloads new weather'
        print 'information inside the main loop. This bug makes all menu'
        print 'actions _very_ slow. Consider not using this plugin for higher'
        print 'speed.'
        print


    def checkweather(self):
        # We don't want to do this every 30 seconds, so we need
        # to cache the date somewhere.
        #
        # First check the age of the cache.
        #
        if (os.path.isfile(self.WEATHERCACHE) == 0 or \
            (abs(time.time() - os.path.getmtime(self.WEATHERCACHE)) > 3600)):
            try:
                rf=pymetar.ReportFetcher(self.METARCODE)
                rep=rf.FetchReport()
                rp=pymetar.ReportParser()
                pr=rp.ParseReport(rep)
                if (pr.getTemperatureCelsius()):
                    if self.TEMPUNITS == 'F':
                        temperature = '%2d' % pr.getTemperatureFahrenheit()
                    elif self.TEMPUNITS == 'K':
                        ktemp = pr.getTemperatureCelsius() + 273
                        temperature = '%3d' % ktemp
                    else:
                        temperature = '%2d' % pr.getTemperatureCelsius()
                else:
                    temperature = '?'  # Make it a string to match above.
                if pr.getPixmap():
                    icon = pr.getPixmap() + '.png'
                else:
                    icon = 'sun.png'
                cachefile = open(self.WEATHERCACHE,'w+')
                cachefile.write(temperature + '\n')
                cachefile.write(icon + '\n')
                cachefile.close()
            except:
                try:
                    # HTTP Problems, use cache. Wait till next try.
                    cachefile = open(self.WEATHERCACHE,'r')
                    newlist = map(string.rstrip, cachefile.readlines())
                    temperature,icon = newlist
                    cachefile.close()
                except IOError:
                    print 'WEATHER: error reading cache. Using fake weather.'
                    try:
                        cachefile = open(self.WEATHERCACHE,'w+')
                        cachefile.write('?' + '\n')
                        cachefile.write('sun.png' + '\n')
                        cachefile.close()
                    except IOError:
                        print 'You have no permission to write %s' % self.WEATHERCACHE
                    return '0', 'sun.png'


        else:
            cachefile = open(self.WEATHERCACHE,'r')
            newlist = map(string.rstrip, cachefile.readlines())
            temperature,icon = newlist
            cachefile.close()
        return temperature, icon

    def draw(self, (type, object), x, osd):
        temp,icon = self.checkweather()
        font  = osd.get_font('small0')
        osd.draw_image(os.path.join(config.ICON_DIR, 'weather/' + icon),
                        (x, osd.y + 15, -1, -1))
        temp = u'%s\xb0' % temp
        width = font.stringsize(temp)
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



class logo(IdleBarPlugin):
    """
    Display the freevo logo in the idlebar
    """
    def __init__(self, image=None):
        IdleBarPlugin.__init__(self)
        self.image = image

    def draw(self, (type, object), x, osd):
        if not self.image:
            image = osd.settings.images['logo']
        else:
            image = os.path.join(config.IMAGE_DIR, self.image)
        return osd.drawimage(image, (x, osd.y + 5, -1, 75))[0]
