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

# freevo imports
from videoitem import VideoItem
from menu import Files

# get logging object
log = logging.getLogger('video')

class VideoChild(object):
    """
    Objects of this class contain a parsed a subitem from <video>
    """
    def __init__(self, fxd, node, dirname, files):
        self.filename = String(fxd.gettext(node))
        self.media_id = fxd.getattr(node, 'media-id')
        self.mode     = node.name
        self.id       = fxd.getattr(node, 'id')
        self.options  = fxd.getattr(node, 'mplayer-options')
        self.player   = fxd.childcontent(node, 'player')
        self.is_playlist = False

        if fxd.get_children(node, 'playlist'):
            self.is_playlist = True

        if self.mode == 'file':
            if not self.media_id:
                fullname = os.path.join(dirname, self.filename)
            if fullname and not fullname in files:
                files.append(fullname)
        if self.mode == 'url':
            self.url = self.filename
        else:
            self.url = '%s://%s' % (String(self.mode), String(fullname))

    def set_to_item(self, item):
        """
        Set some attributes from the video child to the given item. This
        functionw ill set media_id, mplayer_options, force_player and
        is_playlist.
        """
        item.media_id = self.media_id
        item.mplayer_options = self.options
        if self.player:
            item.force_player = self.player
        if self.is_playlist:
            item.is_playlist = True


    def get_url(self, listing):
        """
        Return the url as string or the ItemInfo from listing.
        """
        if not self.url.startswith('file://'):
            return self.url
        if os.path.isfile(self.url[7:]):
            if self.filename.find('/') == -1:
                return listing.get_by_name(self.filename)
            else:
                # FIXME:
                return self.url
        if os.path.isdir(self.url[7:]):
            # FIXME: dvd dir
            return self.url.replace('file://', 'dvd:/') + \
                   '/VIDEO_TS/'
        # Oops, not found
        log.info('unknown file %s' % (String(self.url)))
        return ''

        
def parse_movie(fxd, node):
    """
    Callback for VideoItem <movie>
    """
    listing = fxd.getattr(None, 'listing', [])
    dirname = os.path.dirname(fxd.filename)

    # a list of all files covered by this <video> node
    files = []

    # create an item
    item = VideoItem('', fxd.getattr(None, 'parent', None))
    # add info from <info>
    fxd.parse_info(node, item, {'runtime': 'length'})

    video_list = []
    video = fxd.get_children(node, 'video')
    if video:
        mplayer_options = fxd.getattr(video[0], 'mplayer_options')
        children = fxd.get_children(video[0], 'file') + \
                   fxd.get_children(video[0], 'vcd') + \
                   fxd.get_children(video[0], 'dvd') + \
                   fxd.get_children(video[0], 'url')
        for child in children:
            video_list.append(VideoChild(fxd, child, dirname, files))

    variants = fxd.get_children(node, 'variants')

    if variants:
        variants = fxd.get_children(variants[0], 'variant')
        # a list of variants
        id = {}
        for video in video_list:
            id[video.id] = video

        for variant in variants:
            mplayer_options += " " + fxd.getattr(variant, 'mplayer-options');
            parts = fxd.get_children(variant, 'part')
            if len(parts) == 1:
                # a variant with one file
                ref = fxd.getattr(parts[0] ,'ref')
                video = id[ref]
                v = VideoItem(video.get_url(listing), parent=item)
                v.info.set_variables(item.info)
                video.set_to_item(v)

                audio = fxd.get_children(parts[0], 'audio')
                if audio:
                    audio = { 'media_id': fxd.getattr(audio[0], 'media-id'),
                              'file'    : fxd.gettext(audio[0]) }
                    if not audio['media_id']:
                        audio['file'] = os.path.join(dirname, audio['file'])
                else:
                    audio = {}
                v.audio_file    = audio

                subtitle = fxd.get_children(parts[0], 'subtitle')
                if subtitle:
                    subtitle = { 'media_id': fxd.getattr(subtitle[0],
                                                         'media-id'),
                                 'file'    : fxd.gettext(subtitle[0]) }
                    if not subtitle['media_id']:
                        subtitle['file'] = os.path.join(dirname,
                                                        subtitle['file'])
                else:
                    subtitle = {}
                v.subtitle_file = subtitle

                # global <video> mplayer_options
                if mplayer_options:
                    v.mplayer_options += mplayer_options
            else:
                # a variant with a list of files
                v = VideoItem('', parent=item)
                v.info.set_variables(item.info)
                for p in parts:
                    ref = fxd.getattr(p ,'ref')
                    video = id[ref]

                    audio    = fxd.get_children(p, 'audio')
                    subtitle = fxd.get_children(p, 'subtitle')

                    if audio:
                        audio = audio[0]
                        audio = { 'media_id': fxd.getattr(audio, 'media-id'),
                                  'file'    : fxd.gettext(audio) }
                        if not audio['media_id']:
                            audio['file'] = os.path.join(dirname,
                                                         audio['file'])
                    else:
                        audio = {}

                    if subtitle:
                        subtitle = { 'media_id': fxd.getattr(subtitle[0],
                                                             'media-id'),
                                     'file'    : fxd.gettext(subtitle[0]) }
                        if not subtitle['media_id']:
                            subtitle['file'] = os.path.join(dirname,
                                                            subtitle['file'])
                    else:
                        subtitle = {}

                    sub = VideoItem(video.get_url(listing), parent=v)
                    sub.info.set_variables(item.info)
                    sub.files = None
                    video.set_to_item(sub)

                    sub.subtitle_file = subtitle
                    sub.audio_file    = audio
                    # global <video> mplayer_options
                    if mplayer_options:
                        sub.mplayer_options += mplayer_options
                    v.subitems.append(sub)

            v.name = fxd.getattr(variant, 'name')
            item.variants.append(v)

    elif len(video_list) == 1:
        # only one file, this is directly for the item
        video = video_list[0]
        video.set_to_item(item)
        variables = item.info.get_variables()
        item.set_url(video.get_url(listing))
        item.info.set_variables(variables)

        # global <video> mplayer_options
        if mplayer_options:
            item.mplayer_options += mplayer_options

    else:
        # a list of files
        for video in video_list:
            v = VideoItem(video.get_url(listing), parent=item)
            v.info.set_variables(item.info)
            v.files = None
            video.set_to_item(v)
            # global <video> mplayer_options
            if mplayer_options:
                v.mplayer_options += mplayer_options
            item.subitems.append(v)


    title = fxd.getattr(node, 'title')
    if title:
        item.set_name(title)

    if not item.files:
        item.files = Files()

    item.files.files     = files
    item.files.fxd_file  = fxd.filename

    image = fxd.childcontent(node, 'cover-img')
    if image:
        item.image = vfs.abspath(os.path.join(dirname, image))
        item.files.image = image

    # remove them from the filelist (if given)
    for f in files:
        try:
            listing.remove(f)
        except:
            pass

    if fxd.is_skin_fxd:
        item.skin_fxd = fxd.filename
    fxd.getattr(None, 'items', []).append(item)





def parse_disc_set(fxd, node):
    """
    Callback for VideoItem <disc-set>
    """
    item = VideoItem('', fxd.getattr(None, 'parent', None))

    dirname  = os.path.dirname(fxd.filename)

    item.name  = fxd.getattr(node, 'title')
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        item.image = vfs.abspath(os.path.join(dirname, item.image))

    fxd.parse_info(node, item, {'runtime': 'length'})
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
    if fxd.is_skin_fxd:
        item.skin_fxd = fxd.filename
    fxd.getattr(None, 'items', []).append(item)
