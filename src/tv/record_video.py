#if 0 /*
# -----------------------------------------------------------------------
# record_video - Video Recording
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# I use mp1e, some people use lavrec, but as long as the command-line options
# they take can be expressed in terms of some simple options, you can add support
# for them without editing the config.
#
# for example, I use this:
# VCR_CMD = ('/usr/bin/schedulerec '+
#            '%(channel)s %(timecode)s ' +
#                       '%(filename)s.mpg')
#
#
# I've modified freevo_config so mencoder works as before.
#
# ---
#
# Other change is adding the Channel ID to the freevo_record.lst file, which is
# used by my skin (for now) to highlight scheduled shows in red.
#
# Last of all, I swapped the filename - time to be time - filename for recording
# shows, because logically, it'll swap them by recording time which seems to make
# more sense.
#
# Please test this and let me know if it's bad.
#
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.26  2003/09/01 19:46:03  dischi
# add menuw to eventhandler, it may be needed
#
# Revision 1.25  2003/08/23 12:51:43  dischi
# removed some old CVS log messages
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
import os
import time

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# Various utilities
import util

# The OSD class
import osd

# The menu widget class
import menu

# The RemoteControl class, sets up a UDP daemon that the remote control client
# sends commands to
import rc

# The TV application
import tv

# Recording daemon
import record_daemon

# Schedule editor
#import record_schedule

import event as em

from gui.PopupBox import PopupBox

# Set to 1 for debug output
DEBUG = config.DEBUG

TRUE = 1
FALSE = 0

# Create the OSD object
osd = osd.get_singleton()

menuwidget = menu.get_singleton()


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

start_times = map(lambda t: time.strftime('%H:%M', time.gmtime(t)), range(0, 86400, 600))
recinfo.start_time = Setting('Start', start_times, None, 'Start time %s')

recinfo.length = Setting('Length', [1, 10, 30, 60, 90, 120, 150, 180, 210,
                                    240, 270, 300, 360, 420, 480, 540, 600, 660, 720],
                         30, 'Length %s minutes')

recinfo.quality = Setting('Quality', ['low', 'medium', 'high'], 'high')



def main_menu(prog):
    recinfo.channel = prog.channel_id
   
    if prog.sub_title:
        prog.title = prog.title + ' - '  + prog.sub_title

    recinfo.program_name = Setting('Program name', [prog.title, '[Timestamp]'],
                         None, 'Program name: %s')
    
    length_minutes = (prog.stop - prog.start) / 60.0
    if (length_minutes - int(length_minutes)) > 0.01:
        recinfo.length.set_selected(int(length_minutes)+1)
    else:
        recinfo.length.set_selected(int(length_minutes))

    prog_time = time.strftime('%H:%M', time.localtime(prog.start))
    recinfo.start_time.set_selected(prog_time)
    
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

    rc.app(eventhandler)

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

    setting.set_selected(selected)
    
    menuw.back_one_menu()


def progname2filename(progname):
    '''Translate a program name to something that can be used as a filename.'''

    # Letters that can be used in the filename
    ok = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

    s = ''
    for letter in progname:
        if letter in ok:
            s += letter
        else:
            if s and s[-1] != '_':
                s += '_'

    return s


def set_schedule(arg=None, menuw=None):
    '''Use the information in the module global variable recinfo to
    schedule a recording through the recording daemon (it might be started by
    this function if it should start immediately).'''

    tunerid = tv.get_tunerid(recinfo.channel)
    tunername = tv.get_friendly_channel(recinfo.channel)

    # Start timestamp
    ts = recinfo.start_date.selected + ' ' + recinfo.start_time.selected
    start_time_s = time.mktime(time.strptime(ts, '%Y-%m-%d %H:%M'))
 
    # Length in seconds
    len_secs = int(recinfo.length.selected) * 60
    len_secs = len_secs-10

    # Recording filename
    rec_name = recinfo.program_name.selected
    start_time_f = start_time_s
    if (time.localtime()[8]==1) and (float(sys.version[0:3]) < 2.3):
            start_time_f = start_time_f - 3600

    ts_ch = time.strftime('%m-%d_%I:%M_-', time.localtime(start_time_f))
    if rec_name != recinfo.program_name.choices[0]:
        rec_name = ts_ch
    else:
        rec_name = ts_ch + '_' + progname2filename(rec_name)
    rec_name = os.path.join(config.DIR_RECORD, rec_name)

    # Calculate timecode for mp1e and similar encoders
    hour = int(len_secs/3600)
    minu = int(len_secs/60)
    seco = int(len_secs%60)
    timecode_format = '%0.2i:%0.2i:%0.2i' % (hour,minu,seco)

    # Flexible command-line options
    cl_options = { 'channel'  : tunerid,
                   'filename' : rec_name,
                   'seconds'  : len_secs,
                   'timecode' : timecode_format }


    # Build the commandline. The -frames option is added later by the daemon.
    sch_cmd = config.VCR_CMD % cl_options
    
    record_daemon.schedule_recording(start_time_s, len_secs, sch_cmd, recinfo.channel)


    s = 'Scheduled recording:\n'
    s += 'Channel %s\n' % tunername
    s += '%s %s %s min' % (recinfo.start_date.selected, recinfo.start_time.selected,
                           recinfo.length.selected)

    pop = PopupBox(text=s)
    pop.show()
    time.sleep(2)
    pop.destroy()


def eventhandler(event, menuw=None):
    if event == em.MENU_BACK_ONE_MENU or event == em.MENU_GOTO_MAINMENU:
        menu.MenuWidget.eventhandler( menuwidget, event )
        rc.app(None) #give control back to the main program
    else:
        menu.MenuWidget.eventhandler( menuwidget, event )
