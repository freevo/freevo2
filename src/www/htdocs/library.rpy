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
# Revision 1.27  2004/07/03 00:41:08  mikeruelle
# fix recording highlighting to match new function output
#
# Revision 1.26  2004/06/09 01:53:09  rshortt
# Small cleanup.
#
# Revision 1.25  2004/06/09 01:46:30  rshortt
# Finally add confirm delete.
#
# Revision 1.24  2004/05/15 02:08:34  mikeruelle
# yet another unicode fix
#
# Revision 1.23  2004/03/21 23:45:56  mikeruelle
# remove non dir items from the list of dirs gets rid of webradio oddity
#
# Revision 1.22  2004/03/21 23:40:00  mikeruelle
# unicode breaks several key test rework the interface to cope.
#
# Revision 1.21  2004/02/23 08:33:21  gsbarbieri
# i18n: help translators job.
#
# Revision 1.20  2004/02/19 04:57:59  gsbarbieri
# Support Web Interface i18n.
# To use this, I need to get the gettext() translations in unicode, so some changes are required to files that use "print _('string')", need to make them "print String(_('string'))".
#
# Revision 1.19  2004/02/09 21:23:42  outlyer
# New web interface...
#
# * Removed as much of the embedded design as possible, 99% is in CSS now
# * Converted most tags to XHTML 1.0 standard
# * Changed layout tables into CSS; content tables are still there
# * Respect the user configuration on time display
# * Added lots of "placeholder" tags so the design can be altered pretty
#   substantially without touching the code. (This means using
#   span/div/etc. where possible and using 'display: none' if it's not in
#   _my_ design, but might be used by someone else.
# * Converted graphical arrows into HTML arrows
# * Many minor cosmetic changes
#
# Revision 1.18  2004/01/26 19:16:13  mikeruelle
# this does not seem to work anymore with twisted 1.1.0
#
# Revision 1.17  2003/11/28 20:08:59  dischi
# renamed some config variables
#
# Revision 1.16  2003/11/28 19:31:52  dischi
# renamed some config variables
#
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
# fixing an error that appends items to VIDEO_ITEMS when downloading an item
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
# config.TV_RECORD_DIR and let you rename or delete them.
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
            suffixes.extend(config.AUDIO_SUFFIX)
            suffixes.extend(config.PLAYLIST_SUFFIX)
        if media == 'images':
            suffixes.extend(config.IMAGE_SUFFIX)
        if media == 'movies':
            suffixes.extend(config.VIDEO_SUFFIX)
        if media == 'rectv':
            suffixes.extend(config.VIDEO_SUFFIX)
        return suffixes

    def get_dirlist(self, media):
        dirs = []
        dirs2 = []

        if media == 'movies':
            dirs2.extend(config.VIDEO_ITEMS)
        elif media == 'music':
            dirs2.extend(config.AUDIO_ITEMS)
        elif media == 'rectv':
            dirs2 = [ ('Recorded TV', config.TV_RECORD_DIR) ]
        elif media == 'images':
            dirs2.extend(config.IMAGE_ITEMS)
        elif media == 'download':
            dirs2.extend(config.VIDEO_ITEMS)
            dirs2.extend(config.AUDIO_ITEMS)
            dirs2.extend( [ ('Recorded TV', config.TV_RECORD_DIR) ])
            dirs2.extend(config.IMAGE_ITEMS)
        #strip out ssr and fxd files
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
        messages = []
        form = request.args

        action           = fv.formValue(form, 'action')
        action_file      = Unicode(fv.formValue(form, 'file'))
        if isinstance( action_file, str ):
            action_file = Unicode( action_file, 'latin-1' )
            
        action_newfile   = Unicode(fv.formValue(form, 'newfile'))
        if isinstance( action_newfile, str ):
            action_newfile = Unicode( action_newfile, 'latin-1' )
            
        action_dir       = Unicode(fv.formValue(form, 'dir'))
        if isinstance( action_dir, str ):
            action_dir = Unicode( action_dir, 'latin-1' )
            
        action_mediatype = fv.formValue(form, 'media')
        action_script = os.path.basename(request.path)        
        #use request.postpath array to set action to download
        if not action and len(request.postpath) > 0:
            action = "download"
            action_file = Unicode(request.postpath[-1])
            action_dir = Unicode(os.sep + string.join(request.postpath[0:-1], os.sep))
            action_mediatype = "download"
        elif not action:
            action = "view"


        #check to make sure no bad chars in action_file
        fs_result = 0
        bs_result = 0
        if len(action_file):
            fs_result = string.find(action_file, '/')
            bs_result = string.find(action_file, '\\')

        #do actions here
        if not action == 'view' and bs_result == -1 and fs_result == -1:
            file_loc = os.path.join(action_dir, action_file)
            if os.path.isfile(file_loc):
                if action == 'rename':
                    if action_newfile:
                        newfile_loc = os.path.join(action_dir, action_newfile)
                        if os.path.isfile(newfile_loc):
                            messages += [ _( '%s already exists! File not renamed.' ) % ('<b>'+newfile_loc+'</b>') ]
                        else:
                            messages += [ _( 'Rename %s to %s.' ) % ('<b>'+file_loc+'</b>', '<b>'+newfile_loc+'</b>') ]
                            os.rename(file_loc, newfile_loc)
                    else:
                        messages += [ '<b>'+_('ERROR') + '</b>: ' +_('No new file specified.') ]

                elif action == 'delete':
                    messages += [ _( 'Delete %s.' ) % ('<b>'+file_loc+'</b>') ]
                    if os.path.exists(file_loc): os.unlink(file_loc)
                    file_loc_fxd = os.path.splitext(file_loc)[0] + '.fxd'
                    if os.path.exists(file_loc_fxd): 
                        os.unlink(file_loc_fxd)
                        messages += [ _('Delete %s.') % ('<b>'+file_loc_fxd+'</b>') ]

                elif action == 'download':
                    sys.stderr.write('download %s\n' % String(file_loc))
                    sys.stderr.flush()
                    return static.File(file_loc).render(request)
                    #request.finish()

            else:
                messages += [ '<b>'+_('ERROR') + '</b>: ' + _( '%s does not exist. No action taken.') % ('<b>'+file_loc+'</b>') ]
        elif action_file and action != 'view':
            messages += [ '<b>'+_('ERROR')+'</b>: ' +_( 'I do not process names (%s) with slashes for security reasons.') % action_file ]

        directories = []
        if action_mediatype:
            directories = self.get_dirlist(action_mediatype)


        if action and action != "download":
            fv.printHeader(_('Media Library'), 'styles/main.css', selected=_("Media Library"))
            fv.res += '<script language="JavaScript"><!--' + "\n"

            fv.res += 'function deleteFile(basedir, file, mediatype) {' + "\n"
            fv.res += '   okdelete=window.confirm("Do you wish to delete "+file+" and its fxd?");' + "\n"
            fv.res += '   if(!okdelete) return;' + "\n"
            fv.res += '   document.location="' + action_script +'?action=delete&file=" + escape(file) + "&dir=" + basedir + "&media=" + mediatype;' + "\n"
            fv.res += '}' + "\n"

            fv.res += 'function renameFile(basedir, file, mediatype) {' + "\n"
            fv.res += '   newfile=window.prompt("New name please.", file);' + "\n"
            fv.res += '   if(newfile == "" || newfile == null) return;' + "\n"
            fv.res += '   document.location="' + action_script +'?action=rename&file=" + escape(file) + "&newfile=" + escape(newfile) + "&dir=" + basedir + "&media=" + mediatype;' + "\n"
            fv.res += '}' + "\n"

            fv.res += '//--></script>' + "\n"
            fv.res += '&nbsp;<br/>\n'

            if messages:
                fv.res += "<h4>"+_("Messages")+":</h4>\n"
                fv.res += "<ul>\n"
                for m in messages:
                    fv.res += "   <li>%s</li>\n" % m
                fv.res += "</ul>\n"
                

        if not action_mediatype:
            fv.tableOpen('class="library"')
            movmuslink = '<a href="%s?media=%s&dir=">%s</a>' 
            rectvlink = '<a href="%s?media=%s&dir=%s">%s</a>' 
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<img src=\"images/library/library-movies.jpg\">')
            fv.tableCell(movmuslink % (action_script, "movies",_("Movies")), '')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<img src=\"images/library/library-tv.jpg\">')
            fv.tableCell(rectvlink % (action_script, "rectv", config.TV_RECORD_DIR, _("Recorded TV")), '')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<img src=\"images/library/library-music.jpg\">')
            fv.tableCell(movmuslink % (action_script,"music",_("Music")), '')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<img src=\"images/library/library-images.jpg\">')
            fv.tableCell(movmuslink % (action_script,"images",_("Images")), '')
            fv.tableRowClose()
            fv.tableClose()
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
        elif action_mediatype and len(action_dir) == 0:
            # show the appropriate dirs from config variables
            # make a back to pick music or movies
            # now make the list unique
            fv.tableOpen('class="library"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(_('Choose a Directory'), 'class="guidehead" colspan="1"')
            fv.tableRowClose()
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('<a href="' + action_script + '">&laquo; '+_('Back')+'</a>', 'class="basic" colspan="1"')
            fv.tableRowClose()
            for d in directories:
                (title, dir) = d
                link = '<a href="' + action_script +'?media='+action_mediatype+'&dir='+urllib.quote(dir)+'">'+title+'</a>'
                fv.tableRowOpen('class="chanrow"')
                fv.tableCell(link, 'class="basic" colspan="1"')
                fv.tableRowClose()
            fv.tableClose()
            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()
        elif action_mediatype and len(action_dir) and action != "download":
            if not self.check_dir(action_mediatype,action_dir) and action != 'view':
                sys.exit(1)

            fv.tableOpen('class="library"')
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell('Name', 'class="guidehead" colspan="1"')
            fv.tableCell('Size', 'class="guidehead" colspan="1"')
            fv.tableCell('Actions', 'class="guidehead" colspan="1"')
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
                                recordingprogram = os.path.basename(tv_util.getProgFilename(prog))
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
                backlink = '<a href="'+ action_script +'">&laquo; '+_('Back')+'</a>'
            elif actiondir_is_root == TRUE:
                backlink = '<a href="'+ action_script +'?media='+action_mediatype+'&dir=">&laquo; '+_('Back')+'</a>'
            else:
                backdir = os.path.dirname(action_dir)
                backlink = '<a href="'+ action_script +'?media='+action_mediatype+'&dir='+urllib.quote(backdir)+'">&laquo; '+_('Back')+'</a>'
            fv.tableRowOpen('class="chanrow"')
            fv.tableCell(backlink, 'class="basic" colspan="1"')
            fv.tableCell('&nbsp;', 'class="basic" colspan="1"')
            fv.tableCell('&nbsp;', 'class="basic" colspan="1"')
            fv.tableRowClose()

            # get me the directories to output
            directorylist = util.getdirnames(String(action_dir))
            for mydir in directorylist:
                mydir = Unicode(mydir)
                fv.tableRowOpen('class="chanrow"')
                mydispdir = os.path.basename(mydir)
                mydirlink = '<a href="'+ action_script +'?media='+action_mediatype+'&dir='+urllib.quote(mydir)+'">'+mydispdir+'</a>'
                fv.tableCell(mydirlink, 'class="basic" colspan="1"')
                fv.tableCell('&nbsp;', 'class="basic" colspan="1"')
                fv.tableCell('&nbsp;', 'class="basic" colspan="1"')
                fv.tableRowClose()

            suffixes = self.get_suffixes(action_mediatype)

            # loop over directory here
            items = util.match_files(String(action_dir), suffixes)
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
                fv.tableCell(Unicode(file), 'class="'+status+'" colspan="1"')
                fv.tableCell(tv_util.descfsize(len_file), 'class="'+status+'" colspan="1"')
                if suppressaction == TRUE:
                    fv.tableCell('&nbsp;', 'class="'+status+'" colspan="1"')
                else:
                    file_esc = urllib.quote(String(file))
                    dllink = ('<a href="'+action_script+'%s">'+_('Download')+'</a>') %  Unicode(os.path.join(basedir,file))
                    delete = ('<a href="javascript:deleteFile(\'%s\',\'%s\',\'%s\')">'+_("Delete")+'</a>') % (basedir, file_esc, action_mediatype)
                    rename = ('<a href="javascript:renameFile(\'%s\',\'%s\',\'%s\')">'+_("Rename")+'</a>') % (basedir, file_esc, action_mediatype)
                    fv.tableCell(rename + '&nbsp;&nbsp;' + delete + '&nbsp;&nbsp;' + dllink, 'class="'+status+'" colspan="1"')
                fv.tableRowClose()

            fv.tableClose()

            fv.printSearchForm()
            fv.printLinks()
            fv.printFooter()

        return String( fv.res )
    
resource = LibraryResource()

