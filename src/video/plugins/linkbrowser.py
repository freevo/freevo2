#if 0 /*
# -----------------------------------------------------------------------
# webradio.py - webradio plugin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:       Proof-of-concept
#
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/09/20 17:02:49  dischi
# do not scan with mmpython
#
# Revision 1.1  2003/09/20 12:58:44  dischi
# small browser to get video from the web
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

import os
from xml.utils import qp_xml
import urllib, urllib2, urlparse
import sys
import re

import config
import plugin
import menu

from item import Item
from video.videoitem import VideoItem
from gui.AlertBox import AlertBox
from gui.PopupBox import PopupBox

class Link(Item):
    """
    An object of this class handles one link. The link can be followed
    and a submenu will be build with all the new links.
    """
    def __init__(self, name, url, parent):
        Item.__init__(self, parent)
        self.url = url
        self.url_name = name
        self.name = name
        self.counter = 1

    def actions(self):
        return [ ( self.cwd, 'Browse links' ) ]

    def sort(self):
        """
        Sort the links: first links deeper in the tree, second links
        from the same domain, last other urls. Urls referenced more than
        once will be sorted higher.
        """
        if self.url_name.find('http:') == 0:
            return 'c %3d%s' % (100 - self.counter, self.url_name)
        if self.url_name.find('/') == 0:
            return 'b %3d%s' % (100 - self.counter, self.url_name)
        return 'a %3d%s' % (100 - self.counter, self.url_name)
        
    def cwd(self, arg=None, menuw=None):
        # headers for urllib2
        txdata = None
        txheaders = {   
            'User-Agent': 'freevo %s (%s)' % (config.VERSION, sys.platform),
            'Accept-Language': 'en-us',
            }
        
        popup = PopupBox(text='Downloading link list...')
        popup.show()
        try:
            req = urllib2.Request(self.url, txdata, txheaders)
            response = urllib2.urlopen(req)
        except:
            popup.destroy()
            box = AlertBox(text=_('Failed to download %s' % self.url))
            box.show()
            return

        # normalize the text so that it can be searched
        all = ''
        for line in response.read().split('\n'):
            all += line + ' '
        all = all.replace('\r', '').replace('\t', ' ')

        # find names for links (text between <a>)
        name_map = {}
        m = re.compile('href="([^"]*)">([^<]*)</a>', re.I).findall(all)
        if m:
            for url, title in m:
                while title.find('  ') > 0:
                    title = title.replace('  ', ' ')
                while title and not title[0].isalnum():
                    title = title[1:]
                title.lstrip().rstrip()
                name_map[url] = title

        # now search for links
        links  = []

        m = re.compile('href="(.*?)"', re.I).findall(all)
        if m:
            for url in m:
                title = ''
                if name_map.has_key(url):
                    title = name_map[url]
                        
                if url.find('mailto:') > 0 or url.find('.css') > 0:
                    continue
                
                if url.find('javascript:') == 0:
                    x = url[url.find('(')+1:url.rfind(')')]
                    if x and x[0] in ('\'', '"') and x[-1] in ('\'', '"'):
                        url = x[1:-1]

                if url.find('javascript:') >= 0:
                    continue
                
                # create the correct url
                name = url
                if not url.find('http://') == 0:
                    if url.find('/') == 0:
                        url = response.geturl()[:response.geturl()[8:].find('/')+8] + url
                    else:
                        url = response.geturl()[:response.geturl().rfind('/')+1] + url

                # search for duplicate links
                for l in links:
                    if l.url_name == name and l.url == url:
                        l.counter += 1
                        break

                # add new it
                else:
                    links.append(Link(name, url, self))
                    if title:
                        links[-1].name = title
                    else:
                        links[-1].name = 'url: %s' % links[-1].name
                    
        # sort all links
        links.sort(lambda l, o: cmp(l.sort().upper(),
                                    o.sort().upper()))

        # add part of the url to the name in case a title is used for
        # more than one item
        for l in links:
            for o in links:
                if l.name == o.name and l.name.find('(') == -1 and not l == o:
                    # duplicate found, get last part of the url
                    url = l.url[l.url.rfind('/')+1:]
                    if not url:
                        url = l.url[l.url[:-1].rfind('/')+1:]
                    if url:
                        l.name = '%s (%s)' % (l.name, url)
                    # same for the other
                    url = o.url[o.url.rfind('/')+1:]
                    if not url:
                        url = o.url[o.url[:-1].rfind('/')+1:]
                    if url:
                        o.name = '%s (%s)' % (o.name, url)
                    
        # now search for movies
        movies = []
        m = re.compile('"(http.[^"]*.(mov|avi|mpg|asf))"', re.I).findall(all)
        if m:
            murl = []
            for url in m:
                if not url[0] in murl:
                    murl.append(url[0])
            for url in murl:
                movies.append(VideoItem(url, self, parse=False))
                movies[-1].name = 'Video: ' + url[url.rfind('/')+1:]

        # all done
        popup.destroy()
        if links or movies:
            menuw.pushmenu(menu.Menu(self.name, movies + links))

            
class LinkList(Item):
    """
    The main menu item with all links from LINKBROWSER_URLS
    """
    def __init__(self, parent):
        Item.__init__(self, parent)
        self.name = 'LinkBrowser'
        self.type = 'browser'
        
    def actions(self):
        return [ ( self.cwd, 'Browse link list' ) ]

    def cwd(self, arg=None, menuw=None):
        items = []
        for name, url in config.LINKBROWSER_URLS:
            items.append(Link(name, url, self))
        menuw.pushmenu(menu.Menu('Link List', items))


class PluginInterface(plugin.MainMenuPlugin):
    """
    Browse links to find video files

    This plugin makes it possible to play video files from the net. You can
    specify a list of urls to be browsable. Each site will be parsed for more
    links and video files. 

    You need to set LINKBROWSER_URLS in local.conf.py. It's a list of urls
    with a descriptions:

    LINKBROWSER_URLS = (('name of the link', 'url'),
                        ('second link', 'second url'))

    activate this plugin with plugin.activate('video.linkbrowser')
    """
    def config(self):
        return [('LINKBROWSER_URLS', (), 'link list for the browser')]
            
    def items(self, parent):
        return [ LinkList(parent) ]
