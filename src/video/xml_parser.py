#if 0 /*
# -----------------------------------------------------------------------
# xml_parser.py - Parser for imdb.py xml files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2003/01/12 13:51:51  dischi
# Added the feature to remove items for videos, too. For that the interface
# was modified (update instead of remove).
#
# Revision 1.3  2003/01/12 10:58:31  dischi
# Changed the multiple file handling. If a videoitem has more than one file,
# the videoitem gets the filename '' and subitems for each file. With that
# change it is possible to spit a movie that part one is a VCD, part two a
# file on the harddisc.
#
# Revision 1.2  2002/12/07 13:29:49  dischi
# Make a new database with all movies, even without id and label
#
# Revision 1.1  2002/11/24 13:58:45  dischi
# code cleanup
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
import re

import config
import util

# XML support
from xml.utils import qp_xml

from videoitem import VideoItem

# Set to 1 for debug output
DEBUG = config.DEBUG
TRUE = 1
FALSE = 0


#
# parse <video> tag    
#
def xml_parseVideo(video_node, dir, duplicate_check):
    playlist = []
    mode = 'file'
    mplayer_options = ""

    for node in video_node.children:
        if node.name == u'dvd':
            mode = 'dvd'
        if node.name == u'vcd':
            mode = 'vcd'
        if node.name == u'mplayer_options':
            mplayer_options += node.textof()

        if node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename':
                    filename = file_nodes.textof()
                    if filename.find('://') == -1:
                        filename = os.path.join(dir, filename)

                    for i in range(len(duplicate_check)):
                        if (unicode(duplicate_check[i], 'latin1', 'ignore') == filename):
                            del duplicate_check[i]
                            break
                    playlist += [filename]

        # XXX fix this to merge all -vop arguments into one
        # XXX one -vob .... argument
        if node.name == u'crop':
            try:
                crop = "-vop crop=%s:%s:%s:%s " % \
                       (node.attrs[('', "width")], node.attrs[('', "height")], \
                        node.attrs[('', "x")], node.attrs[('', "y")])
                mplayer_options += crop
            except KeyError:
                pass

    if len(playlist) > 1:
        movie = VideoItem('', None)
        for p in playlist:
            subitem = VideoItem(p, movie)
            subitem.mode = mode
            subitem.mplayer_options = mplayer_options
            movie.subitems += [ subitem ]

    elif len(playlist) == 1:
        movie = VideoItem(playlist[0], None)

    else:
        movie = VideoItem('', None)
        
    movie.mode = mode
    movie.mplayer_options = mplayer_options

    return movie



#
# parse <info> tag (not implemented yet)
#
def xml_parseInfo(info_node, i):
    for node in info_node.children:
        if node.name == u'url':
            i.url = node.textof().encode('latin-1')
        if node.name == u'genre':
            i.genre = node.textof().encode('latin-1')
        if node.name == u'runtime':
            i.runtime = node.textof().encode('latin-1')
        if node.name == u'tagline':
            i.tagline = node.textof().encode('latin-1')
        if node.name == u'plot':
            i.plot = node.textof().encode('latin-1')
        if node.name == u'year':
            i.year = node.textof().encode('latin-1')
        if node.name == u'rating':
            i.rating = node.textof().encode('latin-1')


#
# parse a XML movie file
#
def parseMovieFile(file, parent, duplicate_check):
    dir = os.path.dirname(file)
    movies = []
    
    try:
        parser = qp_xml.Parser()
        box = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file
        return []


    for c in box.children:
        if c.name == 'movie':
            mitem = None

            for node in c.children:
                if node.name == u'video':
                    mitem = xml_parseVideo(node, dir, duplicate_check)

            if mitem:
                mitem.parent = parent
                for node in c.children:
                    if node.name == u'title':
                        mitem.name = node.textof().encode('latin-1')
                    elif node.name == u'cover' and \
                         os.path.isfile(os.path.join(dir,node.textof())):
                        mitem.image = os.path.join(dir, node.textof())
                    elif node.name == u'id':
                        mitem.rom_id += [node.textof()]
                    elif node.name == u'label':
                        mitem.rom_label += [node.textof()]
                    elif node.name == u'item':
                        xml_parseInfo(node, mitem)
                        
                mitem.xml_file = file
                for subitem in mitem.subitems:
                    subitem.xml_file = file
                movies += [ mitem ]

    return movies


# --------------------------------------------------------------------------------------

#
# hash all XML movie files
#
def hash_xml_database():
    config.MOVIE_INFORMATIONS       = []
    config.MOVIE_INFORMATIONS_ID    = {}
    config.MOVIE_INFORMATIONS_LABEL = []

    if os.path.exists("/tmp/freevo-rebuild-database"):
        os.system('rm -f /tmp/freevo-rebuild-database')

    if DEBUG: print "Building the xml hash database...",

    for name,dir in config.DIR_MOVIES:
        for file in util.recursefolders(dir,1,'*.xml',1):
            infolist = parseMovieFile(file, os.path.dirname(file),[])
            for info in infolist:
                if info.rom_id:
                    for i in info.rom_id:
                        if len(i) > 16:
                            i = i[0:16]
                        config.MOVIE_INFORMATIONS_ID[i] = info
                if info.rom_label:
                    for l in info.rom_label:
                        l_re = re.compile(l)
                        config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
                
    for file in util.recursefolders(config.MOVIE_DATA_DIR,1,'*.xml',1):
        infolist = parseMovieFile(file, os.path.dirname(file),[])
        for info in infolist:
            config.MOVIE_INFORMATIONS += [ info ]
            if info.rom_id:
                for i in info.rom_id:
                    if len(i) > 16:
                        i = i[0:16]
                    config.MOVIE_INFORMATIONS_ID[i] = info
            if info.rom_label:
                for l in info.rom_label:
                    l_re = re.compile(l)
                    config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]

    if DEBUG: print 'done'
