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
# Revision 1.89  2004/01/07 18:18:59  dischi
# remove update info on build
#
# Revision 1.88  2004/01/06 19:27:03  dischi
# use new mtime function to avoid crash
#
# Revision 1.87  2004/01/05 15:21:04  outlyer
# I am seeing OSErrors not IOErrors for this, so we can just watch for both
#
# Revision 1.86  2004/01/04 17:18:50  dischi
# also check OVERLAY_DIR for update
#
# Revision 1.85  2004/01/04 13:06:20  dischi
# delete skin information on update
#
# Revision 1.84  2004/01/04 10:24:12  dischi
# inherit config variables from parent if possible
#
# Revision 1.83  2004/01/03 17:39:45  dischi
# Remove the update function fro the MimetypePlugin and inside DirItem.
# Now all items are rebuild as default, because the old style didn't
# support adding images to items during display and now it's also
# possible to change a fxd file and the directory will update.
#
# Revision 1.82  2004/01/01 19:48:42  dischi
# fix dir playing
#
# Revision 1.81  2004/01/01 17:42:23  dischi
# add FileInformation
#
# Revision 1.80  2003/12/31 16:40:24  dischi
# small speed enhancements
#
# Revision 1.79  2003/12/30 15:33:01  dischi
# remove unneeded copy function, make id a function
#
# Revision 1.78  2003/12/29 22:07:14  dischi
# renamed xml_file to fxd_file
#
# Revision 1.77  2003/12/17 16:43:59  outlyer
# Prevent a crash if the current directory is removed... just silently move
# up to the previous directory.
#
# (This is identical to the previous 1.4 behaviour)
#
# Revision 1.74  2003/12/08 20:37:33  dischi
# merged Playlist and RandomPlaylist into one class
#
# Revision 1.73  2003/12/07 14:45:57  dischi
# make the busy icon thread save
#
# Revision 1.72  2003/12/07 12:26:55  dischi
# add osd busy icon (work in progress)
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
import stat
import copy
import rc
import mmpython

import config
import util

import menu
import skin
import plugin
import osd

from item import Item, FileInformation
from playlist import Playlist
from event import *
from gui import PasswordInputBox, AlertBox, ProgressBox

skin = skin.get_singleton()

all_variables = [('DIRECTORY_SORT_BY_DATE', _('Directory Sort By Date'),
                  _('Sort directory by date and not by name.')),
                 
                 ('DIRECTORY_AUTOPLAY_SINGLE_ITEM', _('Directory Autoplay Single Item'),
                  _('Don\'t show directory if only one item exists and auto-select ' \
                    'the item.')),

                 ('DIRECTORY_FORCE_SKIN_LAYOUT', _('Force Skin Layout'),
                  _('Force skin to a specific layout. This option doesn\'t work with ' \
                    'all skins and the result may differ based on the skin.')),

                 ('DIRECTORY_SMART_SORT', _('Directory Smart Sort'),
                  _('Use a smarter way to sort the items.')),

                 ('DIRECTORY_USE_MEDIAID_TAG_NAMES', _('Use MediaID Tag Names'),
                  _('Use the names from the media files tags as display name.')),

                 ('DIRECTORY_REVERSE_SORT', _('Directory Reverse Sort'),
                  _('Show the items in the list in reverse order.')),

                 ('DIRECTORY_AUDIO_FORMAT_STRING', '', ''),

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


class DirItem(Playlist):
    """
    class for handling directories
    """
    def __init__(self, directory, parent, name = '', display_type = None, add_args = None):
        Playlist.__init__(self, parent=parent)
        self.type = 'dir'
        self.menuw = None
        self.menu  = None
        self.name  = os.path.basename(directory)

        # store FileInformation for moving/copying
        self.files = FileInformation()
        if self.media:
            self.files.read_only = True
        self.files.append(directory)
        
        if name:
            self.name = name
        
        # variables only for DirItem
        self.dir           = os.path.abspath(directory)
        self.display_type  = display_type
        self.info          = {}
        self.mountpoint    = None
        self.skin_settings = False
        
        if add_args == None and hasattr(parent, 'add_args'): 
            add_args = parent.add_args

        self.add_args = add_args

        # set directory variables to default
        global all_variables
        for v,n,d in all_variables:
            if hasattr(parent, v):
                setattr(self, v, eval('parent.%s' % v))
            else:
                setattr(self, v, eval('config.%s' % v))
        self.modified_vars = []

        # Check for a cover in current dir
        image = util.getimage(os.path.join(directory, 'cover'))
        if image:
            self.image       = image
            self.handle_type = self.display_type
            
        # Check mimetype plugins if they want to add something
        for p in plugin.mimetype(display_type):
            p.dirinfo(self)
            
        if vfs.isfile(directory+'/folder.fxd'): 
            self.fxd_file = directory+'/folder.fxd'

        if self.fxd_file:
            self.set_fxd_file(self.fxd_file)
            
        if self.DIRECTORY_SORT_BY_DATE == 2 and self.display_type != 'tv':
            self.DIRECTORY_SORT_BY_DATE = 0



    def set_fxd_file(self, file):
        """
        Set self.fxd_file and parse it
        """
        self.fxd_file = file
        if self.fxd_file and vfs.isfile(self.fxd_file):
            try:
                parser = util.fxdparser.FXD(self.fxd_file)
                parser.set_handler('folder', self.read_folder_fxd)
                parser.set_handler('skin', self.read_folder_fxd)
                parser.parse()
            except:
                print "fxd file %s corrupt" % self.fxd_file
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

        if node.name == 'skin':
            self.skin_settings = True
            return
        
        global all_variables
        set_all = self.fxd_file == self.dir+'/folder.fxd'

        # read attributes
        if set_all:
            self.name = fxd.getattr(node, 'title', self.name)

            image = fxd.childcontent(node, 'cover-img')
            if image and vfs.isfile(os.path.join(self.dir, image)):
                self.image = os.path.join(self.dir, image)

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
            possible_display_types = [ ]

            for p in plugin.get('mimetype'):
                for t in p.display_type:
                    if not t in possible_display_types:
                        possible_display_types.append(t)
                        
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
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        items = [ ( self.cwd, _('Browse directory')) ]

        has_files = False
        has_dirs  = False

        for f in os.listdir(self.dir):
            if not has_files and os.path.isfile(os.path.join(self.dir,f)):
                has_files = True
            if not has_dirs and os.path.isdir(f) and \
                   not f in ('CVS', '.xvpics', '.thumbnails', '.pics'):
                has_dirs = True
            if has_dirs and has_files:
                break

        if has_files:
            items.append((self.play, _('Play all files in directory')))

        if display_type in self.DIRECTORY_AUTOPLAY_ITEMS and not has_dirs:
            items.reverse()

        if has_files:
            items.append((self.play_random, _('Random play all items')))
        if has_dirs:
            items += [ (self.play_random_recursive, _('Recursive random play all items')),
                       (self.play_recursive, _('Recursive play all items')) ]

        items.append((self.configure, _('Configure directory'), 'configure'))
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


    def play_random(self, arg=None, menuw=None):
        """
        play in random order
        """
        self.check_password_and_build(arg='playlist:random', menuw=menuw)
        

    def play_recursive(self, arg=None, menuw=None):
        """
        play recursive
        """
        self.check_password_and_build(arg='playlist:recursive', menuw=menuw)
        

    def play_random_recursive(self, arg=None, menuw=None):
        """
        play recursive in random order
        """
        self.check_password_and_build(arg='playlist:random_recursive', menuw=menuw)
        

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
	    pb = PasswordInputBox(text=_('Enter Password'), handler=self.pass_cmp_cb)
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
        self.playlist   = []
        self.play_items = []
        self.dir_items  = []
        self.pl_items   = []

        if hasattr(self, '__dirwatcher_last_time__'):
            del self.__dirwatcher_last_time__
            
        if arg == 'update':
            if not self.menu.choices:
                selected_pos = -1
            else:
                # store the current selected item
                selected_id  = self.menu.selected.id()
                selected_pos = self.menu.choices.index(self.menu.selected)
            if hasattr(self.menu, 'skin_default_has_description'):
                del self.menu.skin_default_has_description
            if hasattr(self.menu, 'skin_default_no_images'):
                del self.menu.skin_default_no_images
            if hasattr(self.menu, 'skin_force_text_view'):
                del self.menu.skin_force_text_view

        if arg and arg.startswith('playlist:'):
            if arg.endswith(':random'):
                Playlist(playlist = [ (self.dir, 0) ], parent = self,
                         display_type=display_type, random=True).play()
            elif arg.endswith(':recursive'):
                Playlist(playlist = [ (self.dir, 1) ], parent = self,
                         display_type=display_type, random=False).play()
            elif arg.endswith(':random_recursive'):
                Playlist(playlist = [ (self.dir, 1) ], parent = self,
                         display_type=display_type, random=True).play()
            return
        
        display_type = self.display_type
        if self.display_type == 'tv':
            display_type = 'video'

        if config.OSD_BUSYICON_TIMER:
            osd.get_singleton().busyicon.wait(config.OSD_BUSYICON_TIMER[0])
        
        files = vfs.listdir(self.dir)

        self.all_files = copy.copy(files)

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


        elif config.OSD_BUSYICON_TIMER and len(files) > config.OSD_BUSYICON_TIMER[1]:
            # many files, just show the busy icon now
            osd.get_singleton().busyicon.wait(0)
        

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

        #
        # build items
        #

        # build play_items, pl_items and dir_items
        for p in plugin.mimetype(display_type):
            if p.files_only:
                self.play_items += p.get(self, files)
            else:
                for i in p.get(self, files):
                    if i.type == 'playlist':
                        self.pl_items.append(i)
                    elif i.type == 'dir':
                        self.dir_items.append(i)
                    else:
                        self.play_items.append(i)


        # normal DirItems
        for filename in files:
            if vfs.isdir(filename):
                self.dir_items.append(DirItem(filename, self, display_type =
                                              self.display_type))

        #
        # sort all items
        #
        
        # sort directories
        if self.DIRECTORY_SMART_SORT:
            self.dir_items.sort(lambda l, o: util.smartsort(l.dir,o.dir))
        else:
            self.dir_items.sort(lambda l, o: cmp(l.dir.upper(), o.dir.upper()))

        # sort playlist
        self.pl_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))

        # sort normal items
        if self.DIRECTORY_SORT_BY_DATE:
            self.play_items.sort(lambda l, o: cmp(l.sort('date').upper(),
                                                  o.sort('date').upper()))
        else:
            self.play_items.sort(lambda l, o: cmp(l.sort().upper(),
                                                  o.sort().upper()))

        if self.DIRECTORY_REVERSE_SORT:
            self.dir_items.reverse()
            self.play_items.reverse()
            self.pl_items.reverse()

        # delete pl_items if they should not be displayed
        if self.display_type and not self.display_type in self.DIRECTORY_ADD_PLAYLIST_FILES:
            self.pl_items = []

        # add all playable items to the playlist of the directory
        # to play one files after the other
        if not self.display_type or self.display_type in self.DIRECTORY_CREATE_PLAYLIST:
            self.playlist = self.play_items


        # build a list of all items
        items = self.dir_items + self.pl_items + self.play_items

        # random playlist (only active for audio)
        if self.display_type and self.display_type in self.DIRECTORY_ADD_RANDOM_PLAYLIST \
               and len(self.play_items) > 1:
            pl = Playlist(_('Random playlist'), self.play_items, self, random=True)
            pl.autoplay = True
            items = [ pl ] + items



        if pop:
            pop.destroy()
            # closing the poup will rebuild the menu which may umount
            # the drive
            if self.media:
                self.media.mount()

        if config.OSD_BUSYICON_TIMER:
            # stop the timer. If the icons is drawn, it will stay there
            # until the osd is redrawn, if not, we don't need it to pop
            # up the next milliseconds
            osd.get_singleton().busyicon.stop()


        #
        # action
        #
        
        if arg == 'update':
            # update because of dirwatcher changes
            self.menu.choices = items

            if selected_pos != -1:
                for i in items:
                    if i.id() == selected_id:
                        self.menu.selected = i
                        break
                else:
                    # item is gone now, try to the selection close
                    # to the old item
                    pos = max(0, min(selected_pos-1, len(items)-1))
                    if items:
                        self.menu.selected = items[pos]

            self.menuw.init_page()
            self.menuw.refresh()
                

        elif len(items) == 1 and items[0].actions() and \
                 self.DIRECTORY_AUTOPLAY_SINGLE_ITEM:
            # autoplay
            items[0].actions()[0][0](menuw=menuw)

        elif arg=='play' and self.play_items:
            # called by play function
            self.playlist = self.play_items
            Playlist.play(self, menuw=menuw)
            
        else:
            # normal menu build
            item_menu = menu.Menu(self.name, items, reload_func=self.reload,
                                  item_types = self.display_type,
                                  force_skin_layout = self.DIRECTORY_FORCE_SKIN_LAYOUT)

            if self.skin_settings:
                item_menu.skin_settings = skin.load(self.fxd_file)

            if menuw:
                menuw.pushmenu(item_menu)

            dirwatcher.cwd(menuw, self, item_menu, self.dir, self.all_files)
            self.menu  = item_menu
            self.menuw = menuw
        return items


    def reload(self):
        """
        called when we return to this menu
        """
        dirwatcher.cwd(self.menuw, self, self.menu, self.dir, self.all_files)
        dirwatcher.scan()

        # we changed the menu, don't build a new one
        return None


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

        # for DIRECTORY_FORCE_SKIN_LAYOUT max = number of styles in the menu
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
        self.fxd_file = os.path.join(self.dir, 'folder.fxd')

        try:
            parser = util.fxdparser.FXD(self.fxd_file)
            parser.set_handler('folder', self.write_folder_fxd, 'w', True)
            parser.save()
        except:
            print "fxd file %s corrupt" % self.fxd_file
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
            mi = menu.MenuItem(name, self.configure_set_var, i)
            mi.description = descr
            items.append(mi)
        m = menu.Menu(_('Configure'), items)
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
        try:
            self.last_time = item.__dirwatcher_last_time__
        except AttributeError:
            self.last_time = vfs.mtime(self.dir)
            self.item.__dirwatcher_last_time__ = self.last_time
        

    def scan(self, force=False):
        if not self.dir:
            return
        try:
            if config.DIRECTORY_USE_STAT_FOR_CHANGES and \
                   vfs.mtime(self.dir) <= self.last_time:
                return True
        except (OSError, IOError):
            # the directory is gone
            _debug_('Dirwatcher: unable to read directory %s' % self.dir,1)

            # send EXIT to go one menu up:
            rc.post_event(MENU_BACK_ONE_MENU)
            self.dir = None
            return
        

        if not config.DIRECTORY_USE_STAT_FOR_CHANGES:
            try:
                files = vfs.listdir(self.dir, False)
            except OSError:
                # the directory is gone
                _debug_('Dirwatcher: unable to read directory %s' % self.dir,1)

                # send EXIT to go one menu up:
                rc.post_event(MENU_BACK_ONE_MENU)
                self.dir = None
                return

            new_files = []
            del_files = []
            for f in files:
                if not f in self.files:
                    new_files.append(f)
            for f in self.files:
                if not f in files:
                    del_files.append(f)
            self.files = files


        if config.DIRECTORY_USE_STAT_FOR_CHANGES or new_files or del_files:
            _debug_('directory has changed')
            self.item.build(menuw=self.menuw, arg='update')
            self.last_time = vfs.mtime(self.dir)
            self.item.__dirwatcher_last_time__ = self.last_time
                    

    
    def poll(self):
        if self.dir and self.menuw and \
               self.menuw.menustack[-1] == self.item_menu and not rc.app():
            self.scan()

# and activate that DaemonPlugin
dirwatcher = Dirwatcher()
plugin.activate(dirwatcher)
