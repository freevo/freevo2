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
# Revision 1.2  2002/08/12 11:34:59  dischi
# Changed IMDb support:
# o informations are now stored in hashes (Python dict)
# o support for rebuilding the database when imdb.py added something
# o support for the the new timestamp+label keys (only the timestamp is
#   used right now, this may change)
#
# Revision 1.1  2002/07/31 08:07:23  dischi
# Moved the XML movie file parsing in a new file. Both movie.py and
# config.py use the same code now.
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
import config
import util

# XML support
from xml.utils import qp_xml

# Set to 1 for debug output
DEBUG = 1



#
# parse <video> tag    
#
def parseVideo(dir, mplayer_files, video_node):
    first_file = ""
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
        if node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename':
                    if first_file == "":
                        first_file = os.path.join(add_to_path, file_nodes.textof())
                try: mplayer_files.remove(os.path.join(add_to_path,file_nodes.textof()))
                except ValueError: pass
                playlist += [os.path.join(add_to_path, file_nodes.textof())]
        if node.name == u'crop':
            try:
                crop = "-vop crop=%s:%s:%s:%s " % \
                       (node.attrs[('', "width")], node.attrs[('', "height")], \
                        node.attrs[('', "x")], node.attrs[('', "y")])
                mplayer_options += crop
            except KeyError:
                pass
    return ( mode, first_file, playlist, mplayer_options )


#
# parse <info> tag (not implemented yet)
#
def parseInfo(info_node):
    for node in info_node.children:
        pass



#
# parse a XML movie file
#
def parse(file, dir, mplayer_files):
    title = first_file = mplayer_options = ""
    image = None
    playlist = []
    info = []
    id = []
    mode = 'video'
    
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
                    elif node.name == u'video':
                        (mode, first_file, playlist, mplayer_options) = \
                               parseVideo(dir, mplayer_files, node)
                    elif node.name == u'info':
                        parseInfo(node)

    return title, image, (mode, first_file, playlist, mplayer_options), id, info



#
# hash all XML movie files
#
def hash_xml_database():
    config.MOVIE_INFORMATIONS = {}

    if os.path.exists("/tmp/freevo-rebuild-database"):
        os.system('rm -f /tmp/freevo-rebuild-database')

    if DEBUG: print "building xml hash databse"

    for name,dir in config.DIR_MOVIES:
        for file in util.recursefolders(dir,1,'*.xml',1):
            title, image, None, id, info = parse(file, os.path.dirname(file),[])
            if title and id:
                for i in id:
                    if len(i) > 16:
                        i = i[0:16]
                    config.MOVIE_INFORMATIONS[i] = (title, image, file)

    for file in util.recursefolders(config.MOVIE_DATA_DIR,1,'*.xml',1):
        title, image, None, id, info = parse(file, os.path.dirname(file),[])
        if title and id:
            for i in id:
                if len(i) > 16:
                    i = i[0:16]
                config.MOVIE_INFORMATIONS[i] = (title, image, file)


