# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# helpers/fxdimdb.py - class and helpers for fxd/imdb generation
# -----------------------------------------------------------------------
# $Id$
#
# Notes: see http://pintje.servebeer.com/fxdimdb.html for documentatio,
# Todo: 
# - add support making fxds without imdb (or documenting it)
# - webradio support?
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.7  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.6  2004/06/20 13:06:20  dischi
# move freevo-rebuild-database to cache dir
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


# python has no data hiding, but this is the intended use...
# subroutines completly in lowercase are regarded as more "private" functions
# subRoutines are regarded as public

#some data
__author__ = "den_RDC (rdc@kokosnoot.com)"
__version__ = "Revision 0.1"
__copyright__ = "Copyright (C) 2003 den_RDC"
__license__ = "GPL"

#Module Imports
import re
import urllib, urllib2, urlparse
import sys
import codecs
import os

import config 
import util

from mmpython.disc.discinfo import cdrom_disc_id
#Constants

freevo_version = '1.3.4'

imdb_title_list = '/tmp/imdb-movies.list'
imdb_title_list_url = 'ftp://ftp.funet.fi/pub/mirrors/ftp.imdb.com/pub/movies.list.gz'
imdb_titles = None
imdb_info_tags = ('year', 'genre', 'tagline', 'plot', 'rating', 'runtime');


# headers for urllib2
txdata = None
txheaders = {   
    'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform),
    'Accept-Language': 'en-us',
}

#Begin class

class FxdImdb:
    """Class for creating fxd files and fetching imdb information"""
    
    def __init__(self):
        """Initialise class instance"""
    
        # these are considered as private variables - don't mess with them unless
        # no other choise is given
        # fyi, the other choice always exists : add a subroutine or ask :)
        
        self.imdb_id_list = []
        self.imdb_id = None
        self.isdiscset = False
        self.title = ''
        self.info = {}
        
        self.image = None # full path image filename
        self.image_urls = [] # possible image url list
        self.image_url = None # final image url 
        
        self.fxdfile = None # filename, full path, WITHOUT extension

        self.append = False
        self.device = None
        self.regexp = None
        self.mpl_global_opt = None
        self.media_id = None
        self.file_opts = []
        self.video = []
        self.variant = []
        self.parts = []
        self.var_mplopt = []
        self.var_names = []
        
        #initialize self.info    
        for t in imdb_info_tags:
            self.info[t] = ""
            
        #image_url_handler stuff
        self.image_url_handler = {}
        self.image_url_handler['www.impawards.com'] = self.impawards
        
    
    
    def searchImdb(self, name):
        """name (string), returns id list
        Search for name and returns an id list with tuples:
            (id , name, year, type)"""

        url = 'http://us.imdb.com/Tsearch?title=%s&restrict=Movies+and+TV' % \
              urllib.quote(name)
        req = urllib2.Request(url, txdata, txheaders)
        searchstring = name
        
        try:
            response = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            raise FxdImdb_Net_Error("IMDB unreachable : " + error) 
            return None
            
        regexp_get_imdb_id = re.compile(r'''
        http://.*imdb\.com/
        (?:Title\?|title/tt) # ( old style | new style )
        (?P<id>\d+)          # imdb id
        ''', re.VERBOSE)

        m = re.match(regexp_get_imdb_id, response.geturl())
        if m:
            data = self.parsedata(response)
            #print 'data[0]: ' + data[0]
            self.imdb_id_list = [ ( m.group('id'),
                                    data[0], 
                                    data[1]['year'],
                                    "Movie/TV-Movie") ]
            return self.imdb_id_list
        
        regexp_type  = re.compile(r'''
        <H2><A[ ]NAME=.*?>
        (?P<type>.*?)     # Most popular searches/Movies/TV-Movies/Video Games etc.
        </A></H2>
        ''', re.VERBOSE)

        regexp_imdb_list_entry = re.compile(r'''
        <A[ ]HREF="/(?:Title\?|title/tt)     # match both old and new style
        (?P<id>      \d+)/">                  # imdb id
        (?P<title>   .*?)\s*                  # imdb movie title
        \(
        (?P<year>    \d{4}.*?)                # year and possibly /I, /II etc.
        \)</A>
        ''', re.VERBOSE | re.IGNORECASE)

        type = ''
        for line in response.read().split("\n"):
            m = regexp_type.match(line)
            if m:
                type = m.group('type')
                # delete plural s
                if type in ('Movies', 'TV-Movies'):
                    type = type[:-1]
    
            m = regexp_imdb_list_entry.search(line)

            if m and not type == 'Video Games':
                id   = m.group('id')
                name = m.group('title')
                year = m.group('year')
    
                # delete " before and after name
                if name[0] == '"' and name [-1] == '"':
                    name=name[1:-1]
    
                # only add entries that hasn't been added before
                for i in self.imdb_id_list:
                    if i[0] == id:
                        break
                else:
                    self.imdb_id_list += [ ( id, name, year, type ) ]

        response.close()
        if len(self.imdb_id_list) > 20:
            # too much results, check if there are stupid results in the
            # list
            words = []
            
            # make a list of all words (no numbers) in the search string
            for p in re.split('[\._ -]', searchstring):
                if p and not p[0] in '0123456789':
                    words.append(p)

            # at least one word has to be in the result
            new_list = []
            for result in self.imdb_id_list:
                appended = False
                for search_word in words:
                    if appended == False and \
                           result[1].lower().find(search_word.lower()) != -1:
                        new_list.append(result)
                        appended = True
            self.imdb_id_list = new_list
        return self.imdb_id_list
    
    
    def setImdbId(self, id):
        """id (number)
        Set an imdb_id number for object, and fetch data"""
        self.imdb_id = id
        
        url = 'http://us.imdb.com/Title?%s' % id
        req = urllib2.Request(url, txdata, txheaders)
        
        try:
            idpage = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            raise FxdImdb_Net_Error("IMDB unreachable" + error)
            return None
    
        self.parsedata(idpage, id)
        idpage.close()

    
    def setFxdFile(self, fxdfilename = None, overwrite = False):
        """
        fxdfilename (string, full path)
        Set fxd file to write to, may be omitted, may be an existing file
        (data will be added) unless overwrite = True
        """
        
        if fxdfilename: 
            if vfs.splitext(fxdfilename)[1] == '.fxd':
                self.fxdfile = vfs.splitext(fxdfilename)[0]
            else: self.fxdfile = fxdfilename
        
        else:
            if self.isdiscset == True:
                self.fxdfile = vfs.join(config.OVERLAY_DIR, 'disc-set',
                                        self.getmedia_id(self.device))
            else:
                self.fxdfile = vfs.splitext(file)[0]
        
        if overwrite == False:
            try:
                vfs.open(self.fxdfile + '.fxd')
                self.append = True
            except: 
                pass
        else:
            self.append = False

        # XXX: add this back in without using parseMovieFile
        # if self.append == True and \
        #    parseMovieFile(self.fxdfile + '.fxd', None, []) == []:
        #     raise FxdImdb_XML_Error("FXD file to be updated is invalid, please correct it.")

        if not vfs.isdir(vfs.dirname(self.fxdfile)):
            if vfs.dirname(self.fxdfile):
                os.makedirs(vfs.dirname(self.fxdfile))
            
    
    def setVideo(self, *videos, **mplayer_opt):
        """
        videos (tuple (type, id-ref, device, mplayer-opts, file/param) (multiple allowed), 
        global_mplayer_opts
        Set media file(s) for fxd
        """
        if self.isdiscset == True:
            raise FxdImdb_XML_Error("<disc-set> already used, can't use both "+
                                    "<movie> and <disc-set>")
        
        if videos:
            for video in videos:
                self.video += [ video ]
        if mplayer_opt and 'mplayer_opt' in mpl_global_opt:
            self.mpl_global_opt = mplayer_opt['mplayer_opt']
        
    def setVariants(self, *parts, **mplayer_opt):
        """
        variants/parts (tuple (name, ref, mpl_opts, sub, s_dev, audio, a_dev)),
        var_mplayer_opts
        Set Variants & parts
        """
        if self.isdiscset == True:
            raise FxdImdb_XML_Error("<disc-set> already used, can't use both "+
                                    "<movie> and <disc-set>")
 
        if mplayer_opt and 'mplayer_opt' in mpl_global_opt:
            self.varmpl_opt = (mplayer_opt['mplayer_opt'])
        for part in parts:
            self.variant += [ part ]
        
    
    def writeFxd(self):
        """Write fxd file"""
        #if fxdfile is empty, set it yourself
        if not self.fxdfile:
            self.setFxdFile()
        
        try:
            #should we add to an existing file?
            if self.append == True :
                if self.isdiscset == True:
                    self.update_discset()
                else: self.update_movie()
            else:
                #fetch images
                self.fetch_image()
                #should we write a disc-set ?
                if self.isdiscset == True:
                    self.write_discset()
                else:
                    self.write_movie()

            #check fxd 
            # XXX: add this back in without using parseMovieFile
            # if parseMovieFile(self.fxdfile + '.fxd', None, []) == []:
            #     raise FxdImdb_XML_Error("""FXD file generated is invalid, please "+
            #                             "post bugreport, tracebacks and fxd file.""")

        except (IOError, FxdImdb_IO_Error), error:
            raise FxdImdb_IO_Error('error saving the file: %s' % str(error))
            
    
    def setDiscset(self, device, regexp, *file_opts, **mpl_global_opt):
        """
        device (string), regexp (string), file_opts (tuple (mplayer-opts,file)),
        mpl_global_opt (string)
        Set media is dvd/vcd,
        """
        if len(self.video) != 0 or len(self.variant) != 0:
            raise FxdImdb_XML_Error("<movie> already used, can't use both "+
                                    "<movie> and <disc-set>")
        
        self.isdiscset = True
        if (not device and not regexp) or (device and regexp):
            raise FxdImdb_XML_Error("Can't use both media-id and regexp")
            
        self.device = device
        self.regexp = regexp
        
        for opts in file_opts:
            self.file_opts += [ opts ]
            
        if mpl_global_opt and 'mplayer_opt' in mpl_global_opt: 
            self.mpl_global_opt = (mpl_global_opt['mplayer_opt'])
            
    
    def isDiscset(self):
        """Check if fxd file describes a disc-set, returns 1 for true, 0 for false
        None for invalid file"""
        try:
            file = vfs.open(self.fxdfile + '.fxd')
        except IOError:
            return None
            
        content = file.read()
        file.close()
        if content.find('</disc-set>') != -1: return 1
        return 0

        
    def guessImdb(self, filename, label=False):
        """Guess possible imdb movies from filename. Same return as searchImdb"""

        name = filename
        
        name  = vfs.basename(vfs.splitext(name)[0])
        name  = re.sub('([a-z])([A-Z])', point_maker, name)
        name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
        name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())
        name  = re.sub(',', ' ', name)

        if label == True:
            for r in config.IMDB_REMOVE_FROM_LABEL:
                name  = re.sub(r, '', name)
                
        parts = re.split('[\._ -]', name)
        name = ''
        for p in parts:
            if not p.lower() in config.IMDB_REMOVE_FROM_SEARCHSTRING and \
                   not re.search('[^0-9A-Za-z]', p):
                # originally: not re.search(p, '[A-Za-z]'):
                # not sure what's meant with that
                name += '%s ' % p
        return self.searchImdb(name)

        
#------ private functions below .....

    def write_discset(self):
        """Write a <disc-set> to a fresh file"""        
    
        try:
            i = vfs.codecs_open( (self.fxdfile + '.fxd') , 'wb', encoding='utf-8')
        except IOError, error:
            raise FxdImdb_IO_Error("Writing FXD file failed : " + str(error))
            return 
    
        #header
        i.write("<?xml version=\"1.0\" ?>\n<freevo>\n")
        i.write("  <copyright>\n" +
                "    The information in this file are from the Internet " +
                "Movie Database (IMDb).\n" +
                "    Please visit http://www.imdb.com for more informations.\n")
        i.write("    <source url=\"http://www.imdb.com/Title?%s\"/>\n"  % self.imdb_id +
                "  </copyright>\n")
        #disc-set    
        i.write("  <disc-set title=\"%s\">\n" % self.str2XML(self.title))
        #disc
        i.write("    <disc")
        if self.device:
            i.write(" media-id=\"%s\"" % self.str2XML(self.getmedia_id(self.device)))
        elif self.regexp:
            i.write(" label-regexp=\"%s\"" % self.str2XML(self.regexp))
        if self.mpl_global_opt:
            i.write(" mplayer-options=\"%s\">" % self.str2XML(self.mpl_global_opt))
        else: i.write(">")
        #file-opts
        if self.file_opts:
            i.write("\n")
            for opts in self.file_opts:
                mplopts, fname = opts 
                i.write("      <file-opt mplayer-options=\"%s\">" % self.str2XML(mplopts))
                i.write("%s</file-opt>\n" % self.str2XML(fname))
            i.write("    </disc>\n")
        else: i.write("    </disc>\n")
        
        #image
        if self.image:
            i.write("    <cover-img source=\"%s\">" % self.str2XML(self.image_url))
            i.write("%s</cover-img>\n" % self.str2XML(self.image))
        #print info
        i.write(self.print_info())
        
        #close tags     
        i.write("  </disc-set>\n")    
        i.write("</freevo>\n")
    
        util.touch(os.path.join(config.FREEVO_CACHEDIR, 'freevo-rebuild-database'))

        
    def write_movie(self):
        """Write <movie> to fxd file"""
        
        try:
            i = vfs.codecs_open( (self.fxdfile + '.fxd') , 'w', encoding='utf-8')
        except IOError, error:
            raise FxdImdb_IO_Error("Writing FXD file failed : " + str(error))
            return 
        
        #header
        i.write("<?xml version=\"1.0\" ?>\n<freevo>\n")
        i.write("  <copyright>\n" +
                "    The information in this file are from the Internet " +
                "Movie Database (IMDb).\n" +
                "    Please visit http://www.imdb.com for more informations.\n")
        i.write("    <source url=\"http://www.imdb.com/Title?%s\"/>\n"  % self.imdb_id +
                "  </copyright>\n")
        # write movie
        i.write("  <movie title=\"%s\">\n" % self.str2XML(self.title))
        #image
        if self.image:
            i.write("    <cover-img source=\"%s\">" % self.str2XML(self.image_url))
            i.write("%s</cover-img>\n" % self.str2XML(self.image))
        #video
        if self.mpl_global_opt:
            i.write("    <video mplayer-options=\"%s\">\n" % \
                    self.str2XML(self.mpl_global_opt))
        else: i.write("    <video>\n")
        # videos
        i.write(self.print_video())
        i.write('    </video>\n')
        #variants <varinats !!
        if len(self.variant) != 0:
            i.write('    <variants>\n')
            i.write(self.print_variant())
            i.write('    </variants>\n')
        
        #info
        i.write(self.print_info())
        #close tags
        i.write('  </movie>\n')
        i.write('</freevo>\n')     
        
        util.touch(os.path.join(config.FREEVO_CACHEDIR, 'freevo-rebuild-database'))


        
    def update_movie(self):
        """Updates an existing file, adds exftra dvd|vcd|file and variant tags"""
        passedvid = False
        #read existing file in memory
        try:
            file = vfs.open(self.fxdfile + '.fxd')
        except IOError, error:
            raise FxdImdb_IO_Error("Updating FXD file failed : " + str(error))
            return
            
        content = file.read()
        file.close()
        
        if content.find('</video>') == -1:
            raise FxdImdb_XML_Error("FXD cannot be updated, doesn't contain <video> tag")

        regexp_variant_start = re.compile('.*<variants>.*', re.I)
        regexp_variant_end = re.compile(' *</variants>', re.I)
        regexp_video_end  = re.compile(' *</video>', re.I)
    
        file = vfs.open(self.fxdfile + '.fxd', 'w')
    

        for line in content.split('\n'):
            if passedvid == True and content.find('<variants>') == -1:
                #there is no variants tag
                if len(self.variant) != 0:
                    file.write('    <variants>\n')
                    file.write(self.print_variant())
                    file.write('    </variants>\n')
                file.write(line + '\n')
                passedvid = False
                
            elif regexp_video_end.match(line):
                if len(self.video) != 0:
                    file.write(self.print_video())
                file.write(line + '\n')
                passedvid = True
                
            elif regexp_variant_end.match(line):
                if len(self.variant) != 0:
                    file.write(self.print_variant())
                file.write(line + '\n')
                
            else: file.write(line + '\n')
            
        file.close()
        util.touch(os.path.join(config.FREEVO_CACHEDIR, 'freevo-rebuild-database'))


        
    def update_discset(self):
        """Updates an existing file, adds extra disc in discset"""
        
        #read existing file in memory
        try:
            file = vfs.open(self.fxdfile + '.fxd')
        except IOError, error:
            raise FxdImdb_IO_Error("Updating FXD file failed : " + str(error))
            return
            
        content = file.read()
        file.close()
        
        if content.find('</disc-set>') == -1:
            raise FxdImdb_XML_Error("FXD file cannot be updated, doesn't contain <disc-set>")
            
        regexp_discset_end  = re.compile(' *</disc-set>', re.I)
    
        file = vfs.open(self.fxdfile + '.fxd', 'w')
    
        for line in content.split('\n'):
                
            if regexp_discset_end.match(line):
                file.write("    <disc")
                if self.device:
                    file.write(" media-id=\"%s\"" % \
                               self.str2XML(self.getmedia_id(self.device)))
                elif self.regexp:
                    file.write(" label-regexp=\"%s\"" % self.str2XML(self.regexp))
                if self.mpl_global_opt:
                    file.write(" mplayer-options=\"%s\">" % self.str2XML(self.mpl_global_opt))
                else: file.write(">")
                #file-opts
                if self.file_opts:
                    file.write("\n")
                    for opts in self.file_opts:
                        mplopts, fname = opts 
                        file.write("      <file-opt mplayer-options=\"%s\">" % \
                                   self.str2XML(mplopts))
                        file.write("%s</file-opt>\n" % self.str2XML(fname))
                    file.write("    </disc>\n")
                else: file.write("    </disc>\n")
                file.write(line + '\n')
                
            else: file.write(line + '\n')
            
        file.close()
        util.touch(os.path.join(config.FREEVO_CACHEDIR, 'freevo-rebuild-database'))



    
    def parsedata(self, results, id=0):
        """results (imdb html page), imdb_id
        Returns tuple of (title, info(dict), image_urls)"""

        dvd = 0
        
        regexp_title   = re.compile('.*STRONG CLASS="title">(.*?)<', re.I)
        regexp_year    = re.compile('.*<A HREF="/Sections/Years/.*?([0-9]*)<', re.I)
        regexp_genre   = re.compile('.*href="/Sections/Genres(.*)$', re.I)
        regexp_tagline = re.compile('.*<B CLASS="ch">Tagline.*?</B>(.*?)<', re.I)
        regexp_plot1   = re.compile('.*<B CLASS="ch">Plot Outline.*?</B>(.*?)<', re.I)
        regexp_plot2   = re.compile('.*<B CLASS="ch">Plot Summary.*?</B>(.*?)<', re.I)
        regexp_rating  = re.compile('.*<B>([0-9\.]*)/10</B> (.[0-9,]* votes.?)', re.I)
        regexp_image   = re.compile('.*ALT="cover".*src="(http://.*?)"', re.I)
        regexp_runtime = re.compile('.*<b class="ch">Runtime', re.I)
        regexp_dvd     = re.compile('.*<a href="/DVD\?', re.I)
    
        regexp_dvd_image = re.compile('.*(http://images.amazon.com.*?ZZZZZ.*?)"')
        regexp_url   = re.compile('.*href="(http.*?)"', re.I)
    
        next_line_is = None
    
        for line in results.read().split("\n"):
            if next_line_is == 'runtime':
                next_line_is = None
                self.info['runtime'] = self.str2XML(line)
    
            if regexp_runtime.match(line):
                next_line_is = 'runtime'
                continue
    
            m = regexp_title.match(line)
            if m: self.title = self.str2XML(m.group(1))
    
            m = regexp_year.match(line)
            if m: self.info['year'] = m.group(1)
    
            m = regexp_genre.match(line)
            if m:
                for g in re.compile(' *</A>.*?> *', re.I).split(' </a>'+line+' > '):
                    if self.info['genre'] == "": self.info['genre'] = g
                    elif g != "" and g != "(more)": self.info['genre'] += " / "+ g
    
    
            m = regexp_tagline.match('%s<' % line)
            if m:
                self.info['tagline'] = self.str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])
    
            m = regexp_plot1.match('%s<' % line)
            if m: self.info['plot'] = self.str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])
    
            m = regexp_plot2.match('%s<' % line)
            if m: self.info['plot'] = self.str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])
    
            m = regexp_rating.match(line)
            if m: self.info['rating'] = m.group(1) + '/10 ' + m.group(2)
    
            m = regexp_dvd.match(line)
            if m: dvd = 1
    
            m = regexp_image.match(line)
            if m: self.image_urls += [ m.group(1) ]
    
    
        if not id:
            return (self.title, self.info, self.image_urls)
    
    
        if dvd:
            url = 'http://us.imdb.com/DVD?%s' % id
            req = urllib2.Request(url, txdata, txheaders)
            
            try:
                r = urllib2.urlopen(req)
                for line in r.read().split("\n"):
                    m = regexp_dvd_image.match(line)
                    if m: self.image_urls += [ m.group(1) ]
                r.close()
            except urllib2.HTTPError, error:
                pass
    
        #oldcode
        #if not self.image_url_handler:
        #    return #(title, info, image_urls)
    
        url = 'http://us.imdb.com/title/tt%s/posters' % id
        req = urllib2.Request(url, txdata, txheaders)
        try:
            r = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print error
            return (self.title, self.info, self.image_urls)

        data = r.read().replace('</a>', '\n').replace('</A>', '\n')
        for line in data.split('\n'):
            m = regexp_url.match(line)
            if m:
                url = urlparse.urlsplit(m.group(1))
                if url[0] == 'http' and self.image_url_handler.has_key(url[1]):
                    self.image_urls += self.image_url_handler[url[1]](url[1], url[2])
        
        r.close()
        return (self.title, self.info, self.image_urls)
    
    
    def impawards(self, host, path):
        """parser for posters from www.impawards.com. TODO: check for licences
        of each poster and add all posters"""
        
        path = '%s/posters/%s.jpg' % (path[:path.rfind('/')], \
                                      path[path.rfind('/')+1:path.rfind('.')])
        return [ 'http://%s%s' % (host, path) ]
    
    
    def fetch_image(self):
        """Fetch the best image"""
        image_len = 0

        if (len(self.image_urls) == 0): # No images
            return

        for image in self.image_urls:
            try:
                # get sizes of images
                req = urllib2.Request(image, txdata, txheaders)
                r = urllib2.urlopen(req)
                length = int(r.info()['Content-Length'])
                r.close()
                if length > image_len:
                    image_len = length
                    self.image_url = image
            except:
                pass
        if not self.image_url:
            print "Image dowloading failed"
            return
        
        self.image = (self.fxdfile + '.jpg')
        
        req = urllib2.Request(self.image_url, txdata, txheaders)
        r = urllib2.urlopen(req)
        i = vfs.open(self.image, 'w')
        i.write(r.read())
        i.close()
        r.close()
        
        # try to crop the image to avoid borders by imdb 
        try:
            import Image
            image = Image.open(filename)
            width, height = image.size
            image.crop((2,2,width-4, height-4)).save(filename)
        except:
            pass
        
        self.image = vfs.basename(self.image)

        print "Downloaded cover image from %s" % self.image_url
        print "Freevo knows nothing about the copyright of this image, please"
        print "go to %s to check for more informations about private." % self.image_url
        print "use of this image"

        
    def str2XML(self, line):
        """return a valid XML string"""
        try:
            s = Unicode(line)
            while s[-1] == u' ':
                s = s[:-1]
            if s[:4] == u'&#34':
                s = s[5:]
            if s[-4:] == u'#34;':
                s = s[:-5]
            # replace all & to &amp; ...
            s = s.replace(u"&", u"&amp;")

            # ... but this may be wrong for &#
            s = s.replace(u"&amp;#", u"&#")
            return s
        except:
            return Unicode(line)
        
    
    def getmedia_id(self, drive):
        """drive (device string)
        return a unique identifier for the disc"""

        if not vfs.exists(drive): return drive
        return cdrom_disc_id(drive)[1]

        
    def print_info(self):
        """return info part for FXD writing""" 
        ret = u''
        if self.info:
            ret = u'    <info>\n'
            for k in self.info.keys():
                ret += u'      <%s>' % k + Unicode(self.info[k]) + '</%s>\n' % k
            ret += u'    </info>\n'
        return ret

        
    def print_video(self):
        """return info part for FXD writing""" 
        ret = ''
        for vid in self.video:
            type, idref, device, mpl_opts, fname = vid
            ret += '      <%s' % self.str2XML(type)
            ret += ' id=\"%s\"' % self.str2XML(idref)
            if device: ret += ' media-id=\"%s\"' % self.str2XML(self.getmedia_id(device))
            if mpl_opts: ret += ' mplayer-options=\"%s\">' % self.str2XML(mpl_opts)
            else: ret += '>'
            ret += '%s' % self.str2XML(fname)
            ret += '</%s>\n' % self.str2XML(type)
        return ret

        
    def print_variant(self):
        """return info part for FXD writing""" 
        ret = ''
        for x in range(len(self.variant)):
            name, idref, mpl_opts, sub, s_dev, audio, a_dev = self.variant[x]
            
            ret += '      <variant name=\"%s\"' % self.str2XML(name)
            if self.varmpl_opt:
                ret += ' mplayer-options=\"%s\">\n' % self.str2XML(self.varmpl_opt)
            else: ret += '>\n'
            ret += '         <part ref=\"%s\"' % self.str2XML(idref)
            if mpl_opts: ret += ' mplayer-options=\"%s\">\n' % self.str2XML(mpl_opts)
            else: ret += ">\n"
            if sub:
                ret += '          <subtitle'
                if s_dev: ret += ' media-id=\"%s\">' % self.str2XML(self.getmedia_id(s_dev))
                else: ret += '>'
                ret += '%s</subtitle>\n' % self.str2XML(sub)
            if audio:
                ret += '          <audio'
                if a_dev: ret += ' media-id=\"%s\">' % self.str2XML(self.getmedia_id(a_dev))
                else: ret += '>'
                ret += '%s</audio>\n' % self.str2XML(audio)
            ret += '        </part>\n'
            ret += '      </variant>\n'
        
        return ret
        

#--------- Exception class

class Error(Exception):
    """Base class for exceptions in Imdb_Fxd"""
    def __str__(self):
        return self.message
    def __init__(self, message):
        self.message = message
        
class FxdImdb_Error(Error):
    """used to raise exceptions"""
    pass
        
class FxdImdb_XML_Error(Error):
    """used to raise exceptions"""
    pass
        
class FxdImdb_IO_Error(Error):
    """used to raise exceptions"""
    pass
    
class FxdImdb_Net_Error(Error):
    """used to raise exceptions"""
    pass
            
#------- Helper functions for creating tuples - these functions are classless

def makeVideo(type, id_ref, file, **values):
    """Create a video tuple"""
    device = mplayer_opt = None
    types = ['dvd', 'file', 'vcd']
    if type == None or id_ref == None or file == None:
        raise FxdImdb_XML_Error("Required values missing for tuple creation")

    if type not in types:
        raise FxdImdb_XML_Error("Invalid type passed to makeVideo")
        
    if values:
        #print values
        if 'device' in values: device = values['device']
        if 'mplayer_opt' in values: mplayer_opt = values['mplayer_opt']
    
    file = relative_path(file)
    t = type, id_ref, device, mplayer_opt, file
    return t
    
def makePart(name, id_ref, **values):
    """Create a part tuple"""
    mplayer_opt = sub = s_dev = audio = a_dev = None

    if id_ref == None or name == None:
        raise FxdImdb_XML_Error("Required values missing for tuple creation")
        
    if values:
        if 'mplayer_opt' in values: mplayer_opt = values['mplayer_opt']
        if 'sub' in values: sub = values['sub']
        if 's_dev' in values: s_dev = values['s_dev']
        if 'audio' in values: audio = values['audio']
        if 'a_dev' in values: a_dev = values['a_dev']
    if a_dev: audio = relative_path(audio)
    if s_dev: sub = relative_path(sub)
    t = name, id_ref, mplayer_opt, sub, s_dev, audio, a_dev
    return t
    
def makeFile_opt(mplayer_opt, file):
    """Create a file_opt tuple"""
    if mplayer_opt == None or file == None:
        raise FxdImdb_XML_Error("Required values missing for tuple creation")
    file = relative_path(file)        
    t = mplayer_opt, file
    
    return t

#--------- classless private functions
    
def relative_path(filename):
    """return the relative path to a mount point for a file on a removable disc"""
    from os.path import isabs, ismount, split, join
    
    if not isabs(filename) and not ismount(filename): return filename
    drivepaths = []
    for item in config.REMOVABLE_MEDIA:
        drivepaths.append(item.mountdir)
    for path in drivepaths:
        if filename.find(path) != -1:
            head = filename
            tail = ''
            while (head != path):
                x = split(head)
                head = x[0]
                if x[0] == '/' and x[1] == '' : return filename
                elif tail == '': tail = x[1]
                else: tail = join(x[1], tail)
                
            if head == path: return tail
    
    return filename
    
def point_maker(matching):
    return '%s.%s' % (matching.groups()[0], matching.groups()[1])
            
