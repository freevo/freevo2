#if 0 /*
# -----------------------------------------------------------------------
# headlines.py - a simple plugin to listen to headlines
# -----------------------------------------------------------------------
# $Id$
#
# Notes: 
# Todo: 
# activate:
# plugin.activate('headlines', level=45)
# HEADLINES_LOCATIONS = [ ("Advogato", "http://advogato.org/rss/articles.xml"),
#  ("Dictionary.com Word of the Day", "http://www.dictionary.com/wordoftheday/wotd.rss"),
#  ("DVD Review", "http://www.dvdreview.com/rss/newschannel.rss") ]
#
# for a full list of tested sites see Docs/plugins/headlines.txt
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2003/08/30 15:23:39  mikeruelle
# RDF headlines plugin. does pretty much anysite listed in evolution's summary section
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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

#python modules
import os, string, time

# rdf modules
from xml.dom.ext.reader import Sax2
import urllib
import cPickle

#freevo modules
import config, menu, rc, plugin, skin

from item import Item

#get the sinfletons so we can add our menu and get skin info
skin = skin.get_singleton()
menuwidget = menu.get_singleton()

TRUE = 1
FALSE = 0
#check every 20 minutes
MAX_HEADLINE_AGE = 1200

class HeadlinesSiteItem(Item):
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.url = ''
        self.location_index = None


    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.getheadlines , 'See Sites Headlines' ) ]
        return items
    
    def getsiteheadlines(self):
        headlines = []
        pfile = os.path.join(config.FREEVO_CACHEDIR, 'headlines-%i' % self.location_index)
        if (os.path.isfile(pfile) == 0 or \
            (abs(time.time() - os.path.getmtime(pfile)) > MAX_HEADLINE_AGE)):
            #print 'Fresh Headlines'
            headlines = self.fetchheadlinesfromurl()
        else:
            #print 'Cache Headlines'
            try:
                headlines = cPickle.load(open(pfile,'rb'))
            except:
                 print 'HEADLINES ERROR: could not read %s' % pfile
                 return []
        return headlines

    def fetchheadlinesfromurl(self):
        headlines = []
        # create Reader object
        reader = Sax2.Reader()
                                                                                                                    
        # parse the document
        try:
            myfile=urllib.urlopen(self.url)
            doc = reader.fromStream(myfile)
            items = doc.getElementsByTagName('item')
            for item in items:
                #print item
                if item.hasChildNodes():
                    for c in item.childNodes:
                        if c.localName == 'title':
                            headlines += [ '%s' % c.firstChild.data ]
        except:
            #unreachable or url error
            print 'HEADLINES ERROR: could not open %s' % self.url
            pass

        #write the file
        if len(headlines) > 0:
            pfile = os.path.join(config.FREEVO_CACHEDIR, 'headlines-%i' % self.location_index)
            try:
                cPickle.dump(headlines, open(pfile,'wb'))
            except:
                print 'HEADLINES ERROR: could not write %s' % pfile
                pass
        return headlines

    def getheadlines(self, arg=None, menuw=None):
        headlines = [] 
        rawheadlines = []
        rawheadlines = self.getsiteheadlines()
        for title in rawheadlines:
            headlines += [ menu.MenuItem('%s' % title, menuwidget.goto_prev_page, 0) ]

        if (len(headlines) == 0):
            headlines += [menu.MenuItem('No Headlines found', menuwidget.goto_prev_page, 0)]

        headlines_menu = menu.Menu('Headlines', headlines)
        rc.app(None)
        menuwidget.pushmenu(headlines_menu)
        menuwidget.refresh()

# this is the item for the main menu and creates the list
# of Headlines Sites in a submenu.
class HeadlinesMainMenuItem(Item):

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.create_locations_menu , 'Headlines Sites' ) ]
        return items
 
    def create_locations_menu(self, arg=None, menuw=None):
        headlines_sites = []
        for location in config.HEADLINES_LOCATIONS:
            headlines_site_item = HeadlinesSiteItem(self)
            headlines_site_item.name = location[0]
            headlines_site_item.url = location[1]
            headlines_site_item.location_index = config.HEADLINES_LOCATIONS.index(location)
            headlines_sites += [ headlines_site_item ]
        if (len(headlines_sites) == 0):
            headlines_sites += [menu.MenuItem('No Headlines Sites found', menuwidget.goto_prev_page, 0)]
        headlines_site_menu = menu.Menu('Headlines Sites', headlines_sites)
        rc.app(None)
        menuwidget.pushmenu(headlines_site_menu)
        menuwidget.refresh()

# our plugin wrapper, just creates the main menu item and adds it.
class PluginInterface(plugin.MainMenuPlugin):

    # make an init func that creates the cache dir if it don't exist

    def items(self, parent):
        menu_items = skin.settings.mainmenu.items

        item = HeadlinesMainMenuItem()
        item.name = 'Headlines'
        if menu_items.has_key('headlines') and menu_items['headlines'].icon:
            item.icon = os.path.join(skin.settings.icon_dir, menu_items['headlines'].icon)
        if menu_items.has_key('headlines') and menu_items['headlines'].image:
            item.image = menu_items['headlines'].image

        item.parent = parent
        return [ item ]


