# -*- coding: iso-8859-1 -*-
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
# Revision 1.8  2004/07/22 21:21:50  dischi
# small fixes to fit the new gui code
#
# Revision 1.7  2004/07/10 12:33:43  dischi
# header cleanup
#
# Revision 1.6  2003/11/16 17:41:05  dischi
# i18n patch from David Sagnol
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
from xml.utils import qp_xml
import urllib, urllib2, urlparse
import sys
import re

import config
import plugin
import menu
import util

from item import Item
from video.videoitem import VideoItem
from gui import AlertBox
from gui import PopupBox

class Link(Item):
    """
    An object of this class handles one link. The link can be followed
    and a submenu will be build with all the new links.
    """
    def __init__(self, name, url, blacklist_regexp, autoplay, all_links, parent):
        Item.__init__(self, parent)
        self.url = url
        self.url_name = name
        self.name = name
        self.blacklist_regexp = blacklist_regexp
        self.autoplay = autoplay
        self.counter = 1
        self.all_links = all_links
        self.type = 'linkbrowser'

    def actions(self):
        """
        list of possible actions for a Link
        """
        p = [ ( self.play,           _('Browse links (autoplay)') ), 
              ( self.play_max_cache, _('Browse links (autoplay, maximum caching)') ) ]
        b = [ ( self.cwd,            _('Browse links') ) ]

        if self.autoplay:
            return p + b
        return b + p
    

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

        
    def make_complete_url(self, base, url):
        """
        Make a complete url from given url and the base. Return None
        for bad urls like javascript and mailto.
        """
        if url.find('mailto:') > 0 or url.find('.css') > 0:
            return None
                
        if url.find('javascript:') == 0:
            x = url[url.find('(')+1:url.rfind(')')]
            if x and x[0] in ('\'', '"') and x[-1] in ('\'', '"'):
                url = x[1:-1]

        if url.find('javascript:') >= 0:
            return None
                
        # create the correct url
        if not url.find('http://') == 0:
            if url.find('/') == 0:
                url = base[:base[8:].find('/')+8] + url
            else:
                url = base[:base.rfind('/')+1] + url
        return url

    
    def play(self, arg=None, menuw=None):
        """
        download the link and activate autoplay
        """
        self.cwd(arg='autoplay', menuw=menuw)


    def play_max_cache(self, arg=None, menuw=None):
        """
        download the link and activate autoplay with maximum caching
        """
        self.cwd(arg='autoplay_max', menuw=menuw)

        
    def cwd(self, arg=None, menuw=None):
        """
        Download the url and create a menu with more links
        """
        txdata = None
        txheaders = {   
            'User-Agent': 'freevo %s (%s)' % (config.VERSION, sys.platform),
            'Accept-Language': 'en-us',
            }
        
        popup = PopupBox(text=_('Downloading link list...'))
        popup.show()
        try:
            req = urllib2.Request(self.url, txdata, txheaders)
            response = urllib2.urlopen(req)
        except:
            popup.destroy()
            box = AlertBox(text=_('Failed to download %s') % self.url)
            box.show()
            return

        # base for this url
        self.base = response.geturl()[:response.geturl().rfind('/')+1]
        
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
                title = util.htmlenties2txt(title.lstrip().rstrip())
                name_map[url] = title


        # now search for links, normal links and movie links together
        all_urls = []
        movie_regexp = re.compile('.*(mov|avi|mpg|asf)$', re.I)
        for m in (re.compile('href="(.*?)"', re.I).findall(all),
                  re.compile('"(http.[^"]*.(mov|avi|mpg|asf))"', re.I).findall(all)):
            if m:
                for url in m:
                    if isinstance(url, tuple):
                        url = url[0]
                    all_urls.append(url)


        # now split all_urls into link_urls (more links) and
        # movie_urls (video)
        link_urls  = []
        movie_urls = []

        if all_urls:
            for url in all_urls:
                long_url  = self.make_complete_url(response.geturl(), url)

                # bad url?
                if not long_url:
                    continue
                
                # find a title
                title = url
                if name_map.has_key(url):
                    title = name_map[url]
                else:
                    title = title.replace('.html', '').replace('.php', '')

                # remove blacklisted urls
                for b in self.blacklist_regexp:
                    if b(long_url):
                        break
                else:
                    # movie or link?
                    if movie_regexp.match(long_url):
                        movie_urls.append((long_url, url, title))
                    else:
                        link_urls.append((long_url, url, title))



        items  = []

        # add all link urls
        if link_urls:
            for long, short, title in link_urls:
                # should all links be displayed?
                if (not self.all_links) and long.find(self.base) != 0:
                    continue
                # don't display self
                if long == self.url:
                    continue
                # search for duplicate links
                for l in items:
                    if l.url == long:
                        # increase counter, this link seems to be
                        # important
                        l.counter += 1
                        break

                else:
                    # add link as new new
                    l = Link(title, long, self.blacklist_regexp, self.autoplay,
                             self.all_links, self)
                    l.url_name = short
                    l.image = None
                    items.append(l)
                    

        # sort all items
        items.sort(lambda l, o: cmp(l.sort().upper(),
                                    o.sort().upper()))

        # add part of the url to the name in case a title is used for
        # more than one item
        for l in items:
            for o in items:
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
        if movie_urls:
            for long, short, title in movie_urls:
                # search for duplicate links
                for l in movies:
                    if l.filename == long:
                        break
                else:
                    movies.append(VideoItem(long, self, parse=False))
                    if title.find('/') != -1:
                        title = 'Video: ' + long[long.rfind('/')+1:]
                    movies[-1].name = title

        # all done
        popup.destroy()
        if len(movies) == 1 and arg=='autoplay':
            movies[0].play(menuw=menuw)
        elif len(movies) == 1 and arg=='autoplay_max':
            movies[0].play_max_cache(menuw=menuw)
        elif items or movies:
            menuw.pushmenu(menu.Menu(self.name, movies + items))

            

class PluginInterface(plugin.MainMenuPlugin):
    """
    Browse links to find video files

    This plugin makes it possible to play video files from the net. The
    plugin needs to be activated with specific informations about the
    link to be shown. You can activate the plugin more than once with a
    different url.

    Options: name, url, image (optional), blacklist_regexp (optional),
             autoplay (optional), all_links (optional)

             name:  the name the link browser should have in the menu
             url:   the url to be parsed
             image: image for the menu (default: None)

             blacklist_regexp: a list of regular expressions for links to
             be ignored. The default value is []. Notice: the regexp will
             be used witg match() in python, so: 'foo' will only match 'foo',
             not http://www.foo.com. Use '.*foo.*' for that.

             autoplay: if only one video is found (besides some links),
             play it and don't show the links. It's still possible to
             browse the link list by pressing ENTER. Default is False.

             all_links: if True, all links (except blacklisted) will be shown,
             if False, only links deeper to the current one will be shown. E.g.
             when viewing www.foo.com/bar, www.bar.com and www.foo.com/bar will
             be blocked.
             
    activate this plugin with
    plugin.activate('video.linkbrowser', args=('name', 'url') or
    plugin.activate('video.linkbrowser', args=('name', 'url', image', ...)
    """

    def __init__(self, name, url, image=None, blacklist_regexp = [],
                 autoplay = False, all_links = True):
        plugin.MainMenuPlugin.__init__(self)
        self.name = name
        self.url  = url
        self.image = image
        self.blacklist_regexp = []
        self.autoplay = autoplay
        self.all_links = all_links
        self.type = 'linkbrowser'
        for b in blacklist_regexp:
            self.blacklist_regexp.append(re.compile(b).match)
        
    def items(self, parent):
        l = Link(self.name, self.url, self.blacklist_regexp, self.autoplay,
                 self.all_links, parent)
        l.image = self.image
        return [ l ]
