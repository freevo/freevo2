#!/usr/bin/python

#if 0 /*
# -----------------------------------------------------------------------
# library.rpy - a script to display and modify your video library
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo: -allow for an imdb popup
#       -stream tv, video and music somehow
# -----------------------------------------------------------------------
# $Log$
# Revision 1.15  2003/10/20 02:24:17  rshortt
# more tv_util fixes
#
# Revision 1.14  2003/09/05 15:23:02  mikeruelle
# fearless leader missed a import change
#
# Revision 1.13  2003/09/05 02:48:13  rshortt
# Removing src/tv and src/www from PYTHONPATH in the freevo script.  Therefore any module that was imported from src/tv/ or src/www that didn't have a leading 'tv.' or 'www.' needed it added.  Also moved tv/tv.py to tv/tvmenu.py to avoid namespace conflicts.
#
# Revision 1.12  2003/08/23 19:21:29  mikeruelle
# fixing an error that appends items to DIR_MOVIES when downloading an item
#
# Revision 1.11  2003/07/24 11:55:38  rshortt
# Removed the menu images for now because they are missing and I am not even
# sure they look all that great (when there).
#
# Revision 1.10  2003/07/24 00:09:02  rshortt
# Bugfix.
#
# Revision 1.9  2003/07/14 19:30:37  rshortt
# Library update from Mike Ruelle.  Now you can view other media types and
# download as well.
#
# Revision 1.8  2003/07/07 03:20:22  rshortt
# Make the favorites match use the newer file naming scheme (s/ /_/g).
#
# Revision 1.7  2003/07/01 21:47:35  outlyer
# Made a check to see if file exists before unlinking.
#
# Revision 1.6  2003/05/22 21:33:23  outlyer
# Lots of cosmetic changes:
#
# o Moved the header/logo into web_types
# o Made the error messages all use <h4> instead of <h2> so they look the same
# o Removed most <hr> tags since they don't really mesh well with the light blue
# o Moved the title into the "status bar" under the logo
#
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
import config, util
import util.tv_util as tv_util
import tv.record_client as ri

from www.web_types import HTMLResource, FreevoResource
from twisted.web import static

TRUE = 1
FALSE = 0


class LibraryResource(FreevoResource):
    isLeaf=1
    def get_suffixes (self, media):
        suffixes = []
        if media == 'music':
            suffixes.extend(config.SUFFIX_AUDIO_FILES)
            suffixes.extend(config.SUFFIX_AUDIO_PLAYLISTS)
        if media == 'images':
            suffixes.extend(config.SUFFIX_IMAGE_FILES)
        if media == 'movies':
            suffixes.extend(config.SUFFIX_VIDEO_FILES)
        if media == 'rectv':
            suffixes.extend(config.SUFFIX_VIDEO_FILES)
        return suffixes

    def get_dirlist(self, media):
        dirs = []
        dirs2 = []

        if media == 'movies':
            dirs.extend(config.DIR_MOVIES)
        elif media == 'music':
            dirs.extend(config.DIR_AUDIO)
        elif media == 'rectv':
            dirs = [ ('Recorded TV', config.DIR_RECORD) ]
        elif media == 'images':
            dirs2.extend(config.DIR_IMAGES)
            #strip out ssr files
            for d in dirs2:
                (title, tdir) = d
                if os.path.isdir(tdir):
                    dirs.append(d)
        elif media == 'download':
            dirs.extend(config.DIR_MOVIES)
            dirs.extend(config.DIR_AUDIO)
            dirs.extend( [ ('Recorded TV', config.DIR_RECORD) ])
            dirs2.extend(config.DIR_IMAGES)
            #strip out ssr files
            for d in dirs2:
                (title, tdir) = d
                if os.path.isdir(tdir):
                    dirs.append(d)            
        return dirs

    def check_dir(self, media, dir):
        dirs2 = []
        dirs2 = self.get_dirlist(media)
        for d in dirs2:
            (title, tdir) = d
            if re.match(tdir, dir):
                return TRUE
        return FALSE

    def _render(self, request):
        fv = HTMLResource()
        form = request.args

        action = fv.formValue(form, 'action')
        action_file = fv.formValue(form, 'file')
        action_newfile = fv.formValue(form, 'newfile')
        action_dir = fv.formValue(form, 'dir')
        action_mediatype = fv.formValue(form, 'media')
        action_script = os.path.basename(request.path)
        #use request.postpath array to set action to download
        if not action and len(request.postpath) > 0:
            action = "download"
            action_file = request.postpath[-1]
            action_dir = os.sep + string.join(request.postpath[0:-1], os.sep)
            action_mediatype = "download"
        elif not action:
            action = "view"


        #check to make sure no bad chars in action_file
        fs_result = 0
        bs_result = 0
        if action_file:
            fs_result = string.find(action_file, '/')
            bs_result = string.find(action_file, '\\')

        #do actions here
        if bs_result == -1 and fs_result == -1:
            file_loc = os.path.join(action_dir, action_file)
            if os.path.isfile(file_loc):
                if action == 'rename':
                    if action_newfile:
                        newfile_loc = os.path.join(action_dir, action_newfile)
                        if os.path.isfile(newfile_loc):
                            print '%s already exists file not renamed.' % newfile_loc
                        else:
                            print 'rename %s to %s' % (file_loc, newfile_loc)
                            os.rename(file_loc, newfile_loc)
                    else:
                        fv.res += 'Error: no newfile specified.'
                elif action == 'delete':
                    print 'delete %s' % file_loc
                    if os.path.exists(file_loc): os.unlink(file_loc)
                elif action == 'download':
                    sys.stderr.write('download %s' % file_loc)
                    sys.stderr.flush()
                    static.File(file_loc).render(request)
                    request.finish()
            else:
                fv.res += '%s does not exist. no action taken.' % file_loc
        else:
            print 'I do not process names(%s) with slashes for security reasons.' % action_file

        directories = []
        if action_mediatype:
            directories = self.get_dirlist(action_mediatype)


        if action and action != "download":
            fv.printHeader('Media Library', 'styles/main.css')
            fv.res += '<script language="JavaScript"><!--' + "\n"
            fv.res += 'function renameFile(basedir, file, mediatype) {' + "\n"
            fv.res += '   newfile=window.prompt("New name please.");' + "\n"
            fv.res += '   if(newfile == "" || newfile == null) return;' + "\n"
            fv.res += '   document.location="' + action_script +'?action=rename&file=" + escape(file) + "&newfile=" + escape(newfile) + "&dir=" + basedir + "&media=" + mediatype;' + "\n"
            fv.res += '}' + "\n"
            fv.res += '//--></script>' + "\n"

        if not action_mediatype:
            fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="85%"')
            fv.tableRowOpen('class="chanrow"')
            movmuslink = '<a href="%s?media=%s">%s</a>' 
            rectvlink = '<a href="%s?media=%s&dir=%s">%s</a>' 
            fv.tableCell(movmuslink % (action_script, "movies","Movies"), 'align=center')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(rectvlink % (action_script, "rectv", config.DIR_RECORD, "Recorded TV"), 'align=center')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(movmuslink % (action_script,"music","Music"), 'align=center')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(movmuslink % (action_script,"images","Images"), 'align=center')
            fv.tableRowClose()
            fv.tableClose()
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
        elif action_mediatype and not action_dir:
            # show the appropriate dirs from config variables
            # make a back to pick music or movies
            # now make the list unique
            fv.tableOpen('border=0 cellpadding=4 cellspacing=1 width="85%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Choose a Directory', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<a href="' + action_script + '">Back</a>', 'class="basic" align="left" colspan="1"')
            fv.tableRowClose()
            for d in directories:
                (title, dir) = d
                link = '<a href="' + action_script +'?media='+action_mediatype+'&dir='+urllib.quote(dir)+'">'+title+'</a>'
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" align="left" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
        elif action_mediatype and action_dir and not action == "download":
            if not self.check_dir(action_mediatype,action_dir):
                sys.exit(1)

            fv.tableOpen('border="0" cellpadding="4" cellspacing="1" width="100%"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Name', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Size', 'class="guidehead" align="center" colspan="1"')
            fv.tableCell('Actions', 'class="guidehead" align="center" colspan="1"')
            fv.tableRowClose()

            # find out if anything is recording
            recordingprogram = ''
            favre = ''
            favs = []
            if action_mediatype == 'movies' or action_mediatype == 'rectv':
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
                                recordingprogram = string.replace(recordingprogram, ' ', '_')
                                break
                        except:
                            # sorry, have to pass without doing anything.
                            pass
                else:
                    fv.res += '<h4>The recording server is down, recording information is unavailable.</h4>'
            

                #generate our favorites regular expression
                favre = ''
                (result, favorites) = ri.getFavorites()
                if result:
                    favs = favorites.values()
                else:
                    favs = []

                if favs:
                    favtitles = [ fav.title for fav in favs ]
                    # no I am not a packers fan
                    favre = string.join(favtitles, '|') 
                    favre = string.replace(favre, ' ', '_')

            #put in back up directory link
            #figure out if action_dir is in directories variable and change 
            #back if it is
            actiondir_is_root = FALSE
            for d in directories:
                (title, dir) = d
                if dir == action_dir:
                    actiondir_is_root = TRUE
                    break
            backlink = ''
            if actiondir_is_root == TRUE and action_mediatype == 'rectv':
                backlink = '<a href="'+ action_script +'">Back</a>'
            elif actiondir_is_root == TRUE:
                backlink = '<a href="'+ action_script +'?media='+action_mediatype+'">Back</a>'
            else:
                backdir = os.path.dirname(action_dir)
                backlink = '<a href="'+ action_script +'?media='+action_mediatype+'&dir='+urllib.quote(backdir)+'">Back</a>'
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(backlink, 'class="basic" align="left" colspan="1"')
            fv.tableCell('&nbsp;', 'class="basic" align="center" colspan="1"')
            fv.tableCell('&nbsp;', 'class="basic" align="center" colspan="1"')
            fv.tableRowClose()

            # get me the directories to output
            directorylist = util.getdirnames(action_dir)
            for mydir in directorylist:
                fv.tableRowOpen('class="chanrow"')
                mydispdir = os.path.basename(mydir)
                mydirlink = '<a href="'+ action_script +'?media='+action_mediatype+'&dir='+urllib.quote(mydir)+'">'+mydispdir+'</a>'
                fv.tableCell(mydirlink, 'class="basic" align="left" colspan="1"')
                fv.tableCell('&nbsp;', 'class="basic" align="center" colspan="1"')
                fv.tableCell('&nbsp;', 'class="basic" align="center" colspan="1"')
                fv.tableRowClose()

            suffixes = self.get_suffixes(action_mediatype)

            # loop over directory here
            items = util.match_files(action_dir, suffixes)
            for file in items:
                status = 'basic'
                suppressaction = FALSE
                #find size
                len_file = os.stat(file)[6]
                #chop dir from in front of file
                (basedir, file) = os.path.split(file)
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
                    dllink = '<a href="'+action_script+'%s">Download</a>' %  os.path.join(basedir,file)
                    filelink = '<a href="'+action_script+'?media=%s&dir=%s&action=%s&file=%s">%s</a>'
                    delete = filelink % (action_mediatype, basedir, 'delete', file_esc,'Delete')
                    rename = '<a href="javascript:renameFile(\'%s\',\'%s\',\'%s\')">Rename</a>' % (basedir, file_esc, action_mediatype)
                    fv.tableCell(rename + '&nbsp;&nbsp;' + delete + '&nbsp;&nbsp;' + dllink, 'class="'+status+'" align="center" colspan="1"')
                fv.tableRowClose()

            fv.tableClose()

            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

        return fv.res
    
resource = LibraryResource()

