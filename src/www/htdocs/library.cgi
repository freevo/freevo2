#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# library.cgi - a script to display and modify your video library
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#   figure a way to know whether DIR_RECORD has a trailing slash and only
#     add if required when replacing.
#   human readable size rather than bytes from os
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/02/20 22:12:26  rshortt
# Added a check in case the user doesn't input anything or clicks cancel.
#
# Revision 1.1  2003/02/20 21:48:13  rshortt
# New cgi contributed by Mike Ruelle.  This lets you view files inside
# config.DIR_RECORD and let you rename or delete them.
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

import sys, cgi, os, string, urllib
import html_util as fv

so = sys.stdout
sys.stdout = sys.stderr

# needed to put these here to suppress its output
import config
import util

TRUE = 1
FALSE = 0

form = cgi.FieldStorage()

action = fv.formValue(form, 'action')
action_file = fv.formValue(form, 'file')
action_newfile = fv.formValue(form, 'newfile')

#check to make sure no bad chars in action_file
fs_result = 0
bs_result = 0
if action_file:
    fs_result = string.find(action_file, '/')
    bs_result = string.find(action_file, '\\')

#do actions here
if bs_result == -1 and fs_result == -1:
    file_loc = os.path.join(config.DIR_RECORD, action_file)
    if os.path.isfile(file_loc):
        if action == 'rename':
            newfile_loc = os.path.join(config.DIR_RECORD, action_newfile)
            if os.path.isfile(newfile_loc):
                print '%s already exists file not renamed.' % newfile_loc
            else:
                print 'rename %s to %s' % (file_loc, newfile_loc)
                os.rename(file_loc, newfile_loc)
        elif action == 'delete':
            print 'delete %s' % file_loc
            os.unlink(file_loc)
    else:
        print '%s does not exist. no action taken.' % file_loc
else:
    print 'I do not process names(%s) with slashes for security reasons.' % action_file

# ok let's write the page
sys.stdout = so

fv.printContentType()
fv.printHeader('Video Library', 'styles/main.css')

print '<script language="JavaScript"><!--'
print 'function renameFile(file) {'
print '   newfile=window.prompt("New name please.");'
print '   if(newfile == "" || newfile == null) return;'
print '   document.location="library.cgi?action=rename&file=" + escape(file) + "&newfile=" + escape(newfile);'
print '}'
print '//--></script>'

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('<img src="images/logo_200x100.png">', 'align=left')
fv.tableCell('Video Library', 'class="heading" align="left"')
fv.tableRowClose()
fv.tableClose()

fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="100%"')
fv.tableRowOpen('class="chanrow"')
fv.tableCell('Name', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Size', 'class="guidehead" align="center" colspan="1"')
fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
fv.tableRowClose()

# loop over directory here
items = util.match_files(config.DIR_RECORD, config.SUFFIX_VIDEO_FILES)
for file in items:
    #find size
    len_file = os.stat(file)[6]
    #chop dir from in front of file
    file = string.replace(file, config.DIR_RECORD + '/', '')
    fv.tableRowOpen('class="chanrow"')
    fv.tableCell(file, 'class="basic" align="left" colspan="1"')
    fv.tableCell(str(len_file), 'class="basic" align="left" colspan="1"')
    file_esc = urllib.quote(file)
    rename = '<a href="javascript:renameFile(\'%s\')">Rename</a>' % file_esc
    delete = '<a href="library.cgi?action=delete&file=%s">Delete</a>' % file_esc
    fv.tableCell(rename + '&nbsp;&nbsp;' + delete, 'class="basic" align="center" colspan="1"')
    fv.tableRowClose()

fv.tableClose()

fv.printSearchForm()

fv.printLinks()

fv.printFooter()
