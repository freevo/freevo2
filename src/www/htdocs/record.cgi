#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# record.cgi - Web interface to your scheduled recordings.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/02/11 06:40:57  krister
# Applied Robs patch for std fileheaders.
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

import sys, cgi, time
import html_util as fv

so = sys.stdout
sys.stdout = sys.stderr

import rec_interface as ri
import rec_favorites as rf

TRUE = 1
FALSE = 0

form = cgi.FieldStorage()

chan = fv.formValue(form, 'chan')
start = fv.formValue(form, 'start')
action = fv.formValue(form, 'action')

prog = ri.findProg(chan, start)

if prog:
    print 'PROG: %s' % prog

if prog:
    if action == 'remove':
       print 'want to remove prog: %s' % prog
       ri.removeScheduledRecording(prog)
    else:
       ri.scheduleRecording(prog)

recordings = ri.getScheduledRecordings()
progs = recordings.getProgramList()
favs = rf.getFavorites()

sys.stdout = so

fv.printContentType()
fv.printHeader('Scheduled Recordings', 'styles/main.css')

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('<img src="images/logo_200x100.png">', 'align=left')
fv.tableCell('Scheduled Recordings', 'class="heading" align="left"')
fv.tableRowClose()
fv.tableClose()

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('Start Time', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Stop Time', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Channel', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Title', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Program Description', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
fv.tableRowClose()

f = lambda a, b: cmp(a.start, b.start)
progl = progs.values()
progl.sort(f)
for prog in progl:
    status = 'basic'

    if rf.isProgAFavorite(prog, favs):
        status = 'favorite'
    try:
        if prog.isRecording == TRUE:
            status = 'recording'
    except:
        # sorry, have to pass without doing anything.
        pass

    fv.tableRowOpen('class="chanrow"')
    fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.start)), 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(time.strftime('%b %d %H:%M', time.localtime(prog.stop)), 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(prog.channel_id, 'class="'+status+'" align="left" colspan="1"')
    fv.tableCell(prog.title, 'class="'+status+'" align="left" colspan="1"')

    if prog.desc == '':
        cell = 'Sorry, the program description for "%s" is unavailable.' % prog.title
    else:
        cell = prog.desc
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    cell = '<a href="record.cgi?chan=%s&start=%s&action=remove">Remove</a>' % (prog.channel_id, prog.start)
    fv.tableCell(cell, 'class="'+status+'" align="left" colspan="1"')

    fv.tableRowClose()

fv.tableClose()

fv.printSearchForm()

fv.printLinks()

fv.printFooter()
