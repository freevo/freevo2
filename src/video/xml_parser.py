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
# Revision 1.45  2003/11/23 16:59:16  dischi
# Complete rewrite to use the new fxdparser. I didn't wanted to do this,
# it just happened :-)
# I hope all functions are still in there, maybe someone can rewrite the
# imdb grabber to use the new fxd class to also write the fxd file.
#
# Revision 1.44  2003/11/22 21:26:42  dischi
# fix search bug
#
# Revision 1.43  2003/11/22 20:35:50  dischi
# use new vfs
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
import copy

import config
import util

from xml.utils import qp_xml
from videoitem import VideoItem




class MovieParser:
    """
    Class to parse a movie informations from a fxd file
    """
    def __init__(self, parser, filename, parent, duplicate_check):
        self.items    = []
        self.parent   = parent
        self.dirname  = vfs.dirname(vfs.normalize(filename))
        self.filename = filename
        self.duplicate_check = duplicate_check
        parser.set_handler('movie', self.parse)
        parser.set_handler('disc-set', self.parse)


    def parse(self, fxd, node):
        """
        Callback from the fxd parser. Create a VideoItem (since it should handle
        the information and use it's callback function to jump back into this
        class to fill the structure in __init__. So we jump:
        fxd -> MovieParser.parse -> VideoItem.__init__ -> MovieParser.XXX
        """
        v = None
        
        if node.name == 'movie':
            v = VideoItem((fxd, node, self.parse_movie), self.parent, parse=False)
        elif node.name == 'disc-set':
            v = VideoItem((fxd, node, self.parse_disc_set), self.parent, parse=False)
        if v:
            v.xml_file = self.filename
            self.items.append(v)

    def parse_video_child(self, fxd, node):
        """
        parse a subitem from <video>
        """
        filename = fxd.gettext(node)
        filename = vfs.join(self.dirname, filename)
        mode     = node.name
        id       = fxd.getattr(node, 'id')
        media_id = fxd.getattr(node, 'media_id')
        options  = fxd.getattr(node, 'mplayer_options')

        if mode == 'file':
            if not hasattr(self.item, '_fxd_covered_'):
                self.item._fxd_covered_ = []
            if filename and not filename in self.item._fxd_covered_:
                self.item._fxd_covered_.append(filename)
            if filename in self.duplicate_check:
                self.duplicate_check.remove(filename)
            
        return id, filename, mode, media_id, options

    
    def parse_movie(self, fxd, node, item):
        """
        Callback from VideoItem for <movie>

        <movie title>
          <cover-img>file</cover-img>
          <video>
            <dvd|vcd|file id name media_id mplayer_options>file</>+
          <variants>
            <variant>
              <part ref mplayer_options/>
              <subtitle media_id>file</subtitle>
              <audio media_id>file</audio>
            </variant>
          </variants>  
          <info>
        </movie>
        """
        self.item  = item
        item.name  = fxd.getattr(node, 'title')
        item.image = fxd.childcontent(node, 'cover-img')
        if item.image:
            item.image = vfs.join(self.dirname, item.image)
            
        fxd.parse_info(fxd.get_children(node, 'info', 1), item, {'runtime': 'length'})

        video = fxd.get_children(node, 'video')
        if video:
            mplayer_options = fxd.getattr(video[0], 'mplayer_options')
            video = fxd.get_children(video[0], 'file') + \
                    fxd.get_children(video[0], 'vcd') + \
                    fxd.get_children(video[0], 'dvd')

        variants = fxd.get_children(node, 'variants')
        if variants:
            variants = fxd.get_children(variants[0], 'variant')

        if variants:
            # a list of variants
            id = {}
            for v in video:
                info = self.parse_video_child(fxd, v)
                id[info[0]] = info

            for variant in variants:
                audio    = fxd.get_children(variant, 'audio')
                subtitle = fxd.get_children(variant, 'subtitle')

                if audio:
                    audio = { 'media_id': fxd.getattr(audio[0], 'media_id'),
                              'file'    : fxd.gettext(audio[0]) }
                else:
                    audio = {}
                    
                if subtitle:
                    subtitle = { 'media_id': fxd.getattr(subtitle[0], 'media_id'),
                                 'file'    : fxd.gettext(subtitle[0]) }
                else:
                    subtitle = {}
                    
                parts = fxd.get_children(variant, 'part')
                if len(parts) == 1:
                    # a variant with one file
                    ref = fxd.getattr(parts[0] ,'ref')
                    v = VideoItem(id[ref][1], parent=item, parse=False)
                    v.mode, v.media_id, v.mplayer_options = id[ref][2:]

                    v.subtitle_file = subtitle
                    v.audio_file    = audio

                    # global <video> mplayer_options
                    if mplayer_options:
                        v.mplayer_options += mplayer_options
                else:
                    # a variant with a list of files
                    v = VideoItem('', parent=item, parse=False)
                    v.subtitle_file = subtitle
                    v.audio_file    = audio
                    for p in parts:
                        ref = fxd.getattr(p ,'ref')
                        sub = VideoItem(id[ref][1], parent=v, parse=False)
                        sub.mode, sub.media_id, sub.mplayer_options = id[ref][2:]
                        # global <video> mplayer_options
                        if mplayer_options:
                            sub.mplayer_options += mplayer_options
                        v.subitems.append(sub)
                        
                v.name = fxd.getattr(variant, 'name')
                item.variants.append(v)
                
        elif len(video) == 1:
            # only one file, this is directly for the item
            id, item.filename, item.mode, item.media_id, \
                item.mplayer_options = self.parse_video_child(fxd, video[0])
            # global <video> mplayer_options
            if mplayer_options:
                item.mplayer_options += mplayer_options

        else:
            # a list of files
            for s in video:
                info = self.parse_video_child(fxd, s)
                v = VideoItem(info[1], parent=item, parse=False)
                v.mode, v.media_id, v.mplayer_options = info[2:]
                # global <video> mplayer_options
                if mplayer_options:
                    v.mplayer_options += mplayer_options
                item.subitems.append(v)
        


    def parse_disc_set(self, fxd, node, item):
        """
        Callback from VideoItem for <disc-set>
        """
        item.name  = fxd.getattr(node, 'title')
        item.image = fxd.childcontent(node, 'cover-img')
        if item.image:
            item.image = vfs.join(self.dirname, item.image)

        fxd.parse_info(fxd.get_children(node, 'info', 1), item, {'runtime': 'length'})
        item.rom_label = []
        item.rom_id    = []
        
        for disc in fxd.get_children(node, 'disc'):
            id = fxd.getattr(disc, 'media-id')
            if id:
                item.rom_id.append(id)
                
            label = fxd.getattr(disc, 'label-regexp')
            if label:
                item.rom_label.append(label)

            # what to do with the mplayer_options? We can't use them for
            # one disc, or can we? And file_ops? Also only on a per disc base.
            # So I ignore that we are in a disc right now and use the 'item'
            item.mplayer_options = fxd.getattr(disc, 'mplayer_options')
            for f in fxd.get_children(disc, 'file-opts'):
                opt = { 'file-d': f.getattr(f, 'media-id'),
                        'mplayer_options': f.getattr(f, 'mplayer_options') }
                item.files_options.append(opt)

        

def parseMovieFile(filename, parent=None, duplicate_check=[]):
    """
    parse a XML movie file

    Returns:
      a list of VideoItems,
      each VideoItem possibly contains a list of VideoItems
    """
    try:
        # create a basic fxd parser
        parser = util.fxdparser.FXD(filename)

        # create an object that can parse the movie infos out of an fxd
        mp = MovieParser(parser, filename, parent, duplicate_check)

        # start the parsing
        parser.parse()

        # now mp contains the list of items, return it
        return mp.items

    except:
        print "fxd file %s corrupt" % file
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
    
    if vfs.exists("/tmp/freevo-rebuild-database"):
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

    files = []
    if not config.ONLY_SCAN_DATADIR:
        for name,dir in config.DIR_MOVIES:
            files += util.recursefolders(dir,1,'*'+config.SUFFIX_VIDEO_DEF_FILES[0],1)
    if config.OVERLAY_DIR:
        for subdir in ('disc', 'disc-set'):
            files += util.recursefolders(vfs.join(config.OVERLAY_DIR, subdir),
                                         1, '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1)

    for file in files:
        for info in parseMovieFile(file):
            config.MOVIE_INFORMATIONS += [ info ]
            for i in info.rom_id:
                config.MOVIE_INFORMATIONS_ID[i] = info
            for l in info.rom_label:
                l_re = re.compile(l)
                config.MOVIE_INFORMATIONS_LABEL += [(l_re, info)]
            for fo in info.files_options:
                config.DISC_SET_INFORMATIONS_ID[fo['file-id']] = fo['mplayer-options']

    if config.TV_SHOW_DATA_DIR:
        for file in util.recursefolders(config.TV_SHOW_DATA_DIR,1,
                                        '*'+config.SUFFIX_VIDEO_DEF_FILES[0],1):
            for info in parseMovieFile(file):
                k = vfs.splitext(vfs.basename(file))[0]
                config.TV_SHOW_INFORMATIONS[k] = (info.image, info.info,
                                                  info.mplayer_options, file)
            
    _debug_('done',2)
    return 1
