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
# Revision 1.26  2004/08/23 20:41:47  dischi
# fade support
#
# Revision 1.25  2004/08/23 15:53:41  dischi
# do not remove from display, only hide
#
# Revision 1.24  2004/08/22 20:10:38  dischi
# changes to new mevas based gui code
#
# Revision 1.23  2004/08/05 17:39:34  dischi
# remove skin dep
#
# Revision 1.22  2004/08/01 10:48:21  dischi
# Move idlebar to new gui code:
# o it is not drawn inside the area (a.k.a skin) code anymore
# o it updates/removes itself if needed
#
# Some plugins are not changed to the new draw interface of the
# idlebar. They are deactivated. Feel free to send an updated version.
#
# Revision 1.21  2004/07/25 18:22:27  dischi
# changes to reflect gui update
#
# Revision 1.20  2004/07/24 17:49:48  dischi
# rename or deactivate some stuff for gui update
#
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
import util.tv_util as tv_util
import util.pymetar as pymetar
import gui
import gui.imagelib
import eventhandler
from event import *


class PluginInterface(plugin.DaemonPlugin):
    """
    To activate the idle bar, put the following in your local_conf.py:
        plugin.activate('idlebar')
    You can then add various plugins. Plugins inside the idlebar are
    sorted based on the level (except the clock, it's always on the
    right side). Use 'freevo plugins -l' to see all available plugins,
    and 'freevo plugins -i idlebar.<plugin>' for a specific plugin.
    """
    def __init__(self):
        """
        init the idlebar
        """
        plugin.DaemonPlugin.__init__(self)
        plugin.register(self, 'idlebar')
        eventhandler.register(self, SCREEN_CONTENT_CHANGE)
        
        self.poll_interval  = 300
        self.poll_menu_only = False
        self.plugins        = None
        self.visible        = False
        self.bar            = None
        self.barfile        = ''
        self.background     = None
        self.container      = gui.CanvasContainer()
        self.container.set_zindex(10)
        gui.display.add_child(self.container)
        
        # Getting current LOCALE
        try:
            locale.resetlocale()
        except:
            pass


    def update(self):
        """
        draw a background and all idlebar plugins
        """
        screen  = gui.get_display()
        changed = False

        w = screen.width
        h = config.OSD_OVERSCAN_Y + 60
        f = gui.get_image('idlebar')

        if self.barfile != f:
            if self.bar:
                self.container.remove_child(self.bar)
            self.barfile = f
            self.bar = gui.Image(self.barfile, (0,0), (w, h))
            self.container.add_child(self.bar)
            changed = True

        x1 = config.OSD_OVERSCAN_X
        y1 = config.OSD_OVERSCAN_Y
        x2 = screen.width - config.OSD_OVERSCAN_X
        y2 = h

        for p in plugin.get('idlebar'):
            width = p.draw(x2 - x1, y2 - y1)
            if width == p.NO_CHANGE:
                if p.align == 'left':
                    x1 = x1 + p.width
                else:
                    x2 = x2 - p.width
                continue

            if width > x2 - x1:
                # FIXME
                continue

            if p.align == 'left':
                for o in p.objects:
                    o.set_pos((o.get_pos()[0] + x1, o.get_pos()[1] + y1))
                    self.container.add_child(o)
                x1 = x1 + width
            else:
                for o in p.objects:
                    o.set_pos((o.get_pos()[0] + x2 - width, o.get_pos()[1] + y1))
                    self.container.add_child(o)
                x2 = x2 - width
            p.width = width
            changed = True

        return changed
            

    def show(self, update=True, fade=0):
        if self.visible:
            return
        gui.animation.Fade([self.container], fade, 0, 255).start()
        self.visible = True
        self.update()
        if update:
            gui.get_display().update()


    def hide(self, update=True, fade=0):
        if not self.visible:
            return
        gui.animation.Fade([self.container], fade, 255, 0).start()
        self.visible = False
        if update:
            gui.get_display().update()
        

    def add_background(self):
        """
        add a background behind the bar
        """
        if not self.background:
            # FIXME: respect fxd settings changes!!!
            s = gui.get_display()
            self.background = gui.imagelib.load('background', (s.width, s.height))
            if self.background:
                size = (s.width, config.OSD_OVERSCAN_Y + 60)
                self.background.crop((0,0), size)
                self.background = gui.Image(self.background, (0,0))
                self.background.set_alpha(230)
                self.background.set_zindex(-1)
                self.container.add_child(self.background)
        else:
            self.background.show()
            
                                                  
    def remove_background(self):
        """
        remove the background behind the bar
        """
        if self.background:
            self.background.hide()

            
    def eventhandler(self, event, menuw=None):
        """
        catch the IDENTIFY_MEDIA event to redraw the skin (maybe the cd status
        plugin wants to redraw). Also catch SCREEN_CONTENT_CHANGE in case we
        need to hide/show the bar.
        """
        if event == SCREEN_CONTENT_CHANGE:
            # react on toggle fullscreen, hide or show the bar, but not update
            # the screen itself, this is done by the app later
            app, fullscreen, fade = event.arg
            if fade:
                fade = config.OSD_FADE_STEPS
            else:
                fade = 0
            if fullscreen:
                # add the background behind the bar
                self.add_background()
            else:
                # remove the background again, it's done by the
                # 'not in fullscreen' app.
                self.remove_background()
            if fullscreen == self.visible:
                _debug_('set visible %s' % (not fullscreen))
                if not self.visible:
                    self.show(False, fade=fade)
                else:
                    self.hide(False, fade=fade)
                self.update()
            return
        
        if not self.visible:
            return False
        if plugin.isevent(event) == 'IDENTIFY_MEDIA':
            if self.update():
                gui.get_display().update()
        return False


    def poll(self):
        """
        update the idlebar every 30 secs even if nothing happens
        """
        if not self.visible:
            return
        if self.update():
            gui.get_display().update()



class IdleBarPlugin(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        self._type     = 'idlebar'
        self.objects   = []
        self.NO_CHANGE = -1
        self.align     = 'left'

        
    def draw(self, width, height):
        return self.NO_CHANGE


    def clear(self):
        for o in self.objects:
            o.unparent()
        self.objects = []
        
            


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
        self.format = format
        self.object = None
        self.align  = 'right'
        self.width  = 0
        self.text   = ''

    def draw(self, width, height):
        clock  = time.strftime(self.format)

        if self.objects and self.text == clock:
            return self.NO_CHANGE

        self.clear()

        font  = gui.get_font('clock')
        width = min(width, font.stringsize(clock))

        txt = gui.Text(clock, (0, 0), (width, height), font,
                       align_v='center', align_h='right')
        self.objects.append(txt)
        self.text = clock
        return width



class cdstatus(IdleBarPlugin):
    """
    Show the status of all rom drives.

    Activate with:
    plugin.activate('idlebar.cdstatus')
    """
    def __init__(self):
        self.reason = 'draw() function needs update to work with new interface'
        return

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

            width += osd.drawimage(image, (x+width, osd.y + 10, -1, -1))[0] + 10
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
        self.reason = 'draw() function needs update to work with new interface'
        return

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
            return osd.drawimage(self.MAILIMAGE, (x, osd.y + 10, -1, -1))[0]
        else:
            return osd.drawimage(self.NO_MAILIMAGE, (x, osd.y + 10, -1, -1))[0]




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
        self.reason = 'draw() function needs update to work with new interface'
        return
        IdleBarPlugin.__init__(self)

        self.listings_threshold = listings_threshold
        self.next_guide_check   = 0
        self.listings_expire    = 0
        self.tvlockfile         = config.FREEVO_CACHEDIR + '/record'
        self.status             = None
        
        self.TVLOCKED     = 'television_active.png'
        self.TVFREE       = 'television_inactive.png'
        self.NEAR_EXPIRED = 'television_near_expired.png'
        self.EXPIRED      = 'television_expired.png'


    def clear(self):
        IdleBarPlugin.clear(self)
        self.status = None

        
    def checktv(self):
        if os.path.exists(self.tvlockfile):
            return 1
        return 0


    def draw(self, width, height):
        status = 'inactive'
        if self.checktv() == 1:
            status = 'active'

        if self.listings_threshold != -1:
            now = time.time()

            if now > self.next_guide_check:
                self.listings_expire = tv_util.when_listings_expire()
                # check again in 10 minutes
                self.next_guide_check = now + 10*60

            if self.listings_expire <= self.listings_threshold:
                status = 'near_expired'

            if self.listings_expire == 0:
                status = 'expired'

        if self.status == status:
            return self.NO_CHANGE

        self.clear()
        self.status = status
        i = gui.get_icon('status/television_%s' % status)
        i = gui.get_display().renderer.load(i, (None, height))
        
        w,h  = i.get_size()
        self.objects.append(gui.Image(0, 0, w, h, i))
        return w



class weather(IdleBarPlugin):
    """
    Shows the current weather.

    Activate with:
    plugin.activate('idlebar.weather', level=30, args=('4-letter code', ))

    For weather station codes see: http://www.nws.noaa.gov/tg/siteloc.shtml
    You can also set the unit as second parameter in args ('C', 'F', or 'K')
    """
    def __init__(self, zone='CYYZ', units='C'):
        self.reason = 'draw() function needs update to work with new interface'
        return

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
        osd.drawimage(os.path.join(config.ICON_DIR, 'weather/' + icon),
                        (x, osd.y + 15, -1, -1))
        temp = u'%s\xb0' % temp
        width = font.stringsize(temp)
        osd.drawstring(temp, font, None, x + 15, osd.y + 55 - font.h, width, font.h,
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
        self.reason = 'draw() function needs update to work with new interface'
        return
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
            return osd.drawimage(icon, (x, osd.y + 10, -1, -1))[0]



class logo(IdleBarPlugin):
    """
    Display the freevo logo in the idlebar
    """
    def __init__(self, image=None):
        IdleBarPlugin.__init__(self)
        self.image  = image
        self.file   = file
        self.object = None


    def draw(self, width, height):
        if not self.image:
            image = gui.get_image('logo')
        else:
            image = os.path.join(config.IMAGE_DIR, self.image)

        if self.objects and self.file == image:
            return self.NO_CHANGE

        self.file = image
        self.clear()
            
        i = gui.imagelib.load(image, (None, height + 10))
        if not i:
            return 0

        self.objects.append(gui.Image(i, (0, 0)))
        print 'add', self.objects
        return i.width
