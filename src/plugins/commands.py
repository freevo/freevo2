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
import os, popen2, fcntl, select, time
import pygame

#freevo modules
import config, menu, rc, plugin, skin, util

import event as em
from item import Item

from gui.AlertBox import AlertBox
from gui.RegionScroller import RegionScroller
from gui.ListBox import ListBox
from gui.AlertBox import PopupBox
from gui.GUIObject import Align

#get the sinfletons so we can add our menu and get skin info
skin = skin.get_singleton()
menuwidget = menu.get_singleton()

TRUE = 1
FALSE = 0

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

        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT ):
           return self.pb.eventhandler(event)

        elif event == em.INPUT_ENTER or event == em.INPUT_EXIT:
            self.destroy()

        else:
            return self.parent.eventhandler(event)



class CommandOptions(PopupBox):
    def __init__(self, parent='osd', text=None, handler=None,
                 left=None, top=None, width=600, height=300, bg_color=None,
                 fg_color=None, icon=None, border=None, bd_color=None,
                 bd_width=None, vertical_expansion=1):
        
        if not text:
            text = 'Command finished'
        
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
        self.results.add_item(text='OK', value='ok')
        self.results.add_item(text='Show Stderr', value='err')
        self.results.add_item(text='Show Stdout', value='out')
        self.results.toggle_selected_index(0)
        
    def eventhandler(self, event, menuw=None):
                                                                                
        if event in (em.INPUT_UP, em.INPUT_DOWN, em.INPUT_LEFT, em.INPUT_RIGHT):
            return self.results.eventhandler(event)
        elif event == em.INPUT_ENTER:
            selection = self.results.get_selected_item().value
            #print selection
            if selection == 'ok':
                self.destroy()
            elif selection == 'out':
                LogScroll(os.path.join(config.LOGDIR,'command_stdout.log'),
                          text='Stdout File').show()
                return
            elif selection == 'err':
                LogScroll(os.path.join(config.LOGDIR,'command_stderr.log'),
                          text='Stderr File').show()
                return
        elif event == em.INPUT_EXIT:
            self.destroy()
        else:
            return self.parent.eventhandler(event)
                                                                                


# This is the class that actually runs the commands. Eventually
# hope to add actions for different ways of running commands
# and for displaying stdout and stderr of last command run.
class CommandItem(Item):

    def makeNonBlocking(self, fd):
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)


    def getCommandOutput(self, command, outputfile, erroutputfile):
        child = popen2.Popen3(command, 1) # capture stdout and stderr from command
        child.tochild.close()             # don't need to talk to child
        outfile = child.fromchild 
        outfd = outfile.fileno()
        errfile = child.childerr
        errfd = errfile.fileno()
        self.makeNonBlocking(outfd)            # don't deadlock!
        self.makeNonBlocking(errfd)
        outeof = erreof = 0
        while 1:
            ready = select.select([outfd,errfd],[],[]) # wait for input
            if outfd in ready[0]:
                outchunk = outfile.read()
                if outchunk == '': outeof = 1
                outputfile.write(outchunk)
            if errfd in ready[0]:
                errchunk = errfile.read()
                if errchunk == '': erreof = 1
                erroutputfile.write(errchunk)
            if outeof and erreof: break
            select.select([],[],[],.1) # give a little time for buffers to fill
        err = child.wait()
        if (os.WIFEXITED(err)):
            outputfile.write('process exited with status ' + str(os.WEXITSTATUS(err)))
        if (os.WIFSTOPPED(err)):
            outputfile.write('process  ws stopped with signal ' + str(os.WSTOPSIG(err)))
        if (os.WIFSIGNALED(err)):
            outputfile.write('process terminated with signal ' + str(os.WTERMSIG(err)))
        return err

    def actions(self):
        """
        return a list of actions for this item
        """
        items = [ ( self.flashpopup , 'Run Command' ) ]
        return items

    #  1) make running popup
    #  2) run command (spawn and then get exit status)
    #  3) figure out success/failure status (pick correct msg and icon)
    #  4) dispose running popup
    #  5) make new alert popup with messages
    def flashpopup(self, arg=None, menuw=None):
        popup_string="Running Command..."
        pop = PopupBox(text=popup_string)
        pop.show()
        #print self.cmd
        myout = open(os.path.join(config.LOGDIR,'command_stdout.log'), 'wb')
        myerr = open(os.path.join(config.LOGDIR,'command_stderr.log'), 'wb')
        status = self.getCommandOutput(self.cmd, myout, myerr)
        myout.close()
        myerr.close()
        #print status
        icon=""
        message=""
        if status:
            icon='bad'
            message='Command Failed'
        else:
            icon='ok'
            message='Command Completed'
        pop.destroy()
        CommandOptions(text=message).show()
        

# this is the item for the main menu and creates the list
# of commands in a submenu.
class CommandMainMenuItem(Item):
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
            cmd_item = CommandItem()
            cmd_item.name = command
            cmd_item.cmd = os.path.join(config.COMMANDS_DIR, command)
            command_items += [ cmd_item ]
        if (len(command_items) == 0):
            command_items += [menu.MenuItem('No Commands found', menuwidget.goto_prev_page, 0)]
        command_menu = menu.Menu('Commands', command_items, reload_func=menuwidget.goto_main_menu)
        rc.app(None)
        menuwidget.pushmenu(command_menu)
        menuwidget.refresh()

# our plugin wrapper, just creates the main menu item and adds it.
class PluginInterface(plugin.MainMenuPlugin):
    def items(self, parent):
        menu_items = skin.settings.mainmenu.items

        item = CommandMainMenuItem()
        item.name = 'Commands'
        if menu_items.has_key('commands') and menu_items['commands'].icon:
            item.icon = os.path.join(skin.settings.icon_dir, menu_items['commands'].icon)
        if menu_items.has_key('commands') and menu_items['commands'].image:
            item.image = menu_items['commands'].image

        item.parent = parent
        return [ item ]


