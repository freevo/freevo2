#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# library.rpy - a script to display and modify your video library
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
# Revision 1.5  2003/05/14 01:11:20  rshortt
# More error handling and notice if the record server is down.
#
# Revision 1.4  2003/05/13 00:29:46  rshortt
# Renaming works again.  It will choke on filenames with single quotes though.
#
# Revision 1.3  2003/05/13 00:18:07  rshortt
# Bugfix, but rename still doesn't work!
#
# Revision 1.2  2003/05/12 23:02:41  rshortt
# Adding HTTP BASIC Authentication.  In order to use you must override WWW_USERS
# in local_conf.py.  This does not work for directories yet.
#
# Revision 1.1  2003/05/11 22:48:21  rshortt
# Replacements for the cgi files to be used with the new webserver.  These
# already use record_client / record_server.
#
# Revision 1.4  2003/02/27 02:04:34  rshortt
# Committed some code by Michael Ruelle which adds highlighting and file
# size descriptions to library.cgi.
#
# Revision 1.3  2003/02/20 22:36:04  rshortt
# Fixed a crash where newfile was null.
#
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

import sys, os, string, urllib, re


# needed to put these here to suppress its output
import config
import util
import tv_util
import record_client as ri

from web_types import HTMLResource, FreevoResource

TRUE = 1
FALSE = 0


class LibraryResource(FreevoResource):

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

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
                    if action_newfile:
                        newfile_loc = os.path.join(config.DIR_RECORD, action_newfile)
                        if os.path.isfile(newfile_loc):
                            print '%s already exists file not renamed.' % newfile_loc
                        else:
                            print 'rename %s to %s' % (file_loc, newfile_loc)
                            os.rename(file_loc, newfile_loc)
                    else:
                        fv.res += 'Error: no newfile specified.'
                elif action == 'delete':
                    print 'delete %s' % file_loc
                    os.unlink(file_loc)
            else:
                fv.res += '%s does not exist. no action taken.' % file_loc
        else:
            print 'I do not process names(%s) with slashes for security reasons.' % action_file

        fv.printHeader('Video Library', 'styles/main.css')

        fv.res += '<script language="JavaScript"><!--\n'
        fv.res += 'function renameFile(file) {\n'
        fv.res += '   newfile=window.prompt("New name please.");\n'
        fv.res += '   if(newfile == "" || newfile == null) return;\n'
        fv.res += '   document.location="library.rpy?action=rename&file=" + escape(file) + "&newfile=" + escape(newfile);\n'
        fv.res += '}\n'
        fv.res += '//--></script>\n'

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('<img src="images/logo_200x100.png" />', 'align=left')
        fv.tableCell('Video Library', 'class="heading" align="left"')
        fv.tableRowClose()
        fv.tableClose()

        fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
        fv.tableRowOpen('class="chanrow"')
        fv.tableCell('Name', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Size', 'class="guidehead" align="center" colspan="1"')
        fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
        fv.tableRowClose()

        # find out if anything is recording
        recordingprogram = ''

        (got_schedule, recordings) = ri.getScheduledRecordings()
        if got_schedule:
            progs = recordings.getProgramList()
            f = lambda a, b: cmp(a.start, b.start)
            progl = progs.values()
            progl.sort(f)
            for prog in progl:
                try:
                    if prog.isRecording == TRUE:
                        recordingprogram = tv_util.getProgFilename(prog)
                        break
                except:
                    # sorry, have to pass without doing anything.
                    pass
        else:
            fv.res += '<hr /><h2>The recording server is down, recording information is unavailable.</h2><hr />'
            

        #generate our favorites regular expression
        favre = ''
        (result, favorites) = ri.getFavorites()
        if result:
            favs = favorites.values()
        else:
            favs = []

        if favs:
            favtitles = [ fav.title for fav in favs ]
            favre = string.join(favtitles, '|') # no I am not a packers fan

        # loop over directory here
        items = util.match_files(config.DIR_RECORD, config.SUFFIX_VIDEO_FILES)
        for file in items:
            status = 'basic'
            suppressaction = FALSE
            #find size
            len_file = os.stat(file)[6]
            #chop dir from in front of file
            file = string.replace(file, config.DIR_RECORD + '/', '')
            if recordingprogram and re.match(recordingprogram, file):
                status = 'recording'
                suppressaction = TRUE
            elif favs and re.match(favre, file):
                status = 'favorite'
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(file, 'class="'+status+'" align="left" colspan="1"')
            fv.tableCell(tv_util.descfsize(len_file), 'class="'+status+'" align="left" colspan="1"')
            if suppressaction == TRUE:
                fv.tableCell('&nbsp;', 'class="'+status+'" align="center" colspan="1"')
            else:
                file_esc = urllib.quote(file)
                rename = '<a href="javascript:renameFile(\'%s\')">Rename</a>' % file_esc
                delete = '<a href="library.rpy?action=delete&file=%s">Delete</a>' % file_esc
                fv.tableCell(rename + '&nbsp;&nbsp;' + delete, 'class="'+status+'" align="center" colspan="1"')
            fv.tableRowClose()

        fv.tableClose()

        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return fv.res
    
resource = LibraryResource()

