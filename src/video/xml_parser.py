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
# Revision 1.12  2003/03/30 16:50:20  dischi
# pass xml_file definition to submenus
#
# Revision 1.11  2003/03/24 19:42:23  dischi
# fixed cd id search
#
# Revision 1.10  2003/03/23 20:00:26  dischi
# Added patch from Matthieu Weber for better mplayer_options and subitem
# handling
#
# Revision 1.9  2003/03/14 16:24:34  dischi
# Patch from Matthieu Weber with some bugfixes
#
# Revision 1.8  2003/02/17 18:32:24  dischi
# Added the infos from the xml file to VideoItem
#
# Revision 1.7  2003/02/15 19:56:51  dischi
# Removed some debug
#
# Revision 1.6  2003/02/12 10:28:28  dischi
# Added new xml file support. The old xml files won't work, you need to
# convert them.
#
# Revision 1.5  2003/01/19 16:26:35  dischi
# small bugfix
#
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
def xml_parseVideo(video_node):
    """
    Returns a big data structure like this:
    video -+- mplayer-options
           +- items -+- xxx...
                     +- yyy...
                     +- zzz -+- type
                             +- name
                             +- media-id
                             +- mplayer-options
                             +- data
               
              
           
    data types: "video": dictionary
                "items": dictionary of dictionaries (the keys are the "id"
                         attributes of the dvd/vcd/file elements)
                others: string
    
    Note: "items" has no equivalent in the XML file, it's just a container
    
    Example:
    getting the data (here the filename) of the item identified by "p1"
    is done by "filename = video['items']['p2']['data']"
    """
    video = {}
    video['mplayer-options'] = None
    try:
        video['mplayer-options'] = video_node.attrs[('',"mplayer-options")].encode('ascii')
    except KeyError:
        pass

    video['items'] = {}
    video['items-list'] = [] # Keeps a track of the element's order in the DOM tree
    for node in video_node.children:
        id = None
        try:
            id = node.attrs[('',"id")]
        except KeyError:
            # id is a required attribute. If not there, the item is useless
            continue
            
        i = {}
        if node.name == u'dvd':
            i['type'] = 'dvd'
        elif node.name == u'vcd':
            i['type'] = 'vcd'
        elif node.name == u'file':
            i['type'] = 'file'

        i['name'] = None
        try:
            i['name'] = node.attrs[('',"name")]
        except KeyError:
            pass
        i['media-id'] = None
        try:
            i['media-id'] = node.attrs[('',"media-id")]
        except KeyError:
            pass
        i['mplayer-options'] = None
        try:
            i['mplayer-options'] = node.attrs[('',"mplayer-options")]
        except KeyError:
            pass

        i['data'] = node.textof().encode('latin-1')
            
        video['items'][id] = i
        video['items-list'] += [ id ]

    return video


#
# parse <variants> tag    
#
def xml_parseVariants(variants_node):
    """
    Returns a big data structure like this:
    variants -+- 0...
              +- 1...
              +- 2 -+- name
                ... +- mplayer-options
                    +- parts -+- 0...
                              +- 1...
                              +- 2 -+- ref
                                ... +- mplayer-options
                                    +- subtitle -+- media-id
                                    |            +- file
                                    +- audio -+- media-id
                                              +- file
    
    data types: "variants": list of dictionaries
                "parts":    list of dictionaries
                "subtitle": dictionary
                "audio":    dictionary
                others:     string
    
    Example:
    getting the subtitle's filename of the first part of the first variant
    is done by "filename = variants[0]['parts'][0]['subtitle']['file']"
    """

    variants = []
    
    for variants_child in variants_node.children:
        if variants_child.name == u'variant':
            v = {}
            try:
                v['name'] = variants_child.attrs[('',"name")].encode('latin-1')
            except KeyError:
                # The name attribute is required. If not there, the variant is useless
                continue
            v['mplayer-options'] = None
            try:
                v['mplayer-options'] = variants_child.attrs[('',"mplayer-options")].encode('ascii')
            except KeyError:
                pass

            v['parts'] = []
            for variant_child in variants_child.children:
                if variant_child.name == u'part':
                    p = {}
                    try:
                        p['ref'] = variant_child.attrs[('',"ref")]
                    except KeyError:
                        # The ref attribute is required. If not there, the part is useless
                        continue

                    p['subtitle'] = {}
                    p['audio'] = {}
                    p['mplayer-options'] = None 
                    try:
                        p['mplayer-options'] = variant_child.attrs[('',"mplayer-options")].encode('ascii')
                    except KeyError:
                        pass

                    for part_child in variant_child.children:
                        if part_child.name == u'subtitle':
                            p['subtitle']['media-id'] = None
                            try:
                                p['subtitle']['media-id'] = part_child.attrs[('',"media-id")].encode('ascii')
                            except KeyError:
                                pass
                            p['subtitle']['file'] = part_child.textof().encode('latin-1')
                        elif part_child.name == u'audio':
                            p['audio']['media-id'] = None
                            try:
                                p['audio']['media-id'] = part_child.attrs[('',"media-id")].encode('ascii')
                            except KeyError:
                                pass
                            p['audio']['file'] = part_child.textof().encode('ascii')
                    v['parts'] += [ p ]
            variants += [ v ]
    return variants


#
# parse <info> tag (not implemented yet)
#
def xml_parseInfo(info_node):
    i = {}
    for node in info_node.children:
        if node.name == u'copyright':
            i['copyright'] = node.textof().encode('latin-1')
        elif node.name == u'url':
            i['url'] = node.textof().encode('latin-1')
        elif node.name == u'genre':
            i['genre'] = node.textof().encode('latin-1')
        elif node.name == u'runtime':
            i['runtime'] = node.textof().encode('latin-1')
        elif node.name == u'tagline':
            i['tagline'] = node.textof().encode('latin-1')
        elif node.name == u'plot':
            i['plot'] = node.textof().encode('latin-1')
        elif node.name == u'year':
            i['year'] = node.textof().encode('latin-1')
        elif node.name == u'rating':
            i['rating'] = node.textof().encode('latin-1')
    return i

def make_videoitem(video, variant):
    # Returns a VideoItem based on video and on variant.

    vitem = None
    if variant:
        if len(variant['parts']) > 1:
            vitem = VideoItem('', None)
            for part in variant['parts']:
                part_ref = part['ref']
                subitem = VideoItem(video['items'][part_ref]['data'], vitem)
                subitem.mode = video['items'][part_ref]['type']
                subitem.name = variant['name']
                subitem.media_id = video['items'][part_ref]['media-id']
                if subitem.media_id:
                    vitem.rom_id += [ subitem.media_id ]
                subitem.subtitle_file = part['subtitle']
                subitem.audio_file = part['audio']
                subitem.mplayer_options = ''
                if video['mplayer-options']:
                    subitem.mplayer_options += ' ' + video['mplayer-options']
                if video['items'][part_ref]['mplayer-options']:
                    subitem.mplayer_options += ' ' + video['items'][part_ref]['mplayer-options']
                if variant['mplayer-options']:
                    subitem.mplayer_options += ' ' + variant['mplayer-options']
                if part['mplayer-options']:
                    subitem.mplayer_options += " " + part['mplayer-options']
                if not subitem.mplayer_options:
                    subitem.mplayer_options = None
                vitem.subitems += [ subitem ]

        elif len(variant['parts']) == 1:
            part_ref = variant['parts'][0]['ref']
            vitem = VideoItem(video['items'][part_ref]['data'], None)
            vitem.mode = video['items'][part_ref]['type']
            vitem.media_id = video['items'][part_ref]['media-id']
            if vitem.media_id:
                vitem.rom_id += [ vitem.media_id ]
            vitem.subtitle_file = variant['parts'][0]['subtitle']
            vitem.audio_file = variant['parts'][0]['audio']

            vitem.mplayer_options = ''
            if video['mplayer-options']:
                vitem.mplayer_options += ' ' + video['mplayer-options']
            if video['items'][part_ref]['mplayer-options']:
                vitem.mplayer_options += ' ' + video['items'][part_ref]['mplayer-options']
            if variant['mplayer-options']:
                vitem.mplayer_options += ' ' + variant['mplayer-options']
            if variant['parts'][0]['mplayer-options']:
                vitem.mplayer_options += " " + variant['parts'][0]['mplayer-options']
            if not vitem.mplayer_options:
                vitem.mplayer_options = None
    else:
        if len(video['items-list']) > 1:
            vitem = VideoItem('', None)
            for v in video['items-list']:
                subitem = VideoItem(video['items'][v]['data'], vitem)
                subitem.mode = video['items'][v]['type']
                subitem.media_id = video['items'][v]['media-id']
                if subitem.media_id:
                    vitem.rom_id += [ subitem.media_id ]
                subitem.mplayer_options = ''
                if video['mplayer-options']:
                    subitem.mplayer_options += ' ' + video['mplayer-options']
                if video['items'][v]['mplayer-options']:
                    subitem.mplayer_options += ' ' + video['items'][v]['mplayer-options']
                if not subitem.mplayer_options:
                    subitem.mplayer_options = None
                vitem.subitems += [ subitem ]
        else:
            ref = video['items-list'][0]
            vitem = VideoItem(video['items'][ref]['data'], None)
            vitem.mode = video['items'][ref]['type']
            vitem.media_id = video['items'][ref]['media-id']
            if vitem.media_id:
                vitem.rom_id += [ vitem.media_id ]
            vitem.mplayer_options = ''
            if video['mplayer-options']:
                vitem.mplayer_options += ' ' + video['mplayer-options']
            if video['items'][ref]['mplayer-options']:
                vitem.mplayer_options += ' ' + video['items'][ref]['mplayer-options']
            if not vitem.mplayer_options:
                vitem.mplayer_options = None
    
    return vitem

#
# parse a XML movie file
#
def parseMovieFile(file, parent, duplicate_check):
    # Returns:
    #   a list of VideoItems,
    #     each VideoItem possibly contains a list of VideoItems
    # 
    dir = os.path.dirname(file)
    movies = []
    
    try:
        parser = qp_xml.Parser()
        # Let's name node variables after their XML names
        freevo = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file
        return []


    for freevo_child in freevo.children:
        if freevo_child.name == 'disc-set':
            """
            Data structure:
            disc-set -+- [title]
                      +- [cover]
                      +- info -+- ...
                      +- disc -+- 1...
                               +- 2...
                               +- 3 -+- [media-id]
                                     +- [title]
                                     +- [l_re]
                                     +- [cover]
                                     +- info -+- ...
            Data types:
              disc-set: dictionary
              info:     dictionary
              disc:     list of dictionaries
              others:   string
            """
            # freevo_child == /freevo/disc-set
            disc_set = {}
            disc_set['disc'] = []
            disc_set['cover'] = None
            disc_set['title'] = None
            disc_set['info'] = {}
            
            try:
                disc_set['title'] = freevo_child.attrs[('', "title")].encode('latin-1')
            except KeyError:
                pass
                
            for disc_set_child in freevo_child.children:
                if disc_set_child.name == 'disc':
                    # disc_set_child == /freevo/disc-set/disc
                    disc = {}
                    label_required = 0 
                    disc['media-id'] = None
                    # One of the media-id or label-regexp attributes is mandatory.
                    # If not there, the disc is useless
                    try:
                        disc['media-id'] = disc_set_child.attrs[('', "media-id")]
                    except KeyError:
                        label_required = 1
                    
                    disc['l_re'] = None
                    try:
                        disc['l_re'] = disc_set_child.attrs[('', "label-regexp")]
                    except KeyError:
                        if label_required == 1:
                            continue

                    disc_set['disc'] += [ disc ]
                    
                elif disc_set_child.name == u'cover-img':
                    # disc_child == /freevo/disc_set/disc/cover-img
                    img = disc_set_child.textof().encode('ascii')
                    if os.path.isfile(os.path.join(dir, img)):
                        disc_set['cover'] = os.path.join(dir,img)

                elif disc_set_child.name == u'info':
                    # disc_child == /freevo/disc_set/info
                    disc_set['info'] = xml_parseInfo(disc_set_child)

            if disc_set:
                dsitem = VideoItem('', None)
                dsitem.parent = parent
                dsitem.name = disc_set['title']
                dsitem.image = disc_set['cover']
                dsitem.info = disc_set['info']
                dsitem.xml_file = file
                if disc['l_re']:
                    dsitem.rom_label += [ disc['l_re'] ]
                for disc in disc_set['disc']:
                    if disc['media-id']:
                        dsitem.rom_id += [ disc['media-id'] ]
                movies += [ dsitem ]

        elif freevo_child.name == 'movie':
            # freevo_child == /freevo/items/movie
            video = {}
            variants = []
            info = {}
            image = ""

            for movie_child in freevo_child.children:
                if movie_child.name == u'video':
                    # movie_child == /freevo/items/movie/video
                    video = xml_parseVideo(movie_child)
                elif movie_child.name == u'variants':
                    # movie_child == /freevo/items/movie/variants
                    variants = xml_parseVariants(movie_child)
                elif movie_child.name == u'info':
                    # movie_child == /freevo/items/movie/info
                    info = xml_parseInfo(movie_child)
                elif movie_child.name == u'cover-img':
                    # movie_child == /freevo/items/movie/cover-img
                    img = movie_child.textof().encode('ascii')
                    # the image file must be stored in the same
                    # directory than that XML file
                    if os.path.isfile(os.path.join(dir, img)):
                        image = os.path.join(dir, img)

            title = None
            try:
                title = freevo_child.attrs[('', "title")].encode('latin-1')
            except KeyError:
                pass
            
            for p in video['items'].keys():
                if video['items'][p]['type'] == 'file':
                    filename = video['items'][p]['data']
                    if filename.find('://') == -1 and not video['items'][p]['media-id']:
                        video['items'][p]['data'] = os.path.join(dir, filename)
                    for i in range(len(duplicate_check)):
                        try:
                            if (unicode(duplicate_check[i], 'latin1', 'ignore') == \
                                os.path.join(dir, filename)):
                                del duplicate_check[i]
                                break
                        except:
                            if duplicate_check[i] == os.path.join(dir, filename):
                                del duplicate_check[i]
                                break

            mitem = None
            if variants:
                mitem = make_videoitem(video, variants[0])
            else:
                mitem = make_videoitem(video, None)
            mitem.parent = parent
            mitem.name = title
            mitem.image = image
            mitem.xml_file = file
            mitem.info = info
            
            for subitem in mitem.subitems:
                subitem.xml_file = file
            # Be careful: singular and plural names are used
            for variant in variants:
                varitem = make_videoitem(video, variant)
                varitem.parent = mitem
                varitem.name = variant['name']
                varitem.image = image
                varitem.xml_file = file
                for subitem in varitem.subitems:
                    subitem.xml_file = file
                mitem.variants += [ varitem ] 

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
        for file in util.recursefolders(dir,1,'*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
            infolist = parseMovieFile(file, os.path.dirname(file),[])
            for info in infolist:
                if info.rom_id:
                    for i in info.rom_id:
                        config.MOVIE_INFORMATIONS_ID[i] = info
                if info.rom_label:
                    for l in info.rom_label:
                        l_re = re.compile(l)
                        config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
                
    for file in util.recursefolders(config.MOVIE_DATA_DIR,1,
                                    '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
        infolist = parseMovieFile(file, os.path.dirname(file),[])
        for info in infolist:
            config.MOVIE_INFORMATIONS += [ info ]
            if info.rom_id:
                for i in info.rom_id:
                    config.MOVIE_INFORMATIONS_ID[i] = info
            if info.rom_label:
                for l in info.rom_label:
                    l_re = re.compile(l)
                    config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]

    if DEBUG: print 'done'
