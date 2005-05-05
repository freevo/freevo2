# -*- coding: iso-8859-1 -*-
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
# Revision 1.26  2005/05/05 17:33:59  dischi
# adjust to new gui submodule imports
#
# Revision 1.25  2005/01/09 17:35:53  dischi
# make headlines work again (thanks to Eric Bus)
#
# Revision 1.24  2005/01/08 15:09:26  dischi
# replace read_pickle and save_pickle with util.cache functions
#
# Revision 1.23  2004/10/06 18:59:52  dischi
# remove import rc
#
# Revision 1.22  2004/08/05 17:39:17  dischi
# deactivate
#
# Revision 1.21  2004/08/01 10:49:47  dischi
# deactivate plugin
#
# Revision 1.20  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.19  2004/07/25 19:47:39  dischi
# use application and not rc.app
#
# Revision 1.18  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
# Revision 1.17  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.16  2004/06/21 12:21:00  outlyer
# Ouch... there isn't a <bt> tag, but supporting the <br> tag would be a
# good idea ;) Ditto for the 'XHTML' version, <br/>
#
# Works properly now.
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


#python modules
import os, time, stat, re, copy

# rdf modules
from xml.dom.ext.reader import Sax2
import urllib

#freevo modules
import config, menu, plugin, util
import gui
import gui.areas
from item import Item

from mainmenu import MainMenuItem
from application import MenuApplication

import logging
log = logging.getLogger()


class PluginInterface(plugin.MainMenuPlugin):
    """
    A plugin to list headlines from an XML (RSS) feed.

    To activate, put the following lines in local_conf.py:

    plugin.activate('headlines', level=45) 
    HEADLINES_LOCATIONS = [
          ('Advogato', 'http://advogato.org/rss/articles.xml'), 
          ('DVD Review', 'http://www.dvdreview.com/rss/newschannel.rss') ] 

    For a full list of tested sites, see 'Docs/plugins/headlines.txt'. 
    """
    # make an init func that creates the cache dir if it don't exist
    def __init__(self):
        if not hasattr(config, 'MAX_HEADLINE_AGE'):
            #check every 30 minutes
            config.MAX_HEADLINE_AGE = 1800
    
        if not hasattr(config, 'HEADLINES_LOCATIONS'):
            self.reason = 'HEADLINES_LOCATIONS not defined'
            return
            
        plugin.MainMenuPlugin.__init__(self)


#
# TODO: Is this used at all?
#
#    def config(self):
#        return [('HEADLINES_LOCATIONS',
#                 [ ("DVD Review", "http://www.dvdreview.com/rss/newschannel.rss"),
#                   ("Freshmeat", "http://freshmeat.net/backend/fm.rdf") ],
#                 'where to get the news')]


    def items(self, parent):
        return [ HeadlinesMainMenuItem(parent) ]


class ShowHeadlineDetails(MenuApplication):
    """
    Screen to show the details of the headline items
    """
    def __init__(self, (item,menuw)):
        self.item = item
        MenuApplication.__init__(self, 'headlines', 'menu', False)
        
        
    def start(self, parent):
        self.engine = gui.areas.Handler('headlines', ('screen','title','info'))
        self.parent = parent
        
        return True


    def show(self):
        self.engine.draw(self)
        MenuApplication.show(self)
        

    def eventhandler(self, event, menuw=None):
        if MenuApplication.eventhandler(self, event):
            return True
            
        return False
        
        
    def __getitem__(self, key):
        if key == 'description':
            return self.item.description
        
        return None
        

class HeadlinesSiteItem(Item):
    """
    Item for the menu for one rss feed
    """
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.url = ''
        self.cachedir = '%s/headlines' % config.FREEVO_CACHEDIR
        if not os.path.isdir(self.cachedir):
            os.mkdir(self.cachedir,
                     stat.S_IMODE(os.stat(config.FREEVO_CACHEDIR)[stat.ST_MODE]))
        self.location_index = None
        

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.get_headlines , _('Show Sites Headlines') ) ]
        return items

    
    def get_site_headlines(self):
        headlines = []
        pfile = os.path.join(self.cachedir, 'headlines-%i' % self.location_index)
        if (os.path.isfile(pfile) == 0 or \
            (abs(time.time() - os.path.getmtime(pfile)) > config.MAX_HEADLINE_AGE)):
            log.info('Fresh Headlines')
            headlines = self.fetch_headlines_from_url()
        else:
            log.info('Cache Headlines')
            headlines = util.cache.load(pfile)
        return headlines


    def parse_rss_feed(self, doc, headlines):
        """
        parses a rss 0.9, 1.0 or 2.0 feed
        """
        items = doc.getElementsByTagName('item')
        for item in items:
            title = ''
            link  = ''
            description = ''
                
            if item.hasChildNodes():
                for c in item.childNodes:
                    if c.localName == 'title':
                        title = c.firstChild.data
                    if c.localName == 'link':
                        link = c.firstChild.data
                    if c.localName == 'description':
                        description = c.firstChild.data

            if title:
                headlines.append((title, link, description))
    
    
    def parse_atom_feed(self, doc, headlines):
        """
        parses an atom feed
        """
        items = doc.getElementsByTagName('entry')
        for item in items:
            title = ''
            link  = ''
            description = ''
                
            if item.hasChildNodes():
                for c in item.childNodes:
                    if c.localName == 'title':
                        title = c.firstChild.data
                    if c.localName == 'link':
                        link = c.getAttribute('href')
                    if c.localName == 'summary':
                        description = c.firstChild.data

            if title:
                headlines.append((title, link, description))


    def fetch_headlines_from_url(self):
        headlines = []

        # create Reader object
        reader = Sax2.Reader()

        popup = gui.PopupBox(text=_('Fetching headlines...'))
        popup.show()

        # parse the document
        try:
            myfile = urllib.urlopen(self.url)
            doc = reader.fromStream(myfile)
            
            rootName = doc.documentElement.tagName
            if rootName == 'rss':
                self.parse_rss_feed(doc, headlines)
            elif rootName == 'feed':
                self.parse_atom_feed(doc, headlines)
            else:
                popup.destroy()
                gui.AlertBox(text=_('Unsupported RSS feed')).show()
                log.error('unsupported RSS feed with rootNode %s' % rootName)
                return None

        except:
            # unreachable or url error
            popup.destroy()
            gui.AlertBox(text=_('Freevo could not fetch the requested headlines')).show()
            log.error('could not open %s' % self.url)
            return None

        # write the file
        if headlines and len(headlines) > 0:
            pfile = os.path.join(self.cachedir, 'headlines-%i' % self.location_index)
            util.cache.save(pfile, headlines)

        popup.destroy()
        return headlines


    def show_details(self, arg=None, menuw=None):
        det = ShowHeadlineDetails(arg)
        if det.start(self):
            menuw.pushmenu(det)
            menuw.refresh()


    def get_headlines(self, arg=None, menuw=None):
        headlines = [] 
        rawheadlines = []
        rawheadlines = self.get_site_headlines()

        # only show this menu when we have headlines
        if rawheadlines == None:
            return
        
        for title, link, description in rawheadlines:
            mi = menu.MenuItem(title, self.show_details)
            mi.arg = (mi, menuw)
            mi.link = link

            description = description.replace('\n\n', '&#xxx;').replace('\n', ' ').\
                          replace('&#xxx;', '\n')
            description = description.replace('<p>', '\n').replace('<br>', '\n')
            description = description.replace('<p>', '\n').replace('<br/>', '\n')
            description = description + '\n \n \nLink: ' + link
#            description = util.htmlenties2txt(description)

            mi.description = re.sub('<.*?>', '', description)

            headlines.append(mi)

    	if len(headlines) == 0:
            headlines += [menu.MenuItem(_('No Headlines found'), menuw.back_one_menu, 0)]

        headlines_menu = menu.Menu(_('Headlines'), headlines)
        menuw.pushmenu(headlines_menu)
        menuw.refresh()


class HeadlinesMainMenuItem(MainMenuItem):
    """
    This is the item for the main menu and creates the list
    of Headlines Sites in a submenu.
    """
    def __init__(self, parent):
        MainMenuItem.__init__( self, _('Headlines'), type='main',
                               parent=parent, skin_type='headlines')


    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.create_locations_menu , _('Headlines Sites' )) ]
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
            headlines_sites += [menu.MenuItem(_('No Headlines Sites found'),
                                              menuw.goto_prev_page, 0)]
                                              
        headlines_site_menu = menu.Menu(_('Headlines Sites'), headlines_sites)
        menuw.pushmenu(headlines_site_menu)
        menuw.refresh()


