#if 0 /*
# -----------------------------------------------------------------------
# fxdhandler - handler for <movie> and <disc-set> tags in a fxd file
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.20  2004/05/13 12:50:21  dischi
# fix duplicate removal for fxd files in vfs
#
# Revision 1.19  2004/03/02 20:56:59  dischi
# fxd files are always right about the name
#
# Revision 1.18  2004/02/14 12:59:26  dischi
# make sure url is a string
#
# Revision 1.17  2004/02/08 05:33:30  outlyer
# Removed some debug print.
#
# Revision 1.16  2004/02/03 20:51:12  dischi
# fix/enhance dvd on disc
#
# Revision 1.15  2004/02/01 19:47:13  dischi
# some fixes by using new mmpython data
#
# Revision 1.14  2004/01/19 20:20:35  dischi
# fix missing url problem
#
# Revision 1.13  2004/01/17 20:30:19  dischi
# use new metainfo
#
# Revision 1.12  2004/01/10 13:22:17  dischi
# reflect self.fxd_file changes
#
# Revision 1.11  2004/01/04 11:16:53  dischi
# do not override image with nothing
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


from videoitem import VideoItem
from item import FileInformation
import os

def parse_movie(fxd, node):
    """
    Callback for VideoItem <movie>

    <movie title>
        <cover-img>file</cover-img>
        <video>
            <dvd|vcd|file id name media_id mplayer_options>file</>+
        <variants>
            <variant>
                <part ref mplayer_options>
                    <subtitle media_id>file</subtitle>
                    <audio media_id>file</audio>
                </part>+
            </variant>+
        </variants>  
        <info/>
    </movie>
    """

    files = []
    
    def parse_video_child(fxd, node, dirname):
        """
        parse a subitem from <video>
        """
        filename   = String(fxd.gettext(node))
        media_id   = fxd.getattr(node, 'media-id')
        mode       = node.name
        id         = fxd.getattr(node, 'id')
        options    = fxd.getattr(node, 'mplayer-options')
        player     = fxd.childcontent(node, 'player')
        playlist   = False

        if fxd.get_children(node, 'playlist'):
            playlist = True

        if mode == 'file':
            if not media_id:
                filename = os.path.join(dirname, filename)
                if vfs.isoverlay(filename):
                    filename = vfs.normalize(filename)
            if filename and not filename in files:
                files.append(filename)
        if mode == 'url':
            return id, filename, media_id, options, player, playlist
        return id, String('%s://%s' % (mode, filename)), media_id, options, player, playlist
    

    item = VideoItem('', fxd.getattr(None, 'parent', None), parse=False)

    dirname  = os.path.dirname(fxd.filename)
    image      = ''
    title      = fxd.getattr(node, 'title')
    item.name  = title
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        item.image = os.path.join(dirname, item.image)
        image = item.image
        
    fxd.parse_info(node, item, {'runtime': 'length'})

    video = fxd.get_children(node, 'video')
    if video:
        mplayer_options = fxd.getattr(video[0], 'mplayer_options')
        video = fxd.get_children(video[0], 'file') + \
                fxd.get_children(video[0], 'vcd') + \
                fxd.get_children(video[0], 'dvd') + \
                fxd.get_children(video[0], 'url')

    variants = fxd.get_children(node, 'variants')
    if variants:
        variants = fxd.get_children(variants[0], 'variant')

    if variants:
        # a list of variants
        id = {}
        for v in video:
            video_child = parse_video_child(fxd, v, dirname)
            id[video_child[0]] = video_child

        for variant in variants:
            mplayer_options += " " + fxd.getattr(variant, 'mplayer-options');
            parts = fxd.get_children(variant, 'part')
            if len(parts) == 1:
                # a variant with one file
                ref = fxd.getattr(parts[0] ,'ref')
                v = VideoItem(id[ref][1], parent=item, info=item.info, parse=False)
                v.files = None
                v.media_id, v.mplayer_options, player, is_playlist = id[ref][2:]
                if player:
                    v.force_player = player
                if is_playlist:
                    v.is_playlist  = True

                audio    = fxd.get_children(parts[0], 'audio')
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
                    subtitle = { 'media_id': fxd.getattr(subtitle[0], 'media-id'),
                                 'file'    : fxd.gettext(subtitle[0]) }
                    if not subtitle['media_id']:
                        subtitle['file'] = os.path.join(dirname, subtitle['file'])
                else:
                    subtitle = {}
                v.subtitle_file = subtitle

                # global <video> mplayer_options
                if mplayer_options:
                    v.mplayer_options += mplayer_options
            else:
                # a variant with a list of files
                v = VideoItem('', parent=item, info=item.info, parse=False)
                for p in parts:
                    ref = fxd.getattr(p ,'ref')
                    audio    = fxd.get_children(p, 'audio')
                    subtitle = fxd.get_children(p, 'subtitle')
    
                    if audio:
                        audio = { 'media_id': fxd.getattr(audio[0], 'media-id'),
                                  'file'    : fxd.gettext(audio[0]) }
                        if not audio['media_id']:
                            audio['file'] = os.path.join(dirname, audio['file'])
                    else:
                        audio = {}
                        
                    if subtitle:
                        subtitle = { 'media_id': fxd.getattr(subtitle[0], 'media-id'),
                                     'file'    : fxd.gettext(subtitle[0]) }
                        if not subtitle['media_id']:
                            subtitle['file'] = os.path.join(dirname, subtitle['file'])
                    else:
                        subtitle = {}

                    sub = VideoItem(id[ref][1], parent=v, info=item.info, parse=False)
                    sub.files = None
                    sub.media_id, sub.mplayer_options, player, is_playlist = id[ref][2:]
                    sub.subtitle_file = subtitle
                    sub.audio_file    = audio
                    # global <video> mplayer_options
                    if mplayer_options:
                        sub.mplayer_options += mplayer_options
                    v.subitems.append(sub)
 
            v.name = fxd.getattr(variant, 'name')
            item.variants.append(v)

    elif len(video) == 1:
        # only one file, this is directly for the item
        id, url, item.media_id, item.mplayer_options, player, is_playlist = \
            parse_video_child(fxd, video[0], dirname)
        if url.startswith('file://') and os.path.isfile(url[7:]):
            variables = item.info.get_variables()
            item.set_url(url, info=True)
            item.info.set_variables(variables)
        elif url.startswith('file://') and os.path.isdir(url[7:]):
            # dvd dir
            variables = item.info.get_variables()
            item.set_url(url.replace('file://', 'dvd:/')+ '/VIDEO_TS/', info=True)
            item.info.set_variables(variables)
        else:
            item.set_url(url, info=False)
        if title:
            item.name = title
        if player:
            item.force_player = player
        if is_playlist:
            item.is_playlist  = True
        # global <video> mplayer_options
        if mplayer_options:
            item.mplayer_options += mplayer_options
    else:
        # a list of files
        for s in video:
            video_child = parse_video_child(fxd, s, dirname)
            v = VideoItem(video_child[1], parent=item, info=item.info, parse=False)
            v.files = None
            v.media_id, v.mplayer_options, player, is_playlist = video_child[2:]
            if video_child[-2]:
                v.force_player = video_child[-2]
            if video_child[-1]:
                item.is_playlist = True
            # global <video> mplayer_options
            if mplayer_options:
                v.mplayer_options += mplayer_options
            item.subitems.append(v)

    if not item.files:
        item.files = FileInformation()
    item.files.files     = files

    item.files.fxd_file  = fxd.filename
    if image:
        item.files.image = image
    
    # remove them from the filelist (if given)
    duplicates = fxd.getattr(None, 'duplicate_check', [])
    for f in files:
        try:
            duplicates.remove(f)
        except:
            pass
        
    if fxd.is_skin_fxd:
        item.skin_fxd = fxd.filename
    fxd.getattr(None, 'items', []).append(item)





def parse_disc_set(fxd, node):
    """
    Callback for VideoItem <disc-set>
    """
    item = VideoItem('', fxd.getattr(None, 'parent', None), parse=False)

    dirname  = os.path.dirname(fxd.filename)
    
    item.name  = fxd.getattr(node, 'title')
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        item.image = os.path.join(dirname, item.image)

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
            mpl_opts = item.mplayer_options + ' ' + fxd.getattr(f, 'mplayer-options')
            opt = { 'file-id' : file_media_id + fxd.gettext(f),
                    'mplayer-options': mpl_opts }
            item.__fxd_files_options__.append(opt)
        if there_are_file_opts:
            # in this case, the disc/@mplayer_options is retricted to the set
            # of files defined in the file-opt elements
            item.mplayer_options = ''
    
    if not item.files:
        item.files = FileInformation()
    item.files.fxd_file  = fxd.filename
    if fxd.is_skin_fxd:
        item.skin_fxd = fxd.filename
    fxd.getattr(None, 'items', []).append(item)
