#if 0 /*
# -----------------------------------------------------------------------
# commands.py - a simple plugin to run arbitrary commands from a directory.
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
# Revision 1.4  2004/01/13 20:40:55  mikeruelle
# We now use childapp2 to run the commands and store our output. We now have
# an fxd file format to run commands in X which people wanted (aka firebird
# plugin).
#
# Revision 1.3  2003/11/30 14:35:43  dischi
# new skin handling
#
# Revision 1.2  2003/11/29 11:41:04  dischi
# use the given menuw and not a global one
#
# Revision 1.1  2003/11/24 17:12:03  dischi
# rename commands.py to command.py to avoid name problems with the global python commands.py
#
# Revision 1.10  2003/11/03 18:08:14  dischi
# oops
#
# Revision 1.9  2003/11/03 18:04:43  dischi
# cleanup, only show dialog when needed, image support
#
# Revision 1.8  2003/10/27 20:15:58  mikeruelle
# make use of outicon
#
# Revision 1.7  2003/10/16 17:49:59  mikeruelle
# put in a small i18n change
#
# Revision 1.6  2003/09/30 17:09:56  mikeruelle
# add a default dir for commands
#
# Revision 1.5  2003/09/14 20:09:36  dischi
# removed some TRUE=1 and FALSE=0 add changed some debugs to _debug_
#
# Revision 1.4  2003/09/13 10:08:22  dischi
# i18n support
#
# Revision 1.3  2003/09/09 18:54:59  dischi
# Add some doc
#
# Revision 1.2  2003/09/01 19:46:02  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.1  2003/08/06 00:25:40  rshortt
# Update the commands plugin from Mike Ruelle and move it into the main
# plugins directory.
#
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
#endif

#python modules
import os, time
import pygame

#freevo modules
import config, menu, rc, plugin, util
import childapp
import osd
from event import *
from item import Item
from gui import AlertBox, RegionScroller, ListBox, PopupBox, Align
import traceback


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
        #print  self.filetext

        PopupBox.__init__(self, parent, text, handler, left, top, width, height,
                          bg_color, fg_color, icon, border, bd_color, bd_width)


        self.set_h_align(Align.CENTER)
        test = 'AAAAAAAAAA'
        myfont = self.osd.getfont(config.OSD_DEFAULT_FONTNAME, config.OSD_DEFAULT_FONTSIZE)
        surf_w = myfont.stringsize(test*8) 
        data = self.osd.drawstringframed(self.filetext, 0, 0, surf_w, 1000000,
                                         myfont,
                                         align_h='left',
                                         align_v='top',
                                         fgcolor=self.osd.COL_BLACK,
                                         mode='hard',
                                         layer='')[1]
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
    def __init__(self, parent='osd', text=None, handler=None,
                 left=None, top=None, width=600, height=300, bg_color=None,
                 fg_color=None, icon=None, border=None, bd_color=None,
                 bd_width=None, vertical_expansion=1):
        
        if not text:
            text = _('Command finished')
        
        PopupBox.__init__(self, parent, text, handler, left, top, width, height,
                          bg_color, fg_color, icon, border, bd_color, bd_width,
                          vertical_expansion)
        
        items_height = 40
        self.num_shown_items = 3
        self.results = ListBox(width=(self.width-2*self.h_margin),
                               height=self.num_shown_items*items_height,
                               show_v_scrollbar=0)
        self.results.y_scroll_interval = self.results.items_height = items_height
        
        self.results.set_h_align(Align.CENTER)
        self.add_child(self.results)
        self.results.add_item(text=_('OK'), value='ok')
        if islog('err'):
            self.results.add_item(text=_('Show Stderr'), value='err')
        if islog('out'):
            self.results.add_item(text=_('Show Stdout'), value='out')
        self.results.toggle_selected_index(0)
        


    def eventhandler(self, event, menuw=None):
                                                                                
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
                                                                                


class CommandItem(Item):
    """
    This is the class that actually runs the commands. Eventually
    hope to add actions for different ways of running commands
    and for displaying stdout and stderr of last command run.
    """
    def __init__(self, command=None, directory=None, xmlfile=None):
        Item.__init__(self)
	self.stoposd = 0
	self.use_wm = None
	self.spawnwm = config.COMMAND_SPAWN_WM
	self.killwm = config.COMMAND_KILL_WM
	if command and directory:
            self.name = command
            self.cmd  = os.path.join(directory, command)
            self.image = util.getimage(self.cmd)
        elif xmlfile:
	    #create using xmlfile
            try:
	        self.xml_file = xmlfile
                parser = util.fxdparser.FXD(self.xml_file)
                parser.set_handler('command', self.read_command_fxd)
	        parser.parse()
	    except:
	        print "fxd file %s corrupt" % self.xml_file
                traceback.print_exc()
	else:
	    print "bad things...."
	

    def read_command_fxd(self, fxd, node):
        '''
        parse the file for command settings
                                                                                
        <?xml version="1.0" ?>
        <freevo>
          <command title="Mozilla">
            <cmd>/usr/local/bin/mozilla</cmd>
            <stoposd>1</stoposd>
	    <spawnwm>1</spawnwm>
            <info>
              <content>Unleash mozilla on the www</content>
            </info>
          </command>
        </freevo>
        '''
        self.name = fxd.getattr(node, 'title')
        self.cmd = fxd.childcontent(node, 'cmd')
        self.image = util.getimage(self.cmd)
        self.stoposd = fxd.childcontent(node, 'stoposd')
        self.use_wm = fxd.childcontent(node, 'spawnwm')

        # parse <info> tag
        fxd.parse_info(fxd.get_children(node, 'info', 1), self,
                       {'description': 'content', 'content': 'content' })

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.flashpopup , _('Run Command') ) ]
        return items

    def flashpopup(self, arg=None, menuw=None):
        if self.stoposd:
	    if self.use_wm:
	        os.system(self.spawnwm)
	else:
            popup_string=_("Running Command...")
            pop = PopupBox(text=popup_string)
            pop.show()

	workapp = childapp.ChildApp2(self.cmd, 'command', 1, self.stoposd)
	while workapp.isAlive():
	    for child in childapp.running_children:
	        if child != workapp:
	            child.poll()
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

        if not self.stoposd:
            CommandOptions(text=message).show()
        

class CommandMainMenuItem(Item):
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
        command_items = []
        commands = os.listdir(config.COMMANDS_DIR)
        commands.sort(lambda l, o: cmp(l.upper(), o.upper()))
        for command in commands:
            if os.path.splitext(command)[1] in ('.jpg', '.png'):
                continue
            if os.path.splitext(command)[1] in ('.fxd', '.xml'):
		myxmlfile=os.path.join(config.COMMANDS_DIR, command)
                cmd_item = CommandItem(xmlfile=myxmlfile)
	    else:
                cmd_item = CommandItem(command, config.COMMANDS_DIR)
            command_items += [ cmd_item ]
        if (len(command_items) == 0):
            command_items += [menu.MenuItem(_('No Commands found'),
                                            menuw.goto_main_menu, 0)]
        command_menu = menu.Menu(_('Commands'), command_items)
        rc.app(None)
        menuw.pushmenu(command_menu)
        menuw.refresh()



class PluginInterface(plugin.MainMenuPlugin):
    """
    A small plugin to run commands from the main menu. Currently supports only small
    scripts which need no inputs. All output is logged in the freevo logdir, and
    success or failure is determined on the return value of the command. You can now
    also view the log file after the command has finished in freevo itself.

    to activate it, put the following in your local_conf.py:

    plugin.activate('commands', level=45) 
    COMMANDS_DIR = '/usr/local/freevo_data/Commands' 

    The level argument is used to influence the placement in the Main Menu. consult
    freevo_config.py for the level of the other Menu Items if you wish to place it
    in a particular location.
    """
    def items(self, parent):
        return [ CommandMainMenuItem(parent) ]

    def config(self):
        return [ ('COMMANDS_DIR', '/usr/local/bin', 'The directory to show commands from.'),
                 ('COMMAND_SPAWN_WM', '', 'command to start window manager.'),
                 ('COMMAND_KILL_WM', '', 'command to stop window manager.'),
	]

