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
# Revision 1.3  2003/11/30 14:41:10  dischi
# use new Mimetype plugin interface
#
# Revision 1.2  2003/11/25 19:00:52  dischi
# make fxd item parser _much_ simpler
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


from videoitem import VideoItem


def parse_movie(fxd, node):
    """
    Callback for VideoItem <movie>

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

    def parse_video_child(fxd, node, item, dirname):
        """
        parse a subitem from <video>
        """
        filename   = fxd.gettext(node)
        mode       = node.name
        id         = fxd.getattr(node, 'id')
        media_id   = fxd.getattr(node, 'media_id')
        options    = fxd.getattr(node, 'mplayer_options')

        duplicates = fxd.getattr(None, 'duplicate_check', [])

        if mode == 'file':
            filename   = vfs.join(dirname, filename)

            # mark the files we include in the fxd in _fxd_covered_
            if not hasattr(item, '_fxd_covered_'):
                item._fxd_covered_ = []
            if filename and not filename in item._fxd_covered_:
                item._fxd_covered_.append(filename)
            # remove them from the filelist (if given)
            if filename in duplicates:
                duplicates.remove(filename)

        return id, filename, mode, media_id, options
    

    item = VideoItem('', fxd.getattr(None, 'parent', None), parse=False)

    fxd_file = fxd.getattr(None, 'filename', '')
    dirname  = vfs.dirname(fxd_file)
    
    item.name  = fxd.getattr(node, 'title')
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        item.image = vfs.join(dirname, item.image)

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
            info = parse_video_child(fxd, v, item, dirname)
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
            item.mplayer_options = parse_video_child(fxd, video[0], item, dirname)
        # global <video> mplayer_options
        if mplayer_options:
            item.mplayer_options += mplayer_options

    else:
        # a list of files
        for s in video:
            info = parse_video_child(fxd, s, item, dirname)
            v = VideoItem(info[1], parent=item, parse=False)
            v.mode, v.media_id, v.mplayer_options = info[2:]
            # global <video> mplayer_options
            if mplayer_options:
                v.mplayer_options += mplayer_options
            item.subitems.append(v)
        
    item.xml_file = fxd_file
    fxd.getattr(None, 'items', []).append(item)




    
def parse_disc_set(fxd, node):
    """
    Callback for VideoItem <disc-set>
    """
    item = VideoItem('', fxd.getattr(None, 'parent', None), parse=False)

    fxd_file = fxd.getattr(None, 'filename', '')
    dirname  = vfs.dirname(fxd_file)
    
    item.name  = fxd.getattr(node, 'title')
    item.image = fxd.childcontent(node, 'cover-img')
    if item.image:
        item.image = vfs.join(dirname, item.image)

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
    item.xml_file = fxd_file
    fxd.getattr(None, 'items', []).append(item)
