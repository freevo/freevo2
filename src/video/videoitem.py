#if 0 /*
# -----------------------------------------------------------------------
# videoitem.py - Item for video objects
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.86  2003/09/20 15:08:26  dischi
# some adjustments to the missing testfiles
#
# Revision 1.85  2003/09/20 12:59:31  dischi
# do not match urls as tv shows
#
# Revision 1.84  2003/09/20 09:50:07  dischi
# cleanup
#
# Revision 1.83  2003/09/19 22:10:56  dischi
# clear osd before playing with xine
#
# Revision 1.82  2003/09/14 20:09:37  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.81  2003/09/13 10:08:23  dischi
# i18n support
#
# Revision 1.80  2003/08/31 17:14:20  dischi
# Move delete file from VideoItem into a global plugin. Now it's also
# possible to remove audio and image files.
#
# Revision 1.79  2003/08/30 17:05:41  dischi
# remove bookmark support, add support for ItemPlugin eventhandler
#
# Revision 1.78  2003/08/30 12:21:13  dischi
# small changes for the changed xml_parser
#
# Revision 1.77  2003/08/23 18:33:03  dischi
# use util.getimage to get the cover image file
#
# Revision 1.76  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
#
# Revision 1.75  2003/08/23 10:28:47  dischi
# fixed some variants handling
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
import md5
import time
import copy
import mmpython

import config
import util
import rc
import menu
import configure
import plugin

from gui.PopupBox import PopupBox
from gui.AlertBox import AlertBox
from gui.ConfirmBox import ConfirmBox

from item import Item
from event import *


class VideoItem(Item):
    def __init__(self, filename, parent, info=None):
        if parent and parent.media:
            url = 'cd://%s:%s:%s' % (parent.media.devicename, parent.media.mountdir,
                                     filename[len(parent.media.mountdir)+1:])
        else:
            url = filename
        Item.__init__(self, parent, mmpython.parse(url))

        # fix values
        self.type  = 'video'
        self.handle_type = 'video'

        self.mode  = 'file'             # file, dvd or vcd
        self.media_id = ''              # if media == vcd or dvd

        self.files_options = []         # options for specific files of a
                                        # disc in a disc-set

        self.variants = []              # if this item has variants
        self.subitems = []              # if this item has more than one file/track to play
        self.current_subitem = None

        self.subtitle_file = {}         # text subtitles
        self.audio_file = {}            # audio dubbing

        self.filename = filename
        self.id       = filename
        self.item_id  = None
        
        if not self.name:
            self.name     = util.getname(filename)
        self.basename = os.path.basename(os.path.splitext(filename)[0])
        self.tv_show  = False
        self.mplayer_options = ''
        self.xml_file = None
        
        # find image for tv show and build new title
        if config.TV_SHOW_REGEXP_MATCH(self.name) and filename.find('://') == -1 and \
               config.TV_SHOW_DATA_DIR:
            show_name = config.TV_SHOW_REGEXP_SPLIT(self.name)
            if show_name[0] and show_name[1] and show_name[2] and show_name[3]:
                self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                            " - " + show_name[3]
                self.image = util.getimage((config.TV_SHOW_DATA_DIR + \
                                            show_name[0].lower()), self.image)

                if config.TV_SHOW_INFORMATIONS.has_key(show_name[0].lower()):
                    tvinfo = config.TV_SHOW_INFORMATIONS[show_name[0].lower()]
                    for i in tvinfo[1]:
                        self.info[i] = tvinfo[1][i]
                    if not self.image:
                        self.image = tvinfo[0]
                    if not self.xml_file:
                        self.xml_file = tvinfo[3]
                    self.mplayer_options = tvinfo[2]

                self.tv_show = True
                self.show_name = show_name
            
        # find image for this file
        # First check in COVER_DIR
        if config.COVER_DIR:
            self.image = util.getimage(config.COVER_DIR+self.basename, self.image)

        # Then check for episode in TV_SHOW_DATA_DIR
        self.image = util.getimage(os.path.splitext(filename)[0], self.image)

        self.video_player = plugin.getbyname(plugin.VIDEO_PLAYER)

        # variables only for VideoItem
        self.label = ''
        
        self.available_audio_tracks = []
        self.available_subtitles    = []
        self.available_chapters     = 0
        self.video_width  = 0
        self.video_height = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0
        self.deinterlace       = 0
        self.elapsed           = 0
        
        if parent and hasattr(self.parent, 'xml_file') and not self.xml_file:
            self.xml_file = self.parent.xml_file

        
        
    def copy(self, obj):
        """
        Special copy value VideoItems
        """
        Item.copy(self, obj)
        if obj.type == 'video':
            self.available_audio_tracks = obj.available_audio_tracks
            self.available_subtitles    = obj.available_subtitles
            self.available_chapters     = obj.available_chapters

            self.selected_subtitle = obj.selected_subtitle
            self.selected_audio    = obj.selected_audio
            self.num_titles        = obj.num_titles
            self.label             = obj.label
            self.tv_show           = obj.tv_show
            self.id                = obj.id
            
            self.variants          = obj.variants
            self.subitems          = obj.subitems
            self.files_options     = obj.files_options
            self.current_subitem   = obj.current_subitem
            self.subtitle_file     = obj.subtitle_file
            self.audio_file        = obj.audio_file
            self.filename          = obj.filename




    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'item_id':
            if self.item_id:
                return self.item_id
            
            if self.media:
                filename = self.filename[len(self.media.mountdir):]
                id = 'cd://%s-%s' % (self.media.id, filename)
            else:
                id = 'file://%s' % self.filename
            if self.subitems:
                for s in self.subitems:
                    id += s.getattr(attr)
            if self.variants:
                for v in self.variants:
                    id += v.getattr(attr)
                    
            self.item_id = util.hexify(md5.new(id).digest())
            return self.item_id
        
        if attr in ('length', 'geometry', 'aspect'):
            try:
                video = self.info.video[0]
                if attr == 'length':
                    length = video.length
                    if length / 3600:
                        return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60,
                                                  length % 60)
                    else:
                        return '%d:%02d' % (length / 60, length % 60)
                if attr == 'geometry':
                    return '%sx%s' % (video.width, video.height)
                if attr == 'aspect':
                    aspect = getattr(video, attr)
                    return aspect[:aspect.find(' ')].replace('/', ':')
            except:
                pass
        return Item.getattr(self, attr)

    
    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and os.path.isfile(self.filename):
            return '%s%s' % (os.stat(self.filename).st_ctime, self.filename)

        if self.name.find("The ") == 0:
            return self.name[4:]
        return self.name

    
    # ------------------------------------------------------------------------
    # actions:


    def actions(self):
        """
        return a list of possible actions on this item.
        """
        items = [ (self.play, 'Play'), ]
        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                if plugin.getbyname(plugin.DVD_PLAYER):
                    items = [ (self.play, _('Play DVD')),
                              ( self.dvd_vcd_title_menu, 'DVD title list' ) ]
                else:
                    items = [ ( self.dvd_vcd_title_menu, 'DVD title list' ),
                              (self.play, 'Play default track') ]
                    
            elif self.mode == 'vcd':
                if plugin.getbyname(plugin.VCD_PLAYER):
                    items = [ (self.play, _('Play VCD')),
                              ( self.dvd_vcd_title_menu, 'VCD title list' ) ]
                else:
                    items = [ ( self.dvd_vcd_title_menu, 'VCD title list' ),
                              (self.play, _('Play default track')) ]


        items += configure.get_items(self)
 
        if self.variants and len(self.variants) > 1:
            items = [ (self.show_variants, 'Show variants') ] + items

        return items


    def show_variants(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        m = menu.Menu(self.name, self.variants, reload_func=None, xml_file=self.xml_file)
        m.item_types = 'video'
        self.menuw.pushmenu(m)


    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        self.plugin_eventhandler(PLAY, menuw)

        # dvd playback for whole dvd
        if (not self.filename or self.filename == '0') and \
               self.mode == 'dvd' and plugin.getbyname(plugin.DVD_PLAYER):
            if self.menuw.visible:
                self.menuw.hide()
            plugin.getbyname(plugin.DVD_PLAYER).play(self)
            return

        # vcd playback for whole vcd
        if (not self.filename or self.filename == '0') and \
               self.mode == 'vcd' and plugin.getbyname(plugin.VCD_PLAYER):
            if self.menuw.visible:
                self.menuw.hide()
            plugin.getbyname(plugin.VCD_PLAYER).play(self)
            return

        # if we have variants, play the first one as default
        if self.variants:
            self.variants[0].play(arg, menuw)
            return

        # if we have subitems (a movie with more than one file),
        # we start playing the first
        if self.subitems:
            self.current_subitem = self.subitems[0]
            # Pass along the options, without loosing the subitem's own
            # options
            if self.current_subitem.mplayer_options:
                if self.mplayer_options:
                    self.current_subitem.mplayer_options += ' ' + self.mplayer_options
            else:
                self.current_subitem.mplayer_options = self.mplayer_options
            # When playing a subitem, the menu must be hidden. If it is not,
            # the playing will stop after the first subitem, since the
            # PLAY_END/USER_END event is not forwarded to the parent
            # videoitem.
            # And besides, we don't need the menu between two subitems.
            self.menuw.hide()

            self.current_subitem.play(arg, self.menuw)
            return


        # normal plackback of one file
        file = self.filename
        if self.mode == "file":
            if self.media_id:
                mountdir, file = util.resolve_media_mountdir(self.media_id,file)
                if mountdir:
                    util.mount(mountdir)
                else:
                    
                    def do_tryagain():                        
                        # TODO: force to identify media instead of wait
                        box = PopupBox( text=_("Wait while detecting media...") )
                        box.show()
                        l=1
                        for i in range( 10 ): # 10 times
                            
                            for media in config.REMOVABLE_MEDIA:
                                # media has no id? maybe identifying... wait
                                if not media.id:
                                    time.sleep( 2 )
                                if media.id == self.media_id:
                                    # we found it! Stop looping
                                    l=0
                                    break
                                
                            if not l:
                                break
                        box.destroy()
                                                    
                        self.play( arg, menuw )
                    # do_tryagain()
                        
                    
                    ConfirmBox( text=(_('Media not found for file "%s".\n')+
                                      _('Please insert the media.')) % file,
                                handler=do_tryagain ).show()
                    
                    rc.post_event( PLAY_END )

                    return

            elif self.media:
                util.mount(os.path.dirname(self.filename))

        elif self.mode == 'dvd' or self.mode == 'vcd':
            if not self.media:
                media = util.check_media(self.media_id)
                if media:
                    self.media = media
                else:
                    AlertBox(text=_('Media not found for %s track %s') % \
                             (self.mode, file)).show()
                    rc.post_event(PLAY_END)
                    return

        if not self.filename or self.filename == '0':
            if self.mode == 'dvd':
                file = '1'
            elif self.mode == 'vcd':
                # try to get the longest track:
                try:
                    import cdrom
                    device = open(self.media.devicename)
                    (first, last) = cdrom.toc_header(device)

                    lmin = 0
                    lsec = 0

                    mainmovie = (0, 0)
                    for i in range(first, last + 2):
                        if i == last + 1:
                            min, sec, frames = cdrom.leadout(device)
                        else:
                            min, sec, frames = cdrom.toc_entry(device, i)
                        if (min-lmin) * 60 + (sec-lsec) > mainmovie[0]:
                            mainmovie = (min-lmin) * 60 + (sec-lsec), i-1
                        lmin, lsec = min, sec
                    file = str(mainmovie[1])
                    device.close()
                except:
                    file = '1'

        mplayer_options = self.mplayer_options
        if not mplayer_options:
            mplayer_options = ""

        if self.media:
            mplayer_options += ' -cdrom-device %s ' % \
                               (self.media.devicename)

        if self.mode == 'dvd':
            mplayer_options += ' -dvd-device %s' % self.media.devicename


        if self.selected_subtitle and self.mode == 'file':
            mplayer_options += ' -vobsubid %s' % self.selected_subtitle
        elif self.selected_subtitle:
            mplayer_options += ' -sid %s' % self.selected_subtitle
            
        if self.selected_audio:
            mplayer_options += ' -aid %s' % self.selected_audio

        if self.subtitle_file:
            d, f = util.resolve_media_mountdir(self.subtitle_file['media-id'],
                                               self.subtitle_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -sub "%s"' % f

        if self.audio_file:
            d, f = util.resolve_media_mountdir(self.audio_file['media-id'],
                                               self.audio_file['file'])
            if d:
                util.mount(d)
            mplayer_options += ' -audiofile "%s"' % f

        if arg:
            mplayer_options += ' %s' % arg

        if self.deinterlace:
            mplayer_options += ' -vop pp=fd'


        if self.menuw.visible:
            self.menuw.hide()

        if not self.video_player:            
            self.video_player = plugin.getbyname(plugin.VIDEO_PLAYER)
            
        if self.video_player:
            error = self.video_player.play(file, mplayer_options, self)
        else:
            error = "No video player avaiable!"

        if error:
            AlertBox(text=error).show()
            rc.post_event(PLAY_END)


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        self.video_player.stop()


    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        if not self.menuw:
            self.menuw = menuw

        # only one track, play it
        if self.num_titles == 1:
            file = copy.copy(self)
            file.filename = '1'
            file.play(menuw = self.menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            file = copy.copy(self)

            # copy the attributes from mmpython about this track
            if self.info.has_key('tracks'):
                file.info = self.info.tracks[title-1]
            file.info_type = 'track'
            file.filename = '%s' % title
            file.name = _('Play Title %s') % title
            items += [file]

        moviemenu = menu.Menu(self.name, items, umount_all = 1, xml_file=self.xml_file)
        moviemenu.item_types = 'video'
        self.menuw.pushmenu(moviemenu)
        return


    def settings(self, arg=None, menuw=None):
        if not self.menuw:
            self.menuw = menuw
        confmenu = configure.get_menu(self, self.menuw, self.xml_file)
        self.menuw.pushmenu(confmenu)
        

    def eventhandler(self, event, menuw=None):
        """
        eventhandler for this item
        """
        # when called from mplayer.py, there is no menuw
        if not menuw:
            menuw = self.menuw

        if self.plugin_eventhandler(event, menuw):
            return True

        # PLAY_END: do have have to play another file?
        if self.subitems:
            if event == PLAY_END:
                try:
                    pos = self.subitems.index(self.current_subitem)
                    if pos < len(self.subitems)-1:
                        self.current_subitem = self.subitems[pos+1]
                        print "playing next item"
                        self.current_subitem.play(menuw=menuw)
                        return True
                except:
                    pass
            elif event == USER_END:
                pass

        # show configure menu
        if event == MENU:
            self.video_player.stop()
            self.settings(menuw=menuw)
            menuw.show()
            return True
        
        # give the event to the next eventhandler in the list
        if isinstance( self.parent, str ):
            self.parent = None
        return Item.eventhandler(self, event, menuw)
