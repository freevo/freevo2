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
# Revision 1.111  2004/01/04 17:20:20  dischi
# check for .raw file as image
#
# Revision 1.110  2004/01/04 13:06:52  dischi
# make it possible to call thumbnail creation with MENU_CALL_ITEM_ACTION
#
# Revision 1.109  2004/01/04 11:17:10  dischi
# add create thumbnail
#
# Revision 1.108  2004/01/01 19:36:46  dischi
# do not inherit players to child
#
# Revision 1.107  2004/01/01 16:41:30  mikeruelle
# fix dvd crash
#
# Revision 1.106  2004/01/01 16:15:45  dischi
# make sure we have a player even for classes inheriting from videoitem
#
# Revision 1.105  2003/12/31 16:42:40  dischi
# changes, related to item.py changes
#
# Revision 1.104  2003/12/30 15:36:01  dischi
# remove unneeded copy function, small bugfix
#
# Revision 1.103  2003/12/29 22:08:54  dischi
# move to new Item attributes
#
# Revision 1.102  2003/12/22 13:27:34  dischi
# patch for better support of fxd files with more discs from Matthieu Weber
#
# Revision 1.101  2003/12/09 19:43:01  dischi
# patch from Matthieu Weber
#
# Revision 1.100  2003/12/06 16:25:45  dischi
# support for type=url and <playlist> and <player>
#
# Revision 1.99  2003/11/28 20:08:58  dischi
# renamed some config variables
#
# Revision 1.98  2003/11/25 19:01:37  dischi
# remove the callback stuff from fxd, it was to complicated
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

import config
import util
import rc
import menu
import configure
import plugin

from gui   import PopupBox, AlertBox, ConfirmBox
from item  import Item
from event import *

class VideoItem(Item):
    def __init__(self, url, parent, info=None, parse=True):
        Item.__init__(self, parent)

        self.type = 'video'
        self.set_url(url, info=parse)

        if info:
            for key in info:
                self.info[key] = info[key]

        self.handle_type       = 'video'

        self.variants          = []         # if this item has variants
        self.subitems          = []         # more than one file/track to play
        self.current_subitem   = None

        self.subtitle_file     = {}         # text subtitles
        self.audio_file        = {}         # audio dubbing

        self.mplayer_options   = ''
        self.tv_show           = False

        self.video_width       = 0
        self.video_height      = 0

        self.selected_subtitle = None
        self.selected_audio    = None
        self.num_titles        = 0
        self.deinterlace       = 0
        self.elapsed           = 0
        
        self.possible_player   = []

        # find image for tv show and build new title
        if config.VIDEO_SHOW_REGEXP_MATCH(self.name) and not self.network_play and \
               config.VIDEO_SHOW_DATA_DIR:

            show_name = config.VIDEO_SHOW_REGEXP_SPLIT(self.name)
            if show_name[0] and show_name[1] and show_name[2] and show_name[3]:
                self.name = show_name[0] + " " + show_name[1] + "x" + show_name[2] +\
                            " - " + show_name[3]
                self.image = util.getimage((config.VIDEO_SHOW_DATA_DIR + \
                                            show_name[0].lower()), self.image)

                from video import tv_show_informations
                if tv_show_informations.has_key(show_name[0].lower()):
                    tvinfo = tv_show_informations[show_name[0].lower()]
                    for i in tvinfo[1]:
                        self.info[i] = tvinfo[1][i]
                    if not self.image:
                        self.image = tvinfo[0]
                    if not self.fxd_file:
                        self.fxd_file = tvinfo[3]
                    self.mplayer_options = tvinfo[2]

                self.tv_show   = True
                self.show_name = show_name

        # extra infos in discset_informations
        if parent and parent.media:
            fid = parent.media.id + \
                  self.filename[len(os.path.join(parent.media.mountdir,"")):]
            from video import discset_informations
            if discset_informations.has_key(fid):
                self.mplayer_options = discset_informations[fid]


        
    def set_url(self, url, info=True):
        """
        Sets a new url to the item. Always use this function and not set 'url'
        directly because this functions also changes other attributes, like
        filename, mode and network_play
        """
        Item.set_url(self, url, info)
        if url.startswith('dvd://') or url.startswith('vcd://'):
            self.network_play = False
            self.mimetype = self.url[:self.url.find('://')].lower()
        if not self.image or (self.parent and self.image == self.parent.image):
           image = vfs.getoverlay(self.filename + '.raw')
           if os.path.exists(image):
               self.image = image
               self.files.image = image
        
        
    def id(self):
        """
        Return a unique id of the item. This id should be the same when the
        item is rebuild later with the same informations
        """
        ret = self.url
        if self.subitems:
            for s in self.subitems:
                ret += s.id()
        if self.variants:
            for v in self.variants:
                ret += v.id()
        return ret


    def __getitem__(self, key):
        """
        return the specific attribute as string or an empty string
        """
        if key == 'item_id':
            if self.media:
                filename = self.filename[len(self.media.mountdir):]
                id = 'cd://%s-%s' % (self.media.id, filename)
            else:
                id = 'file://%s' % self.filename
            if self.subitems:
                for s in self.subitems:
                    id += s.getattr(key)
            if self.variants:
                for v in self.variants:
                    id += v.getattr(key)
                    
            return util.hexify(md5.new(id).digest())
        
        if key in ('length', 'geometry', 'aspect'):
            try:
                video = self.info.video[0]
                if key == 'length':
                    length = video.length
                    if length / 3600:
                        return '%d:%02d:%02d' % ( length / 3600, (length % 3600) / 60,
                                                  length % 60)
                    else:
                        return '%d:%02d' % (length / 60, length % 60)
                if key == 'geometry':
                    return '%sx%s' % (video.width, video.height)
                if key == 'aspect':
                    aspect = getattr(video, key)
                    return aspect[:aspect.find(' ')].replace('/', ':')
            except:
                pass
            
        return Item.__getitem__(self, key)

    
    def sort(self, mode=None):
        """
        Returns the string how to sort this item
        """
        if mode == 'date' and self.mode == 'file' and os.path.isfile(self.filename):
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

        self.possible_player = []
        for p in plugin.getbyname(plugin.VIDEO_PLAYER, True):
            rating = p.rate(self) * 10
            if config.VIDEO_PREFERED_PLAYER == p.name:
                rating += 1
            if hasattr(self, 'force_player') and p.name == self.force_player:
                rating += 100
            self.possible_player.append((rating, p))

        self.possible_player.sort(lambda l, o: -cmp(l[0], o[0]))

        self.player        = None
        self.player_rating = 0

        if not self.possible_player:
            return []

        self.player_rating, self.player = self.possible_player[0]

        if self.url == 'dvd://':
            if self.player_rating >= 20:
                items = [ (self.play, _('Play DVD')),
                          ( self.dvd_vcd_title_menu, _('DVD title list') ) ]
            else:
                items = [ ( self.dvd_vcd_title_menu, _('DVD title list') ),
                          (self.play, _('Play default track')) ]
                    
        elif self.url == 'vcd://':
            if self.player_rating >= 20:
                items = [ (self.play, _('Play VCD')),
                          ( self.dvd_vcd_title_menu, _('VCD title list') ) ]
            else:
                items = [ ( self.dvd_vcd_title_menu, _('VCD title list') ),
                          (self.play, _('Play default track')) ]
        else:
            items = [ (self.play, _('Play')) ]

        if self.network_play:
            items.append((self.play_max_cache, _('Play with maximum cache')))

        items += configure.get_items(self)
            
        if self.variants and len(self.variants) > 1:
            items = [ (self.show_variants, _('Show variants')) ] + items

        if not self.image and self.filename and not self.variants and not self.subitems:
            items.append((self.create_thumbnail, _('Create Thumbnail'), 'create_thumbnail'))
            
        return items


    def show_variants(self, arg=None, menuw=None):
        """
        show a list of variants in a menu
        """
        if not self.menuw:
            self.menuw = menuw
        m = menu.Menu(self.name, self.variants, reload_func=None, fxd_file=self.fxd_file)
        m.item_types = 'video'
        self.menuw.pushmenu(m)


    def create_thumbnail(self, arg=None, menuw=None):
        """
        create a thumbnail as image icon
        """
        import util.videothumb
        pop = PopupBox(text=_('Please wait....'))
        pop.show()

        util.videothumb.snapshot(self.filename)
        pop.destroy()
        if menuw.menustack[-1].selected != self:
            menuw.back_one_menu()


    def play_max_cache(self, arg=None, menuw=None):
        """
        play and use maximum cache with mplayer
        """
        self.play(menuw=menuw, arg='-cache 65536')


    def set_next_available_subitem(self):
        """
        select the next available subitem. Loops on each subitem and checks if
        the needed media is really there.
        If the media is there, sets self.current_subitem to the given subitem
        and returns 1.
        If no media has been found, we set self.current_subitem to None.
          If the search for the next available subitem did start from the
            beginning of the list, then we consider that no media at all was
            available for any subitem: we return 0.
          If the search for the next available subitem did not start from the
            beginning of the list, then we consider that at least one media
            had been found in the past: we return 1.
        """
        cont = 1
        from_start = 0
        si = self.current_subitem
        while cont:
            if not si:
                # No subitem selected yet: take the first one
                si = self.subitems[0]
                from_start = 1
            else:
                pos = self.subitems.index(si)
                # Else take the next one
                if pos < len(self.subitems)-1:
                    # Let's get the next subitem
                    si = self.subitems[pos+1]
                else:
                    # No next subitem
                    si = None
                    cont = 0
            if si:
                if (si.media_id or si.media):
                    # If the file is on a removeable media
                    if util.check_media(si.media_id):
                        self.current_subitem = si
                        return 1
                else:
                    # if not, it is always available
                    self.current_subitem = si
                    return 1
        self.current_subitem = None
        return not from_start


    def play(self, arg=None, menuw=None):
        """
        play the item.
        """
        if not self.possible_player:
            for p in plugin.getbyname(plugin.VIDEO_PLAYER, True):
                rating = p.rate(self) * 10
                if config.VIDEO_PREFERED_PLAYER == p.name:
                    rating += 1
                if hasattr(self, 'force_player') and p.name == self.force_player:
                    rating += 100
                self.possible_player.append((rating, p))

            self.possible_player.sort(lambda l, o: -cmp(l[0], o[0]))

        if not self.possible_player:
            return

        self.player_rating, self.player = self.possible_player[0]
        self.parent.current_item = self

        if not self.menuw:
            self.menuw = menuw

        # if we have variants, play the first one as default
        if self.variants:
            self.variants[0].play(arg, menuw)
            return

        # if we have subitems (a movie with more than one file),
        # we start playing the first that is physically available
        if self.subitems:
            self.error_in_subitem = 0
            self.last_error_msg = ''
            result = self.set_next_available_subitem()
            if self.current_subitem: # 'result' is always 1 in this case
                # The media is available now for playing
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
                self.last_error_msg = self.current_subitem.play(arg, self.menuw)
                if self.last_error_msg:
                    self.error_in_subitem = 1
                    # Go to the next playable subitem, using the loop in
                    # eventhandler()
                    self.eventhandler(PLAY_END)
                    
            elif not result:
                # No media at all was found: error
                ConfirmBox(text=(_('No media found for "%s".\n')+
                                 _('Please insert the media.')) %
                                 self.name, handler=self.play ).show()
            return

        # normal plackback of one file
        if self.url.startswith('file://'):
            file = self.filename
            if self.media_id:
                mountdir, file = util.resolve_media_mountdir(self.media_id,file)
                if mountdir:
                    util.mount(mountdir)
                else:
                    self.menuw.show()
                    ConfirmBox(text=(_('Media not found for file "%s".\n')+
                                     _('Please insert the media.')) % file,
                               handler=self.play ).show()
                    return

            elif self.media:
                util.mount(os.path.dirname(self.filename))

        elif self.url.startswith('dvd://') or self.url.startswith('vcd://'):
            if not self.media:
                media = util.check_media(self.media_id)
                if media:
                    self.media = media
                else:
                    self.menuw.show()
                    ConfirmBox(text=(_('Media not not found for "%s".\n')+
                                     _('Please insert the media.')) % self.url,
                               handler=self.play).show()
                    return

        if self.player_rating < 10:
            AlertBox(text=_('No player for this item found')).show()
            return
        
        mplayer_options = self.mplayer_options.split(' ')
        if not mplayer_options:
            mplayer_options = []

        if arg:
            mplayer_options += arg.split(' ')

        if self.menuw.visible:
            self.menuw.hide()

        self.plugin_eventhandler(PLAY, menuw)
        
        error = self.player.play(mplayer_options, self)

        if error:
            # If we are a subitem we don't show any error message before
            # having tried all the subitems
            if self.parent.subitems:
                return error
            else:
                AlertBox(text=error).show()
                rc.post_event(PLAY_END)


    def stop(self, arg=None, menuw=None):
        """
        stop playing
        """
        if self.player:
            self.player.stop()


    def dvd_vcd_title_menu(self, arg=None, menuw=None):
        """
        Generate special menu for DVD/VCD/SVCD content
        """
        if not self.menuw:
            self.menuw = menuw

        # only one track, play it
        if self.num_titles == 1:
            i=copy.copy(self)
            i.possible_player = []
            i.set_url(self.url + '1', False)
            i.play(menuw = self.menuw)
            return

        # build a menu
        items = []
        for title in range(1,self.num_titles+1):
            i = copy.copy(self)
            i.possible_player = []
            # copy the attributes from mmpython about this track
            if self.info.has_key('tracks'):
                i.info = self.info.tracks[title-1]
            i.info_type = 'track'
            i.set_url(self.url + str(title), False)
            i.name = _('Play Title %s') % title
            items += [i]

        moviemenu = menu.Menu(self.name, items, umount_all = 1, fxd_file=self.fxd_file)
        moviemenu.item_types = 'video'
        self.menuw.pushmenu(moviemenu)


    def settings(self, arg=None, menuw=None):
        """
        create a menu with 'settings'
        """
        if not self.menuw:
            self.menuw = menuw
        confmenu = configure.get_menu(self, self.menuw, self.fxd_file)
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

        # PLAY_END: do we have to play another file?
        if self.subitems:
            if event == PLAY_END:
                self.set_next_available_subitem()
                # Loop untli we find a subitem which plays without error
                while self.current_subitem: 
                    _debug_('playing next item')
                    error = self.current_subitem.play(menuw=menuw)
                    if error:
                        self.last_error_msg = error
                        self.error_in_subitem = 1
                        self.set_next_available_subitem()
                    else:
                        return True
                if self.error_in_subitem:
                    # No more subitems to play, and an error occured
                    self.menuw.show()
                    AlertBox(text=self.last_error_msg).show()
                    
            elif event == USER_END:
                pass

        # show configure menu
        if event == MENU:
            if self.player:
                self.player.stop()
            self.settings(menuw=menuw)
            menuw.show()
            return True
        
        # give the event to the next eventhandler in the list
        if isinstance( self.parent, str ):
            self.parent = None
        return Item.eventhandler(self, event, menuw)
