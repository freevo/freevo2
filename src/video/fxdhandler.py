# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxdhandler - handler for <movie> and <disc-set> tags in a fxd file
# -----------------------------------------------------------------------------
# $Id$
#
# This file contains the parser for the <movie> and <disc-set> tags
#
# <?xml version="1.0" ?>
# <freevo>
#     <movie title="">
#         <cover-img>file</cover-img>
#         <video>
#             <dvd|vcd|file id name media_id mplayer_options>file</>+
#         <variants>
#             <variant>
#                 <part ref mplayer_options>
#                     <subtitle media_id>file</subtitle>
#                     <audio media_id>file</audio>
#                 </part>+
#             </variant>+
#         </variants>
#         <info/>
#     </movie>
#
# <?xml version="1.0" ?>
# <freevo>
#     <disc-set title="">
#         <disc media-id="id"/>
#         <cover-img source="url">file</cover-img>
#         <info/>
#     </disc-set>
# </freevo>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Unknown
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
# -----------------------------------------------------------------------------


__all__ = [ 'parse_movie', 'parse_disc_set' ]

# python imports
import os
import logging

# kaa imports
from kaa.strutils import unicode_to_str
import kaa.beacon

# freevo imports
from videoitem import VideoItem
from menu import Files

# get logging object
log = logging.getLogger('video')

def parse_movie(name, title, image, info, node, parent, listing):
    """
    Callback for VideoItem <movie>
    """
    # a list of all files covered by this node
    files = []
    for c in node.children:
        if c.name == 'video':
            for f in c.children:
                if f.name == 'file':
                    filename = unicode_to_str(f.content)

                    # FIXME: make this faster
                    for f in listing.get('beacon:all'):
                        if f.get('name') == filename:
                            files.append(f)
                            break
                            
                    # Remove from listing to hide in VideoItem
                    # FIXME: make this faster
                    ext = os.path.splitext(filename)[1][1:]
                    for key in (ext, 'beacon:video'):
                        for f in listing.get(key):
                            if f.get('name') == filename:
                                listing.get(key).remove(f)
                                break
                            
    if len(files) > 1:
        log.error('BEACON_FIXME: VideoItem with more than one file')
        files = [ files[0] ]

    if len(files) == 0:
        log.error('BEACON_FIXME: VideoItem with bad file \n%s', node)
        return None

    item = VideoItem(files[0], parent)
    # BEACON_FIXME: add info from <info>
    if title:
        item.set_name(title)

    # BEACON_FIXME: item.files.fxd_file  = fxd.filename
    if image:
        item.image = image
        # BEACON_FIXME: item.files.image = image

    return item



def parse_disc_set(fxd, node):
    """
    Callback for VideoItem <disc-set>
    """
    item = VideoItem('', fxd.getattr(None, 'parent', None))

    dirname  = os.path.dirname(fxd.filename)

    item.name  = fxd.getattr(node, 'title')
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        # BEACON_FIXME:
        item.image = os.path.join(dirname, item.image)

    fxd.parse_info(node, item, {'length': 'runtime'})
    item.__fxd_rom_info__      = True
    item.__fxd_rom_label__     = []
    item.__fxd_rom_id__        = []
    item.__fxd_files_options__ = []
    for disc in fxd.get_children(node, 'disc'):
        id = fxd.getattr(disc, 'media-id')
        if id:
            item.__fxd_rom_id__.append(id)

        label = fxd.getattr(disc, 'label-regexp')
        if label:
            item.__fxd_rom_label__.append(label)

        # what to do with the mplayer_options? We can't use them for
        # one disc, or can we? And file_ops? Also only on a per disc base.
        # Answer: it applies to all the files of the disc, unless there
        #         are <file-opt> which specify to what files the
        #         mplayer_options apply. <file-opt> is not such a good
        #         name,  though.
        # So I ignore that we are in a disc right now and use the 'item'
        item.mplayer_options = fxd.getattr(disc, 'mplayer-options')
        there_are_file_opts = 0
        for f in fxd.get_children(disc, 'file-opt'):
            there_are_file_opts = 1
            file_media_id = fxd.getattr(f, 'media-id')
            if not file_media_id:
                file_media_id = id
            mpl_opts = item.mplayer_options + ' ' + \
                       fxd.getattr(f, 'mplayer-options')
            opt = { 'file-id' : file_media_id + fxd.gettext(f),
                    'mplayer-options': mpl_opts }
            item.__fxd_files_options__.append(opt)
        if there_are_file_opts:
            # in this case, the disc/@mplayer_options is retricted to the set
            # of files defined in the file-opt elements
            item.mplayer_options = ''

    if not item.files:
        item.files = Files()
    item.files.fxd_file  = fxd.filename
    fxd.getattr(None, 'items', []).append(item)
