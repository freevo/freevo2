#if 0 /*
# -----------------------------------------------------------------------
# directory.py - Directory handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.64  2003/11/23 19:21:55  dischi
# some cleanup
#
# Revision 1.63  2003/11/23 17:04:53  dischi
# directory.py now handles fxd files itself based on the new fxd parser
#
# Revision 1.62  2003/11/22 20:34:44  dischi
# use new vfs
#
# Revision 1.61  2003/11/22 02:31:15  gsbarbieri
# Please don't use:
#     _( "string A" + \
#        "string B" )
#
#  that sucks translation, cause it's split in 2 separate strings.
# Instead, use this:
#
#     _( "string A" \
#        "string B" )
#
# Revision 1.60  2003/11/21 11:48:03  dischi
# Reworked the directory settings: MOVIE_PLAYLISTS and AUDIO_RANDOM_PLAYLIST
# are removed, the new variables to control a directory style are
# DIRECTORY_CREATE_PLAYLIST, DIRECTORY_ADD_PLAYLIST_FILES,
# DIRECTORY_ADD_RANDOM_PLAYLIST and DIRECTORY_AUTOPLAY_ITEMS. The directory
# updated now uses stat, set DIRECTORY_USE_STAT_FOR_CHANGES = 0 if you have
# problems with it.
#
# The dirwatcher is now a plugin and no thread
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
import traceback
import re
import codecs
import stat
import copy
import rc
import mmpython

import config
import util
import menu as menu_module
import skin
import plugin
import video
import audio
import image
import games

from item import Item
from playlist import Playlist, RandomPlaylist
from video.xml_parser import parseMovieFile
from event import *

import gui.PasswordInputBox as PasswordInputBox
import gui.AlertBox as AlertBox
from gui.ProgressBox import ProgressBox

# XML support
from xml.utils import qp_xml
            
# Add support for bins album files
from mmpython.image import bins

skin = skin.get_singleton()

all_variables = [('DIRECTORY_SORT_BY_DATE', _('Directory Sort By Date'),
                  _('Sort directory by date and not by name.')),
                 
                 ('DIRECTORY_AUTOPLAY_SINGLE_ITEM', _('Directory Autoplay Single Item'),
                  _('Don\'t show directory if only one item exists and auto-select ' \
                    'the item.')),

                 ('FORCE_SKIN_LAYOUT', _('Force Skin Layout'),
                  _('Force skin to a specific layout. This option doesn\'t work with ' \
                    'all skins and the result may differ based on the skin.')),

                 ('DIRECTORY_SMART_SORT', _('Directory Smart Sort'),
                  _('Use a smarter way to sort the items.')),

                 ('USE_MEDIAID_TAG_NAMES', _('Use MediaID Tag Names'),
                  _('Use the names from the media files tags as display name.')),

                 ('DIRECTORY_REVERSE_SORT', _('Directory Reverse Sort'),
                  _('Show the items in the list in reverse order.')),

                 ('AUDIO_FORMAT_STRING', '', ''),

                 ('DIRECTORY_CREATE_PLAYLIST', _('Directory Create Playlist'),
                  _('Handle the directory as playlist. After one file is played, the next '\
                    'one will be started.')) ,

                 ('DIRECTORY_ADD_PLAYLIST_FILES', _('Directory Add Playlist Files'),
                  _('Add playlist files to the list of items')) ,

                 ('DIRECTORY_ADD_RANDOM_PLAYLIST', _('Directory Add Random Playlist'),
                  _('Add an item for a random playlist')) ,

                 ('DIRECTORY_AUTOPLAY_ITEMS', _('Directory Autoplay Items'),
                  _('Autoplay the whole directory (as playlist) when it contains only '\
                    'files and no directories' ))]

# varibales that contain a type list
type_list_variables = [ 'DIRECTORY_CREATE_PLAYLIST', 'DIRECTORY_ADD_PLAYLIST_FILES',
                        'DIRECTORY_ADD_RANDOM_PLAYLIST', 'DIRECTORY_AUTOPLAY_ITEMS' ]

possible_display_types = [ ]


class DirItem(Playlist):
    """
    class for handling directories
    """
    def __init__(self, directory, parent, name = '', display_type = None, add_args = None):
        Item.__init__(self, parent)
        self.type = 'dir'
        self.menuw = None
        self.menu  = None
        
        # variables only for Playlist
        self.current_item = 0
        self.playlist = []
        self.autoplay = False

        # variables only for DirItem
        self.dir          = os.path.abspath(directory)
        self.display_type = display_type
        self.info         = {}
        self.mountpoint   = None

        if add_args == None and hasattr(parent, 'add_args'): 
            add_args = parent.add_args

        self.add_args = add_args

        # set directory variables to default
        global all_variables
        for v,n,d in all_variables:
            setattr(self, v, eval('config.%s' % v))
        self.modified_vars = []

        if name:
            self.name = name
	elif vfs.isfile(directory + '/album.xml'):
            try:
                self.name = bins.get_bins_desc(directory)['desc']['title']
            except:
                self.name = vfs.basename(directory)
        else:
            self.name = vfs.basename(directory)

        
        # check for image in album.xml
        if vfs.isfile(directory + '/album.xml'):
            try:
                image = bins.get_bins_desc(directory)['desc']['sampleimage']
                image = vfs.join(directory, image)
                if vfs.isfile(image):
                    self.image = image
                    self.handle_type = self.display_type
            except:
                pass

        # Check for a cover in current dir
        image = util.getimage(directory+'/cover')
        if image:
            self.image = image
            self.handle_type = self.display_type
            
        if not self.image and self.display_type == 'audio':
            images = ()
            covers = ()
            files =()
            def image_filter(x):
                return re.match('.*(jpg|png)$', x, re.IGNORECASE)
            def cover_filter(x):
                return re.search(config.AUDIO_COVER_REGEXP, x, re.IGNORECASE)

            # Pick an image if it is the only image in this dir, or it matches
            # the configurable regexp
            try:
                files = vfs.listdir(directory)
            except OSError:
                print "oops, os.listdir() error"
                traceback.print_exc()
            images = filter(image_filter, files)
            image = None
            if len(images) == 1:
                image = vfs.join(directory, images[0])
            elif len(images) > 1:
                covers = filter(cover_filter, images)
                if covers:
                    image = vfs.join(directory, covers[0])
            self.image = image

        if not self.image and config.TV_SHOW_DATA_DIR:
            self.image = util.getimage(vfs.join(config.TV_SHOW_DATA_DIR,
                                                    vfs.basename(directory).lower()))

            if config.TV_SHOW_INFORMATIONS.has_key(vfs.basename(directory).lower()):
                tvinfo = config.TV_SHOW_INFORMATIONS[vfs.basename(directory).lower()]
                self.info = tvinfo[1]
                if not self.image:
                    self.image = tvinfo[0]
                if not self.xml_file:
                    self.xml_file = tvinfo[3]

        if vfs.isfile(directory+'/folder.fxd'): 
            self.xml_file = directory+'/folder.fxd'

        if self.xml_file:
            self.set_xml_file(self.xml_file)
            
        if self.DIRECTORY_SORT_BY_DATE == 2 and self.display_type != 'tv':
            self.DIRECTORY_SORT_BY_DATE = 0


    def set_xml_file(self, file):
        """
        Set self.xml_file and parse it
        """
        self.xml_file = file
        if self.xml_file and vfs.isfile(self.xml_file):
            try:
                parser = util.fxdparser.FXD(self.xml_file)
                parser.set_handler('folder', self.read_folder_fxd)
                parser.parse()
            except:
                print "fxd file %s corrupt" % self.xml_file
                traceback.print_exc()



    def read_folder_fxd(self, fxd, node):
        '''
        parse the xml file for directory settings
        
	<?xml version="1.0" ?>
	<freevo>
	  <folder title="Incoming TV Shows" cover-img="foo.jpg">
	    <setvar name="directory_autoplay_single_item" val="0"/>
	    <info>
	      <content>Episodes for current tv shows not seen yet</content>
	    </info>
	  </folder>
	</freevo>
        '''

        global all_variables
        set_all = self.xml_file == self.dir+'/folder.fxd'

        # read attributes
        if set_all:
            if node.attrs.has_key(('', 'title')):
                self.name = node.attrs[('', 'title')].encode(config.LOCALE)

            if node.attrs.has_key(('', 'cover-img')):
                image = node.attrs[('', 'cover-img')].encode(config.LOCALE)
                if image and vfs.isfile(vfs.join(self.dir, image)):
                    self.image = vfs.join(self.dir, image)

            if node.attrs.has_key(('', 'import')):
                import_xml = node.attrs[('', 'import')].encode(config.LOCALE)
                if vfs.isfile(vfs.join(self.dir, import_xml + '.fxd')):
                    info = parseMovieFile(vfs.join(self.dir, import_xml + '.fxd'), self, [])
                    if info:
                        self.name      = info[0].name
                        self.image     = info[0].image
                        self.info_type = info[0].type
                        for key in info[0].info:
                            self.info[key] = info[0].info[key]

            # parse <info> tag
            fxd.parse_info(fxd.get_children(node, 'info', 1), self,
                           {'description': 'content', 'content': 'content' })

        for child in fxd.get_children(node, 'setvar', 1):
            # <setvar name="directory_smart_sort" val="1"/>
            for v,n,d in all_variables:
                if child.attrs[('', 'name')].upper() == v.upper():
                    if v.upper() in type_list_variables:
                        if int(child.attrs[('', 'val')]):
                            setattr(self, v, [self.display_type])
                        else:
                            setattr(self, v, [])
                    else:
                        try:
                            setattr(self, v, int(child.attrs[('', 'val')]))
                        except ValueError:
                            setattr(self, v, child.attrs[('', 'val')])
                    self.modified_vars.append(v)

    
    def write_folder_fxd(self, fxd, node):
        """
        callback to save the modified fxd file
        """
        # remove old setvar
        for child in copy.copy(node.children):
            if child.name == 'setvar':
                node.children.remove(child)

        # add current vars as setvar
        for v in self.modified_vars:
            if v in type_list_variables:
                if getattr(self, v):
                    val = 1
                else:
                    val = 0
            else:
                val = getattr(self, v)
            fxd.add(fxd.XMLnode('setvar', (('name', v.lower()), ('val', val))), node, 0)


    def copy(self, obj):
        """
        Special copy value DirItem
        """
        Playlist.copy(self, obj)
        if obj.type == 'dir':
            self.dir          = obj.dir
            self.display_type = obj.display_type
            self.info         = obj.info
            

    def getattr(self, attr):
        """
        return the specific attribute as string or an empty string
        """
        if attr == 'type':
            if self.media:
                return _('Directory on disc [%s]') % self.media.label
            return _('Directory')

        if attr in ( 'freespace', 'totalspace' ):
            if self.media:
                return None
            
            space = eval('util.%s(self.dir)' % attr) / 1000000
            if space > 1000:
                space='%s,%s' % (space / 1000, space % 1000)
            return space
        
        return Item.getattr(self, attr)


    # eventhandler for this item
    def eventhandler(self, event, menuw=None):
        if event == DIRECTORY_CHANGE_DISPLAY_TYPE and menuw.menustack[-1] == self.menu:
            try:
                pos = possible_display_types.index(self.display_type)
                type = possible_display_types[(pos+1) % len(possible_display_types)]

                menuw.delete_menu(allow_reload = False)

                newdir = DirItem(self.dir, self.parent, self.name, type, self.add_args)
                newdir.DIRECTORY_AUTOPLAY_SINGLE_ITEM = False
                newdir.cwd(menuw=menuw)

                menuw.menustack[-2].selected = newdir
                pos = menuw.menustack[-2].choices.index(self)
                menuw.menustack[-2].choices[pos] = newdir
                rc.post_event(Event(OSD_MESSAGE, arg='%s view' % type))
                return True
            except (IndexError, ValueError):
                pass
        
        return Playlist.eventhandler(self, event, menuw)
        


    # ======================================================================
    # actions
    # ======================================================================

    def actions(self):
        """
        return a list of actions for this item
        """
        suffix = ''
        if self.display_type == 'audio':
            suffix = config.SUFFIX_AUDIO_FILES
        elif self.display_type == 'video':
            suffix = config.SUFFIX_VIDEO_FILES

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        items = [ ( self.cwd, _('Browse directory')),
                  ( self.play, _('Play all files in directory')) ]

        if display_type in self.DIRECTORY_AUTOPLAY_ITEMS:
            for d in util.getdirnames(self.dir):
                if not (d.endswith('CVS') or d.endswith('.xvpics') or \
                        d.endswith('.thumbnails') or d.endswith('.pics')):
                    break
            else:
                items.reverse()

        if suffix:
            items += [ ( RandomPlaylist((self.dir, suffix), self, recursive=False),
                         _('Random play all items')),
                       ( RandomPlaylist((self.dir, suffix), self),
                         _('Recursive random play all items')), 
                       ( RandomPlaylist((self.dir, suffix), self, random = False),
                         _('Recursive play all items')) ]
        
        items.append((self.configure, _('Configure directory'), 'configure'))
        return items
    


    def fxd_handler(self, fxd_files, duplicate_check, display_type):
        """
        return a list of items that belong to a fxd files
        """
        items = []
        for fxd_file in fxd_files:
            try:
                # create a basic fxd parser
                parser = util.fxdparser.FXD(fxd_file)

                # create an object that can parse the special infos
                # from the fxd
                handler = []
                for t in possible_display_types:
                    if not display_type or display_type == t and \
                           hasattr(eval(t), 'FXDHandler'):
                        h = eval(t).FXDHandler(parser, fxd_file, self, duplicate_check)
                        handler.append(h)

                # start the parsing
                parser.parse()

                # get this informations back
                for h in handler:
                    items += h.items

            except:
                print "fxd file %s corrupt" % fxd_file
                traceback.print_exc()
        return items
    
        
    def cwd(self, arg=None, menuw=None):
        """
        browse directory
        """
        self.check_password_and_build(arg=None, menuw=menuw)



    def play(self, arg=None, menuw=None):
        """
        play directory
        """
        if arg == 'next':
            Playlist.play(self, arg=arg, menuw=menuw)
        else:
            self.check_password_and_build(arg='play', menuw=menuw)


    def check_password_and_build(self, arg=None, menuw=None):
        """
        password checker
        """
        if not self.menuw:
            self.menuw = menuw

        # are we on a ROM_DRIVE and have to mount it first?
        for media in config.REMOVABLE_MEDIA:
            if self.dir.find(media.mountdir) == 0:
                util.mount(self.dir)
                self.media = media

        if self.mountpoint:
            util.mount(self.mountpoint)
            
	if vfs.isfile(self.dir + '/.password'):
	    print 'password protected dir'
            self.arg   = arg
            self.menuw = menuw
	    pb = PasswordInputBox(text=_('Enter Password'), handler=self.pass_cmp_cp)
	    pb.show()
	else:
	    self.build(arg=arg, menuw=menuw)


    def pass_cmp_cb(self, word=None):
        """
        read the contents of self.dir/.passwd and compare to word
        callback for check_password_and_build
        """
	try:
	    pwfile = vfs.open(self.dir + '/.password')
	    line = pwfile.readline()
	except IOError, e:
	    print 'error %d (%s) reading password file for %s' % \
		  (e.errno, e.strerror, self.dir)
	    return

	pwfile.close()
	password = line.strip()
	if word == password:
	    self.build(self.arg, self.menuw)
	else:
	    pb = AlertBox(text=_('Password incorrect'))
	    pb.show()
            return


    def build(self, arg=None, menuw=None):
        """
        build the items for the directory
        """
        self.playlist = []

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        files = vfs.listdir(self.dir)
        self.all_files = copy.copy(files)

        # build play_items for video, audio, image, games
        # the interface functions must remove the files they cover, they
        # can also remove directories


        # 
        # PHASE I: scan directory with mmpython
        #

        mmpython_dir = self.dir
        if self.media:
            dir_on_disc = self.dir[len(self.media.mountdir)+1:]
            if self.media.cached and dir_on_disc == '':
                mmpython_dir = None
                num_changes = 0
            else:
                mmpython_dir = 'cd://%s:%s:%s' % (self.media.devicename,
                                                  self.media.mountdir, dir_on_disc)

        if mmpython_dir:
            num_changes = mmpython.check_cache(mmpython_dir)
            
        pop = None
        callback=None
        if (num_changes > 10) or (num_changes and self.media):
            if self.media and dir_on_disc == '':
                pop = ProgressBox(text=_('Scanning disc, be patient...'), full=num_changes)
            else:
                pop = ProgressBox(text=_('Scanning directory, be patient...'),
                                  full=num_changes)
            pop.show()
            callback=pop.tick

        if num_changes > 0:
            try:
                mmpython.cache_dir(mmpython_dir, callback=callback)
            except TypeError:
                print
                print 'ERROR:'
                print 'Your mmpython version is too old, please update'
                print
                mmpython.cache_dir(mmpython_dir)

            if self.media:
                self.media.cached = True

        play_items = []


        # 
        # PHASE II: parse fxd files
        #

        fxd_files = util.find_matches(files, ['fxd'])
        for d in copy.copy(files):
            if vfs.isdir(d) and vfs.isfile(vfs.join(d, vfs.basename(d) + '.fxd')):
                fxd_files.append(vfs.join(d, vfs.basename(d) + '.fxd'))
                files.remove(d)

        play_items += self.fxd_handler(fxd_files, files, display_type)


        # 
        # PHASE III: add normal files
        #

        for t in possible_display_types:
            if not display_type or display_type == t:
                play_items += eval(t).cwd(self, files)


        # 
        # PHASE IV: sort play items
        #

        if self.DIRECTORY_SORT_BY_DATE:
            play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                             o.sort('date').upper()))
        else:
            play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                             o.sort().upper()))

        if self.DIRECTORY_REVERSE_SORT:
            play_items.reverse()
            
        files.sort(lambda l, o: cmp(l.upper(), o.upper()))

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if not display_type or display_type in self.DIRECTORY_CREATE_PLAYLIST:
            self.playlist = play_items


        # 
        # PHASE V: add subdirs
        #

        dir_items = []
        for filename in files:
            if vfs.isdir(filename):
                dir_items += [ DirItem(filename, self, display_type =
                                       self.display_type) ]

        if self.DIRECTORY_SMART_SORT:
            dir_items.sort(lambda l, o: util.smartsort(l.dir,o.dir))
        else:
            dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))
 
        if self.DIRECTORY_REVERSE_SORT:
            dir_items.reverse()
            

        # 
        # PHASE VI: add playlists
        #

        pl_items = []
        if not self.display_type or display_type in self.DIRECTORY_ADD_PLAYLIST_FILES:
            for pl in util.find_matches(files, config.SUFFIX_AUDIO_PLAYLISTS):
                pl_items += [ Playlist(pl, self) ]

        if not self.display_type or self.display_type == 'image':
            for file in util.find_matches(files, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = True
                pl_items += [ pl ]

        pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))


        # 
        # PHASE VII: finalize
        #

        # all items together
        items = []

        # random playlist
        if display_type and display_type in self.DIRECTORY_ADD_RANDOM_PLAYLIST \
               and len(play_items) > 1:
            pl = Playlist(play_items, self)
            pl.randomize()
            pl.autoplay = True
            items += [ pl ]

        items += dir_items + pl_items + play_items

        self.dir_items  = dir_items
        self.pl_items   = pl_items
        self.play_items = play_items


        title = self.name

        if pop:
            pop.destroy()
            # closing the poup will rebuild the menu which may umount
            # the drive
            if self.media:
                self.media.mount()

        # 
        # PHASE VIII: action!
        #

        # autoplay
        if len(items) == 1 and items[0].actions() and \
           self.DIRECTORY_AUTOPLAY_SINGLE_ITEM:
            items[0].actions()[0][0](menuw=menuw)

        elif arg=='play' and self.play_items:
            self.playlist = self.play_items
            Playlist.play(self, menuw=menuw)
            
        else:
            item_menu = menu_module.Menu(title, items, reload_func=self.reload,
                                         item_types = self.display_type,
                                         force_skin_layout = self.FORCE_SKIN_LAYOUT)

            if self.xml_file:
                item_menu.skin_settings = skin.LoadSettings(self.xml_file)

            if menuw:
                menuw.pushmenu(item_menu)

            plugin.getbyname('Dirwatcher').cwd(menuw, self, item_menu, self.dir,
                                               self.all_files)
            self.menu  = item_menu
            self.menuw = menuw
        return items


    def reload(self):
        """
        called when we return to this menu
        """
        plugin.getbyname('Dirwatcher').cwd(self.menuw, self, self.menu, self.dir,
                                           self.all_files)
        plugin.getbyname('Dirwatcher').scan(force=True)

        # we changed the menu, don't build a new one
        return None


    def update(self, new_files, del_files, all_files):
        """
        update the current item set. Maybe this function can share some code
        with cwd in the future, but it's easier now the way it is
        """
        new_items = []
        del_items = []

        self.all_files = all_files

        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'


        # a fxd files may be removed, 'free' covered files
        for fxd_file in util.find_matches(del_files, ['fxd']):
            for i in self.play_items:
                if i.xml_file == fxd_file and hasattr(i, '_fxd_covered_'):
                    for covered in i._fxd_covered_:
                        if not covered in del_files:
                            new_files.append(covered)
                    del_items.append(i)
                    del_files.remove(fxd_file)

            
        # a new fxd file may cover items
        fxd_files = util.find_matches(new_files, ['fxd'])
        if fxd_files:
            for f in fxd_files:
                new_files.remove(f)
            copy_all = copy.copy(all_files)
            new_items += self.fxd_handler(fxd_files, copy_all, display_type)
            for f in all_files:
                if not f in copy_all:
                    # covered by fxd now
                    if not f in new_files:
                        del_files.append(f)
                    else:
                        new_files.remove(f)

                    
        # check modules if they know something about the deleted/new files
        for t in possible_display_types:
            if not display_type or display_type == t:
                eval(t).update(self, new_files, del_files, new_items, del_items,
                               self.play_items)
                
        # store the current selected item
        selected = self.menu.selected
        
        # delete play items from the menu
        for i in del_items:
            self.menu.delete_item(i)
            self.play_items.remove(i)

        # delete dir items from the menu
        for dir in del_files:
            for item in self.dir_items:
                if item.dir == dir:
                    self.menu.delete_item(item)
                    self.dir_items.remove(item)

        # delete playlist items from the menu
        for pl in del_files:
            for item in self.pl_items:
                if item.filename == pl:
                    self.menu.delete_item(item)
                    self.pl_items.remove(item)


        # add new play items to the menu
        if new_items:
            self.play_items += new_items
            if self.DIRECTORY_SORT_BY_DATE:
                self.play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                      o.sort('date').upper()))
            else:
                self.play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                      o.sort().upper()))

        # add new dir items to the menu
        new_dir_items = []
        for dir in new_files:
            if vfs.isdir(dir):
                new_dir_items += [ DirItem(dir, self, display_type = self.display_type) ]

        if new_dir_items:
            self.dir_items += new_dir_items
            self.dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))

        if self.DIRECTORY_REVERSE_SORT:
            self.play_items.reverse()
            self.dir_items.reverse()

        # add new playlist items to the menu
        new_pl_items = []
        if not display_type or display_type in self.DIRECTORY_ADD_PLAYLIST_FILES:
            for pl in util.find_matches(new_files, config.SUFFIX_AUDIO_PLAYLISTS):
                new_pl_items += [ Playlist(pl, self) ]

        if not display_type or display_type == 'image':
            for file in util.find_matches(new_files, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = True
                new_pl_items += [ pl ]

        if new_pl_items:
            self.pl_items += new_pl_items
            self.pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))


        
        items = []

        # random playlist (only active for audio)
        if display_type and display_type in self.DIRECTORY_ADD_RANDOM_PLAYLIST \
               and len(play_items) > 1:

            # some files changed, rebuild playlist
            if new_items or del_items:
                pl = Playlist(self.play_items, self)
                pl.randomize()
                pl.autoplay = True
                items += [ pl ]

            # reuse old playlist
            else:
                items += [ self.menu.choices[0] ]

        # build a list of all items
        items += self.dir_items + self.pl_items + self.play_items

        # finally add the items
        for i in new_items + new_dir_items + new_pl_items:
            self.menu.add_item(i, items.index(i))

        if not selected in self.menu.choices:
            if hasattr(selected, 'id'):
                id = selected.id
                for i in self.menu.choices:
                    if hasattr(i, 'id') and i.id == selected.id:
                        self.menu.selected = i
                        break
                    
        # reload the menu, use an event to avoid problems because this function
        # was called by a thread (not anymore, but why change it)
        if hasattr(self.menu,'skin_force_text_view'):
            del self.menu.skin_force_text_view
        rc.post_event('MENU_REBUILD')


    # ======================================================================
    # configure submenu
    # ======================================================================


    def configure_set_name(self, name):
        """
        return name for the configure menu
        """
        if name in self.modified_vars:
            if name == 'FORCE_SKIN_LAYOUT':
                return 'ICON_RIGHT_%s_%s' % (str(getattr(self, arg)),
                                             str(getattr(self, arg)))
            elif getattr(self, name):
                return 'ICON_RIGHT_ON_' + _('on')
            else:
                return 'ICON_RIGHT_OFF_' + _('off')
        else:
            if name == 'FORCE_SKIN_LAYOUT':
                return 'ICON_RIGHT_OFF_' + _('off')
            else:
                return 'ICON_RIGHT_AUTO_' + _('auto')

        
    def configure_set_var(self, arg=None, menuw=None):
        """
        Update the variable in arg and change the menu. This function is used by
        'configure'
        """

        # get current value, None == no special settings
        if arg in self.modified_vars:
            if arg in type_list_variables:
                if getattr(self, arg):
                    current = 1
                else:
                    current = 0
            else:
                current = getattr(self, arg)
        else:
            current = None

        # get the max value for toggle
        max = 1

        # for FORCE_SKIN_LAYOUT max = number of styles in the menu
        if arg == 'FORCE_SKIN_LAYOUT':
            if self.display_type and skin.settings.menu.has_key(self.display_type):
                area = skin.settings.menu[self.display_type]
            else:
                area = skin.settings.menu['default']
            max = len(area.style) - 1

        # switch from no settings to 0
        if current == None:
            self.modified_vars.append(arg)
            if arg in type_list_variables:
                setattr(self, arg, [])
            else:
                setattr(self, arg, 0)

        # inc variable
        elif current < max:
            if arg in type_list_variables:
                setattr(self, arg, [self.display_type])
            else:
                setattr(self, arg, current+1)

        # back to no special settings
        elif current == max:
            setattr(self, arg, getattr(config, arg))
            self.modified_vars.remove(arg)

        # create new item with updated name
        item = copy.copy(menuw.menustack[-1].selected)
        item.name = item.name[:item.name.find('\t') + 1] + self.configure_set_name(arg)

        # write folder.fxd
        self.xml_file = vfs.join(self.dir, 'folder.fxd')

        try:
            parser = util.fxdparser.FXD(self.xml_file)
            parser.set_handler('folder', self.write_folder_fxd, 'w', True)
            parser.save()
        except:
            print "fxd file %s corrupt" % self.xml_file
            traceback.print_exc()

        # rebuild menu
        menuw.menustack[-1].choices[menuw.menustack[-1].choices.\
                                    index(menuw.menustack[-1].selected)] = item
        menuw.menustack[-1].selected = item
        menuw.refresh(reload=1)
            
    
    def configure(self, arg=None, menuw=None):
        """
        show the configure dialog for folder specific settings in folder.fxd
        """
        items = []
        for i, name, descr in all_variables:
            if name == '':
                continue
            name += '\t'  + self.configure_set_name(i)
            mi = menu_module.MenuItem(name, self.configure_set_var, i)
            mi.description = descr
            items.append(mi)
        m = menu_module.Menu(_('Configure'), items)
        m.table = (80, 20)
        m.back_one_menu = 2
        menuw.pushmenu(m)

        


# ======================================================================

class Dirwatcher(plugin.DaemonPlugin):
                
    def __init__(self):
        plugin.DaemonPlugin.__init__(self)
        self.item          = None
        self.menuw         = None
        self.item_menu     = None
        self.dir           = None
        self.files         = None
        self.poll_interval = 100

        plugin.register(self, 'Dirwatcher')


    def cwd(self, menuw, item, item_menu, dir, files):
        self.menuw     = menuw
        self.item      = item
        self.item_menu = item_menu
        self.dir       = dir
        self.files     = files
        self.last_time = vfs.stat(self.dir)[stat.ST_MTIME]
        
    def scan(self, force=False):
        if not self.dir:
            return
        if not force and config.DIRECTORY_USE_STAT_FOR_CHANGES and \
               vfs.stat(self.dir)[stat.ST_MTIME] == self.last_time:
            return True

        try:
            files = vfs.listdir(self.dir, False)
        except OSError:
            # the directory is gone
            _debug_('Dirwatcher: unable to read directory %s' % self.dir,1)

            # send EXIT to go one menu up:
            rc.post_event(MENU_BACK_ONE_MENU)
            return
        
        new_files = []
        del_files = []
        
        for f in files:
            if not f in self.files:
                new_files += [ f ]
        for f in self.files:
            if not f in files:
                del_files += [ f ]

        if new_files or del_files:
            _debug_('directory has changed')
            self.item.update(new_files, del_files, files)
            self.last_time = vfs.stat(self.dir)[stat.ST_MTIME]
                    
        self.files = files

    
    def poll(self):
        if self.dir and self.menuw and \
               self.menuw.menustack[-1] == self.item_menu and not rc.app():
            self.scan()

# and activate that DaemonPlugin
dirwatcher_thread = Dirwatcher()
plugin.activate(dirwatcher_thread)
