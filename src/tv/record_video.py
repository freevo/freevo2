#if 0 /*
# -----------------------------------------------------------------------
# record_video - Video Recording
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2002/11/25 02:17:54  krister
# Minor bugfixes. Synced to changes made in the main tree.
#
# Revision 1.1  2002/11/25 01:56:03  krister
# Updated from old src tree.
#
# Revision 1.1  2002/11/24 07:21:25  krister
# Clean. Started working on a simple TV recording menu.
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

import sys
import time

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The OSD class
import osd

# The menu widget class
import menu

# The mixer class, controls the volumes for playback and recording
import mixer

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The TV application
import tv

# The Skin
import skin

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

# Create the remote control object
rc = rc.get_singleton()

# Set up the mixer
mixer = mixer.get_singleton()

menuwidget = menu.get_singleton()

skin = skin.get_singleton()


class Setting:

    def __init__(self, name, choices, selected = None, fmt_str = None):
        self.name = name
        self.choices = choices
        if not selected:
            self.selected = self.choices[0]
        else:
            self.selected = selected
        if not fmt_str:
            fmt_str = '%s %%s' % name
        self.fmt_str = fmt_str


    def set_selected(self, selected):
        self.selected = selected


    def __str__(self):
        s = self.fmt_str % self.selected
        return s
    

# XXX Clean up, make this a real class
class Struct:
    pass

recinfo = Struct()
recinfo.channel = None

recinfo.program_name = None
recinfo.start_date = None

start_times = map(lambda t: time.strftime('%H:%M', time.gmtime(t)), range(0, 86400, 900))
recinfo.start_time = Setting('Start', start_times, None, 'Start time %s')

recinfo.length = Setting('Length', [10, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300],
                         30, 'Length %s minutes')

recinfo.quality = Setting('Quality', ['low', 'medium', 'high'], 'high')



def main_menu(prog):
    recinfo.channel = prog.channel_id
    
    recinfo.program_name = Setting('Program name', [prog.title, '[Timestamp]'],
                         None, 'Program name: %s')
    
    length_minutes = (prog.stop - max(prog.start, time.time())) / 60.0
    if (length_minutes - int(length_minutes)) > 0.01:
        recinfo.length.set_selected(int(length_minutes)+1)
    else:
        recinfo.length.set_selected(int(length_minutes))

    prog_time = time.strftime('%H:%M', time.localtime(max(prog.start, time.time())))
    recinfo.start_time.set_selected(prog_time)
    
    rc.app = None # XXX We'll jump back to the main menu for now, should be the TV menu

    days = []
    today = time.time()
    for i in range(60):
        day = time.strftime('%Y-%m-%d', time.localtime(today + 86400*i))
        days.append(day)

    prog_day = time.strftime('%Y-%m-%d', time.localtime(prog.start))
    recinfo.start_date = Setting('Start Date', days, prog_day)

    recmenu = generate_main()
    
    menuwidget.pushmenu(recmenu)
    menuwidget.refresh()
    

def generate_main():
    print 'REC: generate_main'
    
    items = []

    items += [menu.MenuItem('Select Recording Name (%s)' % recinfo.program_name.selected,
                            selection_menu, recinfo.program_name)]
    
    items += [menu.MenuItem('Select Start Date (%s)' % recinfo.start_date.selected,
                            selection_menu, recinfo.start_date)]
    
    items += [menu.MenuItem('Select Start Time (%s)' % recinfo.start_time.selected,
                            selection_menu, recinfo.start_time)]
    
    format_func = lambda val: '%s minutes' % val
    items += [menu.MenuItem('Select length (%s minutes)' % recinfo.length.selected,
                            selection_menu, recinfo.length)]

    format_func = lambda val: 'Quality %s' % val
    items += [menu.MenuItem('Select quality (%s)' % recinfo.quality.selected,
                            selection_menu, recinfo.quality)]

    items += [menu.MenuItem('Schedule recording', set_schedule)]

    recmenu = menu.Menu('RECORD CHANNEL %s' % recinfo.channel, items, reload_func=generate_main)

    return recmenu


def selection_menu(arg=None, menuw=None):
    items = []

    setting = arg
    for val in setting.choices:
        items += [ menu.MenuItem(setting.fmt_str % val, set_selection, (setting, val)) ]

    submenu = menu.Menu('SELECT LENGTH', items)
    menuw.pushmenu(submenu)


def set_selection(arg=None, menuw=None):
    setting, selected = arg

    print 'REC: set_sel %s, %s' % (setting.name, selected)

    setting.set_selected(selected)
    
    menuw.back_one_menu()

        
def set_schedule(arg=None, menuw=None):

    s = 'Scheduled recording:\n'
    s += 'Channel %s\n' % recinfo.channel
    s += '%s %s %s min' % (recinfo.start_date.selected, recinfo.start_time.selected,
                           recinfo.length.selected)
    print '"%s"' % s
    skin.PopupBox(s)
    time.sleep(3)
    menuw.refresh()
