# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# apod.py - download the Astronomy Picture of the Day
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.4  2004/06/29 01:39:20  mikeruelle
# added some userproofing to apod
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


import os
import config
import plugin
import menu
import urllib
import rc
import re

from item import Item
from image.imageitem import ImageItem
from gui.AlertBox import AlertBox

class ApodMainMenuItem(Item):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent, apoddir):
        Item.__init__(self, parent, skin_type='image')
        self.name = _( 'APOD' )
        self.title = _( 'APOD' )
        self.apoddir = apoddir
        self.info = { 'name' : 'APOD', 'description' : 'Astronomy Picture of the day', 'title' : 'APOD' }
        self.type = 'image'

    def actions(self):
        return [ ( self.create_apod_menu , 'APOD Pictures' ) ]

    def create_apod_menu(self, arg=None, menuw=None):
        apodmenuitems = []
        apodmenuitems += [menu.MenuItem(_('Current Picture'), action=self.fetchCurrentPicture)]
        apodmenuitems += [menu.MenuItem(_('Previous Pictures'), action=self.browsePictureDir)]
        apod_menu = menu.Menu( _( 'Apod Pictures' ), apodmenuitems)
        rc.app(None)
        menuw.pushmenu(apod_menu)
        menuw.refresh()

    def browsePictureDir(self, arg=None, menuw=None):
        apodpic_items = []
        apodpics = os.listdir(self.apoddir)
        apodpics.sort(lambda l, o: cmp(l.upper(), o.upper()))
        for apodpic in apodpics:
            img_item = ImageItem(os.path.join(self.apoddir,apodpic), self)
            apodpic_items += [ img_item ]
        if (len(apodpic_items) == 0):
            apodpic_items += [menu.MenuItem(_('No Images found'),
                                             menuw.back_one_menu, 0)]
        apodpic_menu = menu.Menu(_('Apod Pictures'), apodpic_items,
                                     reload_func=menuw.back_one_menu )
        rc.app(None)
        menuw.pushmenu(apodpic_menu)
        menuw.refresh()

    def fetchCurrentPicture(self, arg=None, menuw=None):
        url = 'http://antwrp.gsfc.nasa.gov/apod/%s'
        apodpichref = ''
        try:
            myfile=urllib.urlopen(url % 'index.html')
            apodpage=myfile.read()
            result = re.search("a href=\"(image.*)\"", apodpage)
            apodpichref = result.group(1)
        except:
            #unreachable or url error
            realurl = url % 'index.html'
            print 'APOD ERROR: could not open %s' % realurl
            AlertBox(text=_('Unable to open URL')).show()
            return

        apodfile = os.path.join(self.apoddir,os.path.basename(apodpichref))

        try:
            urllib.urlretrieve(url % apodpichref, apodfile)
            imgitem = ImageItem(apodfile, self)
            imgitem.view(menuw=menuw)
        except:
            #unreachable or url error
            realurl = url % apodpichref
            print 'APOD ERROR: could not open %s' % realurl
            AlertBox(text=_('Unable to open URL')).show()
            return

class PluginInterface(plugin.MainMenuPlugin):
    """
    Astronomy Picture of the Day download plugin. Downloads the picture
    for the current day and allow access to the dir for browsing the old
    pictures

    plugin.activate('image.apod', args=('/dir_for_apod',))

    """
    def __init__(self, apoddir=None):
        if not apoddir:
            self.reason = _('Need a directory to store APOD pictures.')
            return
    
        if not os.path.isdir(apoddir):
            self.reason = _('directory %s does not exist.') % apoddir
            return

        if not os.access(apoddir, os.R_OK|os.W_OK|os.X_OK):
            self.reason = _('directory %s must be able to be read, written to and executed by the user running freevo.') % apoddir
            return

        self.apoddir = apoddir

        # init the plugin
        plugin.MainMenuPlugin.__init__(self)

    def items(self, parent):
        return [ ApodMainMenuItem(parent, self.apoddir) ]
                                                                                        


