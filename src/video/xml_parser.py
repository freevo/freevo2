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
# Revision 1.28  2003/07/18 19:48:24  dischi
# support for datadir
#
# Revision 1.27  2003/07/13 13:11:17  dischi
# show xml info on variants, too
#
# Revision 1.26  2003/07/12 10:12:34  dischi
# handle the case where mmpython returns no results
#
# Revision 1.25  2003/07/11 19:44:18  dischi
# close file after parsing
#
# Revision 1.24  2003/07/07 21:51:44  dischi
# add mmpython info to VideoItems with subitems (take infos from first item)
#
# Revision 1.23  2003/06/30 15:30:54  dischi
# some checking to avoid endless scanning
#
# Revision 1.22  2003/06/29 21:31:56  gsbarbieri
# subtitle and audio now use the path to files and are quoted.
#
# Revision 1.21  2003/06/29 20:43:30  dischi
# o mmpython support
# o mplayer is now a plugin
#
# Revision 1.20  2003/05/11 16:22:14  dischi
# use format_text for data
#
# Revision 1.19  2003/04/28 17:57:11  dischi
# exception handling for bad fxd files
#
# Revision 1.18  2003/04/26 16:38:57  dischi
# added patch from Matthieu Weber for mplayer options in disc
#
# Revision 1.17  2003/04/24 19:56:45  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.16  2003/04/24 19:14:51  dischi
# pass xml_file to directory and videoitems
#
# Revision 1.15  2003/04/24 18:07:45  dischi
# use format_text for plot and tagline
#
# Revision 1.14  2003/04/20 17:36:50  dischi
# Renamed TV_SHOW_IMAGE_DIR to TV_SHOW_DATA_DIR. This directory can contain
# images like before, but also fxd files for the tv show with global
# informations (plot/tagline/etc) and mplayer options.
#
# Revision 1.13  2003/04/06 21:13:07  dischi
# o Switched to the new main skin
# o some cleanups (removed unneeded imports)
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
import traceback
import mmpython

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

        i['data'] = util.format_text(node.textof().encode('latin-1'))
            
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
            i['length'] = node.textof().encode('latin-1')
        elif node.name == u'tagline':
            i['tagline'] = util.format_text(node.textof().encode('latin-1'))
        elif node.name == u'plot':
            i['plot'] = util.format_text(node.textof().encode('latin-1'))
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
        if not video.has_key('items-list'):
            video['items-list'] = []
            vitem = VideoItem('', None)
            
        elif len(video['items-list']) == 0:
            vitem = VideoItem('', None)
            vitem.mplayer_options = ''
            if video['mplayer-options']:
                vitem.mplayer_options += ' ' + video['mplayer-options']

        elif len(video['items-list']) > 1:
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
def save_parseMovieFile(file, parent, duplicate_check):
    try:
        return parseMovieFile(file, parent, duplicate_check)
    except:
        print 'Error parsing %s' % file
        traceback.print_exc()
        return []

    
def parseMovieFile(file, parent, duplicate_check):
    # Returns:
    #   a list of VideoItems,
    #     each VideoItem possibly contains a list of VideoItems
    # 
    dir = os.path.dirname(file)

    # find the realdir in case this file is in MOVIE_DATA_DIR
    if dir.find(config.MOVIE_DATA_DIR) == 0:
        realdir = os.path.join('/', dir[len(config.MOVIE_DATA_DIR):])
        if realdir.find('/disc/') == 0:
            realdir = realdir[6:]
            for c in config.REMOVABLE_MEDIA:
                if realdir.find(c.id) == 0:
                    realdir = os.path.join(c.mountdir, realdir[len(c.id)+1:])
                    break
    else:
        realdir = dir
                
    movies = []
    
    parser = qp_xml.Parser()
    # Let's name node variables after their XML names
    f = open(file)
    freevo = parser.parse(f.read())
    f.close()
    
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
                                     +- file -+- 1...
                                              +- 2...
                                              +- 3 -+- file-id
                                                    +- mplayer_options

            Data types:
              disc-set: dictionary
              info:     dictionary
              disc:     list of dictionaries
              file:     list of dictionaries
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
                    disc['mplayer-options'] = None
                    disc['files-options'] = []
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
                    try:
                        disc['mplayer-options'] = disc_set_child.attrs[('', "mplayer-options")]
                    except KeyError:
                        pass

                    for disc_child in disc_set_child.children:
                        if disc_child.name == 'file-opt':
                            fo = {}
                            fo['media-id'] = disc['media-id']
                            fo['mplayer-options'] = disc['mplayer-options']
                            fo['name'] = None
                            fo['file-id'] = None
                            try:
                                if fo['mplayer-options']:
                                    fo['mplayer-options'] += " " + disc_child.attrs[('', "mplayer-options")]
                                else:
                                    fo['mplayer-options'] = disc_child.attrs[('', "mplayer-options")]
                            except KeyError:
                                pass
                            if not fo['media-id']:
                                try:
                                    fo['media-id'] = disc_child.attrs[('', "media-id")]
                                except KeyError:
                                    continue

                            fo['name'] = disc_child.textof().encode('latin-1')
                            fo['file-id'] = fo['media-id']
                            if fo['name']:
                                fo['file-id'] += fo['name']

                            disc['files-options'] += [ fo ]

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
                    if disc['files-options']:
                        for fo in disc['files-options']:
                            dsitem.files_options += [ fo ]
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

            if video.has_key('items'):
                for p in video['items'].keys():
                    if video['items'][p]['type'] == 'file':
                        filename = video['items'][p]['data']
                        if filename.find('://') == -1 and not video['items'][p]['media-id']:
                            video['items'][p]['data'] = os.path.join(realdir, filename)
                        for i in range(len(duplicate_check)):
                            try:
                                if (unicode(duplicate_check[i], 'latin1', 'ignore') == \
                                    os.path.join(realdir, filename)):
                                    del duplicate_check[i]
                                    break
                            except:
                                if duplicate_check[i] == os.path.join(realdir, filename):
                                    del duplicate_check[i]
                                    break

            mitem = None
            if variants:
                for v in variants:
                    for p in v[ 'parts' ]:
                        for i in ( 'audio', 'subtitle' ):
                            if p.has_key( i )  and p[ i ].has_key( 'file' ):
                                filename = p[ i ][ 'file' ]
                                filename = os.path.join( realdir, filename )
                                if os.path.isfile( filename ):
                                    p[ i ][ 'file' ] = filename
                
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
                varitem.info = info
                varitem.xml_file = file
                for subitem in varitem.subitems:
                    subitem.xml_file = file
                mitem.variants += [ varitem ] 

            movies += [ mitem ]

    for m in movies:
        m.fxd_file = file
        if not m.subitems and os.path.isfile(m.filename):
            mminfo = mmpython.parse(m.filename)
            if mminfo:
                for i in m.info:
                    if m.info[i]:
                        mminfo[i] = m.info[i]
                m.info = mminfo
        elif m.subitems and os.path.isfile(m.subitems[0].filename):
            mminfo = mmpython.parse(m.subitems[0].filename)
            if mminfo:
                for i in m.info:
                    if m.info[i]:
                        mminfo[i] = m.info[i]
                m.info = mminfo

    return movies


# --------------------------------------------------------------------------------------

#
# hash all XML movie files
#
def hash_xml_database():
    config.MOVIE_INFORMATIONS       = []
    config.MOVIE_INFORMATIONS_ID    = {}
    config.MOVIE_INFORMATIONS_LABEL = []
    config.DISC_SET_INFORMATIONS_ID = {}
    config.TV_SHOW_INFORMATIONS     = {}
    
    if os.path.exists("/tmp/freevo-rebuild-database"):
        try:
            os.remove('/tmp/freevo-rebuild-database')
        except OSError:
            print '*********************************************************'
            print
            print '*********************************************************'
            print 'ERROR: unable to remove /tmp/freevo-rebuild-database'
            print 'please fix permissions'
            print '*********************************************************'
            print
            return 0

    if DEBUG: print "Building the xml hash database...",

    for name,dir in config.DIR_MOVIES:
        for file in util.recursefolders(dir,1,'*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
            infolist = save_parseMovieFile(file, os.path.dirname(file),[])
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
        infolist = save_parseMovieFile(file, os.path.dirname(file),[])
        for info in infolist:
            config.MOVIE_INFORMATIONS += [ info ]
            if info.rom_id:
                for i in info.rom_id:
                    config.MOVIE_INFORMATIONS_ID[i] = info
            if info.rom_label:
                for l in info.rom_label:
                    l_re = re.compile(l)
                    config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
            if info.files_options:
                for fo in info.files_options:
                    config.DISC_SET_INFORMATIONS_ID[fo['file-id']] = fo['mplayer-options']

    for file in util.recursefolders(config.TV_SHOW_DATA_DIR,1,
                                    '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
        infolist = save_parseMovieFile(file, os.path.dirname(file),[])
        for info in infolist:
            k = os.path.splitext(os.path.basename(file))[0]
            config.TV_SHOW_INFORMATIONS[k] = (info.image, info.info, info.mplayer_options,
                                              file)
            
    if DEBUG: print 'done'
    return 1
