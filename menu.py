#
# menu.py - freevo menu handling system
#
# $Id$

import sys, os, time

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The OSD class, used to communicate with the OSD daemon
import osd

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# Create the remote control object
rc = rc.get_singleton()


# Module variable that contains an initialized MenuWidget() object
_singleton = None

def get_singleton():
    global _singleton

    # One-time init
    if _singleton == None:
        _singleton = MenuWidget()
        
    return _singleton



class MenuItem:

    def __init__(self, name, action=None, arg=None):
        self.name = name
        self.action = action
        self.arg = arg
        

    def select(self):
        self.action(self.arg)

        
class Menu:

    def __init__(self, heading, choices, packrows=1):
        # XXX Add a list of eventhandlers?
        self.heading = heading
        self.choices = choices          # List of MenuItem:s
        self.page_start = 0
        self.packrows = packrows
        self.bgbitmap = ('', 0, 0)
        

#
# The MenuWidget handles a stack of Menu:s
#
class MenuWidget:

    def __init__(self):
        self.osd = osd.get_singleton()
        self.menustack = []
        self.items_per_page = 13
        self.prev_page = MenuItem('Prev Page', self.goto_prev_page)
        self.next_page = MenuItem('Next Page', self.goto_next_page)
        self.back_menu = MenuItem('Back', self.back_one_menu)
        self.main_menu = MenuItem('Main', self.goto_main_menu)


    def back_one_menu(self, arg=None, menuw=None):
        if len(self.menustack) > 1:
            self.menustack = self.menustack[:-1]
            menu = self.menustack[-1]
            self.init_page()
            self.refresh()

    
    def goto_main_menu(self, arg=None, menuw=None):
        self.menustack = [self.menustack[0]]
        menu = self.menustack[0]
        self.init_page()
        self.refresh()

    
    def goto_prev_page(self, arg=None, menuw=None):
        menu = self.menustack[-1]
        if menu.page_start != 0:
            menu.page_start -= self.items_per_page
        self.init_page()
        menu.selected = self.all_items[0]
        self.refresh()

    
    def goto_next_page(self, arg=None, menuw=None):
        menu = self.menustack[-1]
        if menu.page_start + self.items_per_page < len(menu.choices):
            menu.page_start += self.items_per_page
        self.init_page()
        menu.selected = self.menu_items[-1]
        self.refresh()
    
    
    def pushmenu(self, menu):
        menu.page_start = 0
        self.menustack += [menu]
        self.init_page()
        menu.selected = self.all_items[0]
        self.refresh()


    def refresh(self):
        self.osd.clearscreen(self.osd.COL_WHITE)

        menu = self.menustack[-1]

        if not menu:
            osd.drawstring('INTERNAL ERROR, NO MENU!', 100, osd.height/2)
            return

        if menu.bgbitmap[0]:
            apply(self.osd.drawbitmap, menu.bgbitmap)
            
        # Menu heading
        self.osd.drawstring(menu.heading, 160, 50,
                            font=config.OSD_FONTNAME_HDR,
                            ptsize=config.OSD_FONTSIZE_HDR)
        
        # Draw a box around the selection area
        self.osd.drawbox(40, 85, 720, 490, width=3,
                             color=self.osd.COL_BLACK)
        
        # Draw the menu choices for the main selection
        x0 = 60
        y0 = 100
        selection_height = 390
        if menu.packrows:
            spacing = selection_height / self.items_per_page
        else:
            spacing = selection_height / max(len(self.menu_items),1)
        for choice in self.menu_items:
            if len(self.menustack) == 1:
                ptscale = 2.0
            else:
                ptscale = 1.0
            fontsize = config.OSD_FONTSIZE_ITEMS*ptscale
            self.osd.drawstring(choice.name, x0, y0,
                            font=config.OSD_FONTNAME_ITEMS,
                            ptsize=fontsize)
            if menu.selected == choice:
                self.osd.drawbox(x0 - 8, y0 - 3, 705, y0 + fontsize*1.5, width=-1,
                             color=((160 << 24) | self.osd.COL_ORANGE))
            y0 += spacing

        # Draw the menu choices for the meta selection
        x0 = 40
        y0 = 505
        for item in self.nav_items:
            fontsize = config.OSD_FONTSIZE_BTNS*ptscale
            self.osd.drawstring(item.name, x0, y0,
                            font=config.OSD_FONTNAME_BTNS,
                            ptsize=fontsize)
            if menu.selected == item:
                self.osd.drawbox(x0 - 4, y0 - 3, x0 + 150, y0 + fontsize*1.5,
                                 width=-1,
                                 color=((160 << 24) | self.osd.COL_ORANGE))
            x0 += 190

        self.osd.update()
        
        
    def eventhandler(self, event):
        menu = self.menustack[-1]
        if event == rc.UP:
            curr_selected = self.all_items.index(menu.selected)
            curr_selected = max(curr_selected-1, 0)
            menu.selected = self.all_items[curr_selected]
            self.refresh()
        elif event == rc.DOWN:
            curr_selected = self.all_items.index(menu.selected)
            curr_selected = min(curr_selected+1, len(self.all_items)-1)
            menu.selected = self.all_items[curr_selected]
            self.refresh()
        elif event == rc.LEFT:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            curr_selected = self.all_items.index(menu.selected)

            # Move to the previous page if the current position is at the
            # top of the list, otherwise move to the top of the list.
            if curr_selected == 0:
                self.goto_prev_page()
            else:
                curr_selected = 0
                menu.selected = self.all_items[curr_selected]
                self.refresh()
        elif event == rc.RIGHT:
            # Do nothing for an empty file list
            if not len(self.menu_items):
                return
            
            curr_selected = self.all_items.index(menu.selected)
            bottom_index = self.menu_items.index(self.menu_items[-1])
            
            # Move to the next page if the current position is at the
            # bottom of the list, otherwise move to the bottom of the list.
            if curr_selected >= bottom_index:
                self.goto_next_page()
            else:
                curr_selected = bottom_index
                menu.selected = self.all_items[curr_selected]
                self.refresh()
        elif event == rc.MENU:
            self.goto_main_menu()
        elif event == rc.EXIT:
            self.back_one_menu()
        elif event == rc.SELECT or event == rc.PLAY:
            action = menu.selected.action
            if action == None:
                self.osd.clearscreen()
                self.osd.drawstring('No action defined', 230, 280)
                time.sleep(2.0)
                self.refresh()
            else:
                action_str = str(action)
                arg_str = str(menu.selected.arg)[0:40]
                self.osd.clearscreen()
                self.osd.drawstring('Action: %s' % action_str, 50, 240)
                self.osd.drawstring('Args: %s' % arg_str, 50, 280)
                print 'Calling action "%s"' % str(action)
                action(arg=menu.selected.arg, menuw=self)


    def init_page(self):
        menu = self.menustack[-1]
       
        if not menu:
            return

        # Create the list of main selection items (menu_items)
        menu_items = []
        first = menu.page_start
        for choice in menu.choices[first : first+self.items_per_page]:
            menu_items += [choice]
     
        # Create the list of navigation items (nav_items)
        nav_items = []
        if menu.page_start + self.items_per_page < len(menu.choices):
            nav_items += [self.next_page]
        if menu.page_start != 0:
            nav_items += [self.prev_page]
        if len(self.menustack) >= 3:
            nav_items += [self.back_menu]
        if len(self.menustack) >= 2:
            nav_items += [self.main_menu]

        self.menu_items = menu_items
        self.nav_items = nav_items

        self.all_items = self.menu_items + self.nav_items
