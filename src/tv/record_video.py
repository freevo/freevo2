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
# Revision 1.19  2003/06/29 15:01:31  outlyer
# Display the channel's friendly (display name) in the tuner popupbox.
#
# Since XMLTV 0.6.11 uses what they call "RFC" channel names which are
# very long and don't reveal much about the channel.
#
# This will obviously have no regressive effect, since users had the
# friendly name before.
#
# Revision 1.18  2003/06/24 21:08:41  outlyer
# Use the episode title if available in the recording filename.
#
# Revision 1.17  2003/06/02 21:29:22  outlyer
# Changed the "Schedule Editor" to show up in the TV Submenu, along with "Guide" and
# "Recorded Shows" which makes a lot more sense then where it was before, which was
# also exceptionally well hidden.
#
# To do this properly, I also had to move record_schedule into a class, subclassing
# from Item, and so problems may and possibly will arise. I've tested it a little,
# but please bang on this, because while it's a relatively minor change, it does
# get things working inside the properly model, at least for a start.
#
# Bug reports are expected and welcome :)
#
# Revision 1.16  2003/05/31 20:53:03  outlyer
# Fix what I hope is the last event-related crash. Choosing shows to record
# works again.
#
# Revision 1.15  2003/05/27 17:53:35  dischi
# Added new event handler module
#
# Revision 1.14  2003/05/05 01:19:49  outlyer
# An attempt to fix the daylight savings issue; it makes one potentially bad
# assumption, that daylight savings time is one hour rather than more.
#
# Revision 1.13  2003/04/24 19:56:41  dischi
# comment cleanup for 1.3.2-pre4
#
# Revision 1.12  2003/04/20 12:43:34  dischi
# make the rc events global in rc.py to avoid get_singleton. There is now
# a function app() to get/set the app. Also the events should be passed to
# the daemon plugins when there is no handler for them before. Please test
# it, especialy the mixer functions.
#
# Revision 1.10  2003/03/15 05:01:31  outlyer
# Merged Kyle Weston's Schedule Viewer/Editor patch.
#
# Please note, it currently only works with recording files ending in '.avi'
# This is temporary, but as a fix, there is a commented line on line 171,
# if you use mpgs (like I do) you can enable line 171 and comment out line 170.
#
# Since avi is the default, I'm leaving it that way, but I will use mpg myself.
#
# Revision 1.9  2003/03/07 17:13:34  outlyer
# A bunch of internal changes that should be completely invisible to most
# people. Mainly, the scheduling routine is now a little more configurable.
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

    print 'REC: set_sel %s, %s' % (setting.name, selected)

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

    # Recording filename
    rec_name = recinfo.program_name.selected
    start_time_f = start_time_s
    if (time.localtime()[8]==1):
            start_time_f = start_time_f - 3600

    ts_ch = time.strftime('%m-%d_%I:%M_-', time.localtime(start_time_f))
    if rec_name != recinfo.program_name.choices[0]:
        rec_name = ts_ch
    else:
        rec_name = ts_ch + '_' + progname2filename(rec_name)
    rec_name = os.path.join(config.DIR_RECORD, rec_name)

    # Calculate timecode for mp1e and similar encoders
    temp = len_secs - 1
    hour = int(temp/3600)
    minu = int(temp/60)
    seco = int(temp%60)
    timecode_format = '%0.2i:%0.2i:%0.2i' % (hour,minu,seco)

    # Flexible command-line options
    cl_options = { 'channel'  : tunerid,
                   'filename' : rec_name,
                   'seconds'  : len_secs,
                   'timecode' : timecode_format }


    # Build the commandline. The -frames option is added later by the daemon.
    sch_cmd = config.VCR_CMD % cl_options
    print 'SCHEDULE: %s, %s, %s' % (tunerid, time.ctime(start_time_f), rec_name)
    print 'SCHEDULE: %s' % sch_cmd
    
    record_daemon.schedule_recording(start_time_s, len_secs, sch_cmd, recinfo.channel)


    s = 'Scheduled recording:\n'
    s += 'Channel %s\n' % tunername
    s += '%s %s %s min' % (recinfo.start_date.selected, recinfo.start_time.selected,
                           recinfo.length.selected)
    print '"%s"' % s


    pop = PopupBox(text=s)
    pop.show()
    time.sleep(2)
    pop.destroy()


def eventhandler( event):
    print 'using record_video event handler'
    # XXX Hack, make it better!!!!
    #if event == em.MENU_CHANGE_STYLE:
    #    record_schedule.main_menu()
    if event == em.MENU_BACK_ONE_MENU or event == em.MENU_GOTO_MAINMENU:
        menu.MenuWidget.eventhandler( menuwidget, event )
        rc.app(None) #give control back to the main program
    else:
        menu.MenuWidget.eventhandler( menuwidget, event )
