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
# Revision 1.40  2003/10/03 16:46:13  dischi
# moved the encoding type (latin-1) to the config file config.LOCALE
#
# Revision 1.39  2003/10/01 18:56:25  dischi
# bugfix if no MOVIE_DATA_DIR is set
#
# Revision 1.38  2003/09/23 13:45:20  outlyer
# Making more informational text quiet by default.
#
# Revision 1.37  2003/09/20 15:08:26  dischi
# some adjustments to the missing testfiles
#
# Revision 1.36  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.35  2003/08/30 19:00:56  dischi
# multi movie files fixed
#
# Revision 1.34  2003/08/30 12:20:10  dischi
# Respect the given parent for parsing. This avoids calling mmpython again
# with maybe wrong informations (disc or not). Also restructured the code
#
# Revision 1.33  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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
import traceback

import config
import util

# XML support
from xml.utils import qp_xml

from videoitem import VideoItem

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

        i['data'] = util.format_text(node.textof().encode(config.LOCALE))
            
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
                v['name'] = variants_child.attrs[('',"name")].encode(config.LOCALE)
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
                            p['subtitle']['file'] = part_child.textof().encode(config.LOCALE)
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
            i['copyright'] = node.textof().encode(config.LOCALE)
        elif node.name == u'url':
            i['url'] = node.textof().encode(config.LOCALE)
        elif node.name == u'genre':
            i['genre'] = node.textof().encode(config.LOCALE)
        elif node.name == u'runtime':
            i['length'] = node.textof().encode(config.LOCALE)
        elif node.name == u'tagline':
            i['tagline'] = util.format_text(node.textof().encode(config.LOCALE))
        elif node.name == u'plot':
            i['plot'] = util.format_text(node.textof().encode(config.LOCALE))
        elif node.name == u'year':
            i['year'] = node.textof().encode(config.LOCALE)
        elif node.name == u'rating':
            i['rating'] = node.textof().encode(config.LOCALE)
    return i

def make_videoitem(video, variant, parent):
    # Returns a VideoItem based on video and on variant.

    vitem = None
    if variant:
        if len(variant['parts']) > 1:
            vitem = VideoItem('', parent)
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
            vitem = VideoItem(video['items'][part_ref]['data'], parent)
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
            vitem = VideoItem('', parent)
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
            vitem = VideoItem(video['items'][ref]['data'], parent)
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


def parse_disc_set(node, file, parent, duplicate_check):
    """
    parse disc-set

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
    # node == /freevo/disc-set
    disc_set = {}
    disc_set['disc'] = []
    disc_set['cover'] = None
    disc_set['title'] = None
    disc_set['info'] = {}

    movies = []

    try:
        disc_set['title'] = node.attrs[('', "title")].encode(config.LOCALE)
    except KeyError:
        pass

    dir = os.path.dirname(file)

    for disc_set_child in node.children:
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
                            fo['mplayer-options'] += " " + \
                                                     disc_child.attrs[('', "mplayer-options")]
                        else:
                            fo['mplayer-options'] = disc_child.attrs[('', "mplayer-options")]
                    except KeyError:
                        pass
                    if not fo['media-id']:
                        try:
                            fo['media-id'] = disc_child.attrs[('', "media-id")]
                        except KeyError:
                            continue

                    fo['name'] = disc_child.textof().encode(config.LOCALE)
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
        dsitem = VideoItem('', parent)
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

    return movies



def parse_movie(node, file, parent, duplicate_check):
    """
    parse the <movie> tag
    """
    movies = []

    # node == /freevo/items/movie
    video = {}
    variants = []
    info = {}
    image = ""

    dir = os.path.dirname(file)

    # find the realdir in case this file is in MOVIE_DATA_DIR
    if config.MOVIE_DATA_DIR and dir.find(config.MOVIE_DATA_DIR) == 0:
        realdir = os.path.join('/', dir[len(config.MOVIE_DATA_DIR):])
        if realdir.find('/disc/') == 0:
            realdir = realdir[6:]
            for c in config.REMOVABLE_MEDIA:
                if realdir.find(c.id) == 0:
                    realdir = os.path.join(c.mountdir, realdir[len(c.id)+1:])
                    break
    else:
        realdir = dir

    for movie_child in node.children:
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
        title = node.attrs[('', "title")].encode(config.LOCALE)
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

        mitem = make_videoitem(video, variants[0], parent)
    else:
        mitem = make_videoitem(video, None, parent)
    mitem.name = title
    mitem.image = image
    mitem.xml_file = file
    for i in info:
        mitem.info[i] = info[i]

    for subitem in mitem.subitems:
        subitem.xml_file = file
    # Be careful: singular and plural names are used
    for variant in variants:
        varitem = make_videoitem(video, variant, mitem)
        varitem.name = variant['name']
        varitem.image = image
        for i in info:
            varitem.info[i] = info[i]
        varitem.xml_file = file
        for subitem in varitem.subitems:
            subitem.xml_file = file
        mitem.variants += [ varitem ] 

    movies += [ mitem ]
    return movies


def parseMovieFile(file, parent=None, duplicate_check=[]):
    """
    parse a XML movie file

    Returns:
      a list of VideoItems,
      each VideoItem possibly contains a list of VideoItems
    """ 
    try:
        movies = []

        parser = qp_xml.Parser()
        # Let's name node variables after their XML names
        f = open(file)
        freevo = parser.parse(f.read())
        f.close()

        for freevo_child in freevo.children:
            if freevo_child.name == 'disc-set':
                movies += parse_disc_set(freevo_child, file, parent, duplicate_check)

            elif freevo_child.name == 'movie':
                movies += parse_movie(freevo_child, file, parent, duplicate_check)

        for m in movies:
            m.fxd_file = file

        return movies
    except:
        print 'Error parsing %s' % file
        traceback.print_exc()
        return []


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

    _debug_("Building the xml hash database...",2)

    if not config.ONLY_SCAN_DATADIR:
        for name,dir in config.DIR_MOVIES:
            for file in util.recursefolders(dir,1,'*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
                infolist = parseMovieFile(file)
                for info in infolist:
                    if info.rom_id:
                        for i in info.rom_id:
                            config.MOVIE_INFORMATIONS_ID[i] = info
                    if info.rom_label:
                        for l in info.rom_label:
                            l_re = re.compile(l)
                            config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
                
    if config.MOVIE_DATA_DIR:
        for file in util.recursefolders(config.MOVIE_DATA_DIR,1,
                                        '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
            infolist = parseMovieFile(file)
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

    if config.TV_SHOW_DATA_DIR:
        for file in util.recursefolders(config.TV_SHOW_DATA_DIR,1,
                                        '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
            infolist = parseMovieFile(file)
            for info in infolist:
                k = os.path.splitext(os.path.basename(file))[0]
                config.TV_SHOW_INFORMATIONS[k] = (info.image, info.info,
                                                  info.mplayer_options, file)
            
    _debug_('done',2)
    return 1
