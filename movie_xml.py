# ----------------------------------------------------------------------
# movie_xml.py - the Freevo Movie XML Parser module. 
# ----------------------------------------------------------------------
# $Id$
#
# Authors:     Dirk Meyer <dischi@tzi.de>
# Notes:
# Todo:        * Parse the <info> node
#
# ----------------------------------------------------------------------
# $Log$
# Revision 1.15  2002/11/19 06:24:23  krister
# Video files that were in an XML file were not removed from the playlist due to Unicode issues, fixed. Please test!
#
# Revision 1.14  2002/11/01 16:51:19  dischi
# Add support for urls in <filename>
#
# Revision 1.13  2002/10/21 02:31:38  krister
# Set DEBUG = config.DEBUG.
#
# Revision 1.12  2002/10/16 18:22:28  dischi
# Added runtime information (a long time ago, I forgot to check in)
#
# Revision 1.11  2002/10/12 22:30:45  krister
# Removed debug output.
#
# Revision 1.10  2002/10/09 17:24:02  dischi
# only do debug print when we have info
#
# Revision 1.9  2002/10/09 02:39:24  outlyer
# We were throwing away the return value from parseInfo; now we're keeping it.
#
# Revision 1.8  2002/10/08 15:50:54  dischi
# Parse more infos from the xml file to MovieExtraInformation (maybe we
# should change that name...)
#
# Revision 1.7  2002/10/06 14:58:51  dischi
# Lots of changes:
# o removed some old cvs log messages
# o some classes without member functions are in datatypes.py
# o movie_xml.parse now returns an object of MovieInformation instead of
#   a long list
# o mplayer_options now works better for options on cd/dvd/vcd
# o you can disable -wid usage
# o mplayer can play movies as strings or as FileInformation objects with
#   mplayer_options
#
# Revision 1.6  2002/09/15 14:57:16  dischi
# Support for <label> instead of <id> in the movie xml files. You can use a
# regexp to match a hole set of discs (use with care!)
#
# Revision 1.5  2002/09/13 18:07:51  dischi
# Added tag <mplayer_options> inside <video>
#
#
# ----------------------------------------------------------------------
# 
# Copyright (C) 2002 Dirk Meyer
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
# ----------------------------------------------------------------------
#


import os
import re

import config
import util

# XML support
from xml.utils import qp_xml

# Some datatypes we need
from datatypes import *

# Set to 1 for debug output
DEBUG = config.DEBUG


#
# parse <video> tag    
#
def parseVideo(dir, mplayer_files, video_node):
    playlist = []
    mode = 'video'
    add_to_path = dir
    mplayer_options = ""
    
    for node in video_node.children:
        if node.name == u'dvd':
            mode = 'dvd'
            first_file = "1"
        if node.name == u'vcd':
            mode = 'vcd'
            first_file = "1"
        if node.name == u'mplayer_options':
            mplayer_options += node.textof()

        if node.name == u'files':
            for file_nodes in node.children:
                fname = os.path.join(add_to_path, file_nodes.textof())

                for i in range(len(mplayer_files)):
                    if (unicode(mplayer_files[i], 'latin1', 'ignore') == fname):
                        del mplayer_files[i]
                        break
                    
                # XXX add mplayer_options for specific files, too
                filename = file_nodes.textof()
                if filename.find('://') != -1:
                    file = FileInformation(file=filename)
                else:
                    file = FileInformation(file=os.path.join(add_to_path, filename))
                    
                playlist += [file]

        if node.name == u'crop':
            try:
                crop = "-vop crop=%s:%s:%s:%s " % \
                       (node.attrs[('', "width")], node.attrs[('', "height")], \
                        node.attrs[('', "x")], node.attrs[('', "y")])
                mplayer_options += crop
            except KeyError:
                pass

    for file in playlist:
        file.mode = mode
        file.mplayer_options = mplayer_options

    # make dummy filename
    if not playlist:
        file = FileInformation(mode, '', mplayer_options)
        playlist += [file]

    return playlist



#
# parse <info> tag (not implemented yet)
#
def parseInfo(info_node):
    info = MovieExtraInformation()
    for node in info_node.children:
        if node.name == u'url':
            info.url = node.textof().encode('latin-1')
        if node.name == u'genre':
            info.genre = node.textof().encode('latin-1')
        if node.name == u'runtime':
            info.runtime = node.textof().encode('latin-1')
        if node.name == u'tagline':
            info.tagline = node.textof().encode('latin-1')
        if node.name == u'plot':
            info.plot = node.textof().encode('latin-1')
        if node.name == u'year':
            info.year = node.textof().encode('latin-1')
        if node.name == u'rating':
            info.rating = node.textof().encode('latin-1')
    return info


#
# parse a XML movie file
#
def parse(file, dir, mplayer_files):
    title = mplayer_options = ""
    image = None
    playlist = []
    info = []
    id = []
    mode = 'video'
    label = []
    
    try:
        parser = qp_xml.Parser()
        box = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file

    else:
        for c in box.children:
            if c.name == 'movie':
                for node in c.children:
                    if node.name == u'title':
                        title = node.textof().encode('latin-1')
                    elif node.name == u'cover' and \
                         os.path.isfile(os.path.join(dir,node.textof())):
                        image = os.path.join(dir, node.textof())
                    elif node.name == u'id':
                        id += [node.textof()]
                    elif node.name == u'label':
                        label += [node.textof()]
                    elif node.name == u'video':
                        playlist = parseVideo(dir, mplayer_files, node)
                    elif node.name == u'info':
                        info = parseInfo(node)

    return MovieInformation(title, image, playlist, id, label, info, file)



#
# hash all XML movie files
#
def hash_xml_database():
    config.MOVIE_INFORMATIONS_ID    = {}
    config.MOVIE_INFORMATIONS_LABEL = []

    if os.path.exists("/tmp/freevo-rebuild-database"):
        os.system('rm -f /tmp/freevo-rebuild-database')

    if DEBUG: print "Building the xml hash database...",

    for name,dir in config.DIR_MOVIES:
        for file in util.recursefolders(dir,1,'*.xml',1):
            info = parse(file, os.path.dirname(file),[])
            if info.disc_id:
                for i in info.disc_id:
                    if len(i) > 16:
                        i = i[0:16]
                    config.MOVIE_INFORMATIONS_ID[i] = info
            if info.disc_label:
                for l in info.disc_label:
                    l_re = re.compile(l)
                    config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
                
    for file in util.recursefolders(config.MOVIE_DATA_DIR,1,'*.xml',1):
        info = parse(file, os.path.dirname(file),[])
        if info.disc_id:
            for i in info.disc_id:
                if len(i) > 16:
                    i = i[0:16]
                config.MOVIE_INFORMATIONS_ID[i] = info
        if info.disc_label:
            for l in info.disc_label:
                l_re = re.compile(l)
                config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]

    if DEBUG: print 'done'
