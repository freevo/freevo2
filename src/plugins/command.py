# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# command.py - a simple plugin to run arbitrary commands from a directory.
#               it determines success or failure of command based on its
#               exit status.
# -----------------------------------------------------------------------
# $Id$
#
# Notes: no echo of output of command to screen. 
#        To use add the following to local_conf.py:
#        plugin.activate('commands', level=45)
#        COMMANDS_DIR = '/usr/local/freevo_data/Commands'
# Todo: find a way to prompt for arguments. interactive display of output?
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.19  2004/10/06 19:15:12  dischi
# use new childapp interface
#
# Revision 1.18  2004/10/05 19:51:49  dischi
# remove bad import
#
# Revision 1.17  2004/08/28 17:16:32  dischi
# doc fix
#
# Revision 1.16  2004/08/23 12:39:59  dischi
# remove osd.py dep
#
# Revision 1.15  2004/08/01 10:49:47  dischi
# deactivate plugin
#
# Revision 1.14  2004/07/22 21:21:49  dischi
# small fixes to fit the new gui code
#
# Revision 1.13  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.12  2004/06/11 00:35:57  mikeruelle
# move config method to where it can do some good
#
# Revision 1.11  2004/05/30 18:28:15  dischi
# More event / main loop cleanup. rc.py has a changed interface now
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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


#python modules
import os, time
import pygame

#freevo modules
import config
import menu
import plugin
import util
import childapp
import fxditem

from event import *
from item import Item
# from gui import ListBox
# from gui import RegionScroller
from gui import PopupBox

def islog(name):
    f = open(os.path.join(config.LOGDIR,'command-std%s.log' % name))
    data = f.readline()
    if name == 'out':
        data = f.readline()
    f.close()
    return data
    
    
class LogScroll(PopupBox):
    """
    left      x coordinate. Integer
    top       y coordinate. Integer
    width     Integer
    height    Integer
    text      String to print.
    bg_color  Background color (Color)
    fg_color  Foreground color (Color)
    icon      icon
    border    Border
    bd_color  Border color (Color)
    bd_width  Border width Integer
    """

    def __init__(self, file, parent='osd', text=' ', left=None, top=None, width=500,
                 height=350, bg_color=None, fg_color=None, icon=None,
                 border=None, bd_color=None, bd_width=None):

        handler = None
        self.file = file
        self.filetext = open(self.file, 'rb').read()

        PopupBox.__init__(self, text, handler, top, left, width, height,
                          icon, None, None, parent)

        myfont = self.osd.getfont(config.OSD_DEFAULT_FONTNAME, config.OSD_DEFAULT_FONTSIZE)
        surf_w = myfont.stringsize('AAAAAAAAAA'*8) 
        data = self.osd.drawstringframed(self.filetext, 0, 0, surf_w, 1000000,
                                         myfont, align_h='left', align_v='top',
                                         fgcolor=self.osd.COL_BLACK,
                                         mode='hard', layer='')[1]
        (ret_x0,ret_y0, ret_x1, ret_y1) = data
        surf_h = ret_y1 - ret_y0
        if height>surf_h:
            surf_h=height
        surf = pygame.Surface((surf_w, surf_h), 0, 32)
        bg_c = self.bg_color.get_color_sdl()
        surf.fill(bg_c)
        self.osd.drawstringframed(self.filetext, 0, 0, surf_w, surf_h,
                                  myfont,
                                  align_h='left',
                                  align_v='top',
                                  fgcolor=self.osd.COL_BLACK,
                                  mode='hard',
                                  layer=surf)
        self.pb = RegionScroller(surf, 50,50, width=width, height=height)
        self.add_child(self.pb)


    def eventhandler(self, event, menuw=None):

        if event in (INPUT_UP, INPUT_DOWN, INPUT_LEFT, INPUT_RIGHT ):
           return self.pb.eventhandler(event)

        elif event == INPUT_ENTER or event == INPUT_EXIT:
            self.destroy()

        else:
            return self.parent.eventhandler(event)



class CommandOptions(PopupBox):
    """
    Show the command results
    """
    def __init__(self, parent='osd', text=None, handler=None,
                 left=None, top=None, width=600, height=300, bg_color=None,
                 fg_color=None, icon=None, border=None, bd_color=None,
                 bd_width=None, vertical_expansion=1):
        
        if not text:
            text = _('Command finished')
        
        #PopupBox.__init__(self, text, handler=handler, x=top, y=left, width=width, height=height)
        PopupBox.__init__(self, text, handler, top, left, width, height,
                          icon, vertical_expansion, None, parent)

        items_height = 40
        self.num_shown_items = 3
        self.results = ListBox(width=(self.width-2*self.h_margin),
                               height=self.num_shown_items*items_height,
                               show_v_scrollbar=0)
        self.results.y_scroll_interval = self.results.items_height = items_height
        
        self.add_child(self.results)
        self.results.add_item(text=_('OK'), value='ok')
        if islog('err'):
            self.results.add_item(text=_('Show Stderr'), value='err')
        if islog('out'):
            self.results.add_item(text=_('Show Stdout'), value='out')
        self.results.toggle_selected_index(0)
        


    def eventhandler(self, event, menuw=None):
        """
        eventhandler to browse the result popup
        """
        if event in (INPUT_UP, INPUT_DOWN, INPUT_LEFT, INPUT_RIGHT):
            return self.results.eventhandler(event)
        elif event == INPUT_ENTER:
            selection = self.results.get_selected_item().value
            #print selection
            if selection == 'ok':
                self.destroy()
            elif selection == 'out':
                LogScroll(os.path.join(config.LOGDIR,'command-stdout.log'),
                          text=_('Stdout File')).show()
                return
            elif selection == 'err':
                LogScroll(os.path.join(config.LOGDIR,'command-stderr.log'),
                          text=_('Stderr File')).show()
                return
        elif event == INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)
                                                                                

class CommandChild( childapp.Instance ):
    def poll(self):
        pass

    
class CommandItem(Item):
    """
    This is the class that actually runs the commands. Eventually
    hope to add actions for different ways of running commands
    and for displaying stdout and stderr of last command run.
    """
    def __init__(self, command=None, directory=None):
        Item.__init__(self, skin_type='commands')
	self.display_type = 'commands'
	self.stoposd = False
	self.use_wm  = False
	self.spawnwm = config.COMMAND_SPAWN_WM
	self.killwm  = config.COMMAND_KILL_WM
        self.stdout  = True
	if command and directory:
            self.name = command
            self.cmd  = os.path.join(directory, command)
            self.image = util.getimage(self.cmd)


    def actions(self):
        """
        return a list of actions for this item
        """
        return [ ( self.flashpopup , _('Run Command') ) ]


    def flashpopup(self, arg=None, menuw=None):
        """
        start popup and execute command
        """
        if self.stoposd:
	    if self.use_wm:
	        os.system(self.spawnwm)
	else:
            popup_string=_("Running Command...")
            pop = PopupBox(text=popup_string)
            pop.show()

	workapp = CommandChild(self.cmd, 'command', 1, self.stoposd)
	while workapp.isAlive():
            # make sure all callbacks in rc are running
            rc.poll()
            # wait some time
	    time.sleep(0.5)

        if self.stoposd:
	    if self.use_wm:
	        os.system(self.killwm)
	        time.sleep(0.5)
	else:
            pop.destroy()
	workapp.stop()
	message = ''
	if workapp.status:
	    message = _('Command Failed')
        else:
            message = _('Command Completed')

        if not self.stoposd and self.stdout:
            CommandOptions(text=message).show()
        

def fxdparser(fxd, node):
    """
    parse commands out of a fxd file
    """
    item = CommandItem()
    item.name    = fxd.getattr(node, 'title')
    item.cmd     = fxd.childcontent(node, 'cmd')
    item.image   = util.getimage(item.cmd)
    if fxd.get_children(node, 'stoposd'):
        item.stoposd = True
    if fxd.get_children(node, 'spawnwm'):
        item.use_wm  = True
    if fxd.get_children(node, 'nostdout'):
        item.stdout =  False
    
    # parse <info> tag
    fxd.parse_info(fxd.get_children(node, 'info', 1), item)
    fxd.getattr(None, 'items', []).append(item)
    

class CommandMenuItem(Item):
    """
    this is the item for the main menu and creates the list
    of commands in a submenu.
    """
    def __init__(self, parent):
        Item.__init__(self, parent, skin_type='commands')
        self.name = _('Commands')

        
    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.create_commands_menu , 'commands' ) ]
        return items

 
    def create_commands_menu(self, arg=None, menuw=None):
        """
        create a list with commands
        """
        command_items = []
        for command in os.listdir(config.COMMANDS_DIR):
            if os.path.splitext(command)[1] in ('.jpg', '.png'):
                continue
            if os.path.splitext(command)[1] in ('.fxd', '.xml'):
		fxd_file=os.path.join(config.COMMANDS_DIR, command)

                # create a basic fxd parser
                parser = util.fxdparser.FXD(fxd_file)

                # create items to add
                parser.setattr(None, 'items', command_items)

                # set handler
                parser.set_handler('command', fxdparser)
                
                # start the parsing
                parser.parse()
	    else:
                cmd_item = CommandItem(command, config.COMMANDS_DIR)
                command_items.append(cmd_item)

        command_items.sort(lambda l, o: cmp(l.name.upper(), o.name.upper()))
        command_menu = menu.Menu(_('Commands'), command_items)
        menuw.pushmenu(command_menu)
        menuw.refresh()



class PluginInterface(plugin.MainMenuPlugin):
    """
    A small plugin to run commands from the main menu. Currently supports only small
    scripts which need no inputs. All output is logged in the freevo logdir, and
    success or failure is determined on the return value of the command. You can now
    also view the log file after the command has finished in freevo itself.

    to activate it, put the following in your local_conf.py:

    plugin.activate('command', level=45) 
    COMMANDS_DIR = '/usr/local/freevo_data/Commands' 

    The level argument is used to influence the placement in the Main Menu. consult
    freevo_config.py for the level of the other Menu Items if you wish to place it
    in a particular location.

    This plugin also activates <command> tag support in all menus, see information
    from command.fxdhandler for details.
    """
    def __init__(self):
        self.reason = config.REDESIGN_BROKEN
        return

        # register command to normal fxd item parser
        # to enable <command> tags in fxd files in every menu
        plugin.register_callback('fxditem', [], 'command', fxdparser)
        plugin.MainMenuPlugin.__init__(self)
        
    def items(self, parent):
        return [ CommandMenuItem(parent) ]

    def config(self):
        return [ ('COMMANDS_DIR', '/usr/local/bin', 'The directory to show commands from.'),
                 ('COMMAND_SPAWN_WM', '', 'command to start window manager.'),
                 ('COMMAND_KILL_WM', '', 'command to stop window manager.'),
	]


class fxdhandler(plugin.Plugin):
    """
    Small plugin to enable <command> tags inside fxd files in every menu. You
    don't need this plugin if you activate the complete 'command' plugin.

    to activate it, put the following in your local_conf.py:
    plugin.activate('command.fxdhandler')

    Sample fxd file starting mozilla:
    <?xml version="1.0" ?>
    <freevo>
      <command title="Mozilla">
        <cmd>/usr/local/bin/mozilla</cmd>
        <stoposd />  <!-- stop osd before starting -->
        <spawnwm />  <!-- start windowmanager -->
        <nostdout /> <!-- do not show stdout on exit -->
        <info>
          <description>Unleash mozilla on the www</description>
        </info>
      </command>
    </freevo>

    Putting a <command> in a folder.fxd will add this command to the list of
    item actions for that directory.
    """
    def __init__(self):
        # register command to normal fxd item parser
        # to enable <command> tags in fxd files in every menu
        plugin.register_callback('fxditem', [], 'command', fxdparser)
        plugin.Plugin.__init__(self)
        
class CommandMainMenuItem(plugin.MainMenuPlugin):
    """
    A small plugin to put a command in the main menu.
    Uses the command.py fxd file format to say which command to run.
    All output is logged in the freevo logdir.
    to activate it, put the following in your local_conf.py:

    plugin.activate('command.CommandMainMenuItem', args=(/usr/local/freevo_data/Commands/Mozilla.fxd', ), level=45) 

    The level argument is used to influence the placement in the Main Menu.
    consult freevo_config.py for the level of the other Menu Items if you
    wish to place it in a particular location.
    """
    def __init__(self, commandxmlfile):
        plugin.MainMenuPlugin.__init__(self)
        self.cmd_xml = commandxmlfile
    
    def config(self):
        return [ ('COMMAND_SPAWN_WM', '', 'command to start window manager.'),
                 ('COMMAND_KILL_WM', '', 'command to stop window manager.') ]

    def items(self, parent):
        command_items = []
        parser = util.fxdparser.FXD(self.cmd_xml)
        parser.setattr(None, 'items', command_items)
        parser.set_handler('command', fxdparser)
        parser.parse()
        cmd_item = command_items[0]
        return [ cmd_item ]

