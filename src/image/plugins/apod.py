# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# apod.py - download the Astronomy Picture of the Day
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003-2007 Dirk Meyer, et al.
#
# First Edition: Michael Ruelle <mikeruelle@comcast.net>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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
# -----------------------------------------------------------------------------

# python imports
import os
import urllib
import re

# kaa imports
import kaa
import kaa.beacon

# freevo imports
from freevo.ui.menu import Item, Action, ActionItem, Menu, MediaPlugin
from freevo.ui.mainmenu import MainMenuPlugin
from freevo.ui.image import ImageItem
from freevo.ui.application import TextWindow, MessageWindow

class ApodMainMenuItem(Item):
    """
    This is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent, imagedir):
        Item.__init__(self, parent)
        self.name = _( 'APOD' )
        self.info = { 'title'       : 'APOD',
                      'description' : 'Astronomy Picture of the day' }
        self.imagedir = imagedir


    def actions(self):
        """
        Return actions for the item.
        """
        return [ Action(_('APOD Pictures'), self.create_menu) ]


    def create_menu(self):
        """
        Create a menu for APOD.
        """
        # current image
        current = ActionItem(_('Current Picture'), self, self.fetch_picture)
        current.description = _('Download the current picture')

        # previous images
        previous = ActionItem(_('Previous Pictures'), self,
                              self.browse_pictures)
        previous.description = _('Browse all previously downloaded images')

        # add menu
        self.get_menustack().pushmenu(Menu( _( 'Apod Pictures' ), [ current, previous ]))


    def browse_pictures(self):
        """
        Show a list of all APOD.
        """
        listing = kaa.beacon.query(filename=self.imagedir).get(filter='extmap')

        # get items
        items = []
        for p in MediaPlugin.plugins('image'):
            items += p.get(self, listing)

        if items:
            self.get_menustack().pushmenu(Menu(_('Apod Pictures'), items))
        else:
            MessageWindow(_('No Images found')).show()


    def fetch_picture(self):
        """
        Fetch current picture.
        """
        box = TextWindow(text=_('Getting picture, please wait'))
        box.show()

        async = kaa.ThreadCallback(self._fetch_picture_thread)()
        async.connect(self._fetch_picture_finished, box)
        async.exception_handler.connect(self._fetch_picture_error, box)


    def _fetch_picture_thread(self):
        """
        Fetch current picture.
        """
        url = 'http://antwrp.gsfc.nasa.gov/apod/'

        try:
            myfile=urllib.urlopen(url + 'index.html')
            apodpage=myfile.read()
            result = re.search("a href=\"(image.*)\"", apodpage)
            ref = result.group(1)
        except Exception, e:
            raise 'Could not open %sindex.html: %s' % (url, e)

        filename = os.path.join(self.imagedir, os.path.basename(ref))

        try:
            urllib.urlretrieve(url + ref, filename)
            return filename
        except Exception, e:
            raise 'Could not open %s%s: %s' % (url, ref, e)


    def _fetch_picture_error(self, error, box):
        """
        Handle error for the thread in the main loop.
        """
        box.destroy()
        if not isinstance(error, (str, unicode)):
            error = 'Exception: %s' % error
        MessageWindow(error).show()


    def _fetch_picture_finished(self, filename, box):
        """
        Download finished.
        """
        box.destroy()
        ImageItem(filename, self, duration=0).play()





class PluginInterface(MainMenuPlugin):
    """
    Astronomy Picture of the Day download plugin. Downloads the picture
    for the current day and allow access to the dir for browsing the old
    pictures

    plugin.activate('image.apod', args=('/dir_for_apod',))

    """
    def __init__(self, imagedir=None):
        """
        Init plugin and check if imagedir is a valid directory.
        """
        if not imagedir:
            self.reason = _('Need a directory to store APOD pictures.')
            return

        if not os.path.isdir(imagedir):
            self.reason = _('Directory %s does not exist.') % imagedir
            return

        if not os.access(imagedir, os.R_OK|os.W_OK|os.X_OK):
            self.reason = _('Directory %s must be able to be read, ' + \
                            'written to and executed by the user running ' + \
                            'freevo.') % imagedir
            return

        self.imagedir = imagedir

        # init the plugin
        MainMenuPlugin.__init__(self)



    def items(self, parent):
        """
        Return the main menu item.
        """
        return [ ApodMainMenuItem(parent, self.imagedir) ]
