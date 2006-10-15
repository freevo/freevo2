# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# freevoscreensaver.py - quick hurry and save the screen!!!
# -----------------------------------------------------------------------
# $Id$
#
# Notes: maybe some day i will make it really start and stop the saver
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.12  2005/08/06 14:50:32  dischi
# adjust to kaa.notifier.Timer.start now using seconds
#
# Revision 1.11  2005/07/22 19:30:24  dischi
# fix event handling
#
# Revision 1.10  2005/07/16 11:40:28  dischi
# remove poll_menu_only
#
# Revision 1.9  2005/07/16 09:48:23  dischi
# adjust to new event interface
#
# Revision 1.8  2005/07/15 20:42:53  dischi
# remove variable event_listener, not needed anymore
#
# Revision 1.7  2005/06/09 19:43:53  dischi
# clean up eventhandler usage
#
# Revision 1.6  2005/01/08 15:40:52  dischi
# remove TRUE, FALSE, DEBUG and HELPER
#
# Revision 1.5  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.4  2004/10/06 19:24:02  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.3  2004/07/26 18:10:18  dischi
# move global event handling to eventhandler.py
#
# Revision 1.2  2004/07/10 12:33:40  dischi
# header cleanup
#
# Revision 1.1  2004/01/10 21:32:53  mikeruelle
# ok this works well enough now.
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file doc/CREDITS for a complete list of authors.
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


import time
import os
import config
import plugin
from playlist import Playlist
import event as em
import fxditem

import logging
log = logging.getLogger()

class PluginInterface(plugin.DaemonPlugin):
    """
    A plugin to start a screensaver when freevo has been inactive in a menu
    for a long time. There are 4 basic types and one of the types has two
    subtypes. The types are xscreensaver, ssr, fxd, and script. The fxd type
    has two subtypes: one for movies and one for slideshows. The 
    xsccreensaver type will only work if you are using an Xserver. 
    
    Here is an example xscreensaver type. You must provide the paths to
    your xscreensaver and xscreensaver-command programs.
    plugin.activate('freevoscreensaver', args=('xscreensaver','/usr/bin/xscreensaver','/usr/bin/xscreensaver-command',))
    
    Here is a script type example. Basically you write a  start and stop
    script you wish to use for a screensaver. This is a catchall for people
    wanting a very specific saver with a specific config.
    plugin.activate('freevoscreensaver', args=('script','/usr/local/bin/screensaverstart','/usr/local/bin/screensaverstop',))

    Shown below is and example of a ssr type of screensaver. It takes an ssr
    file which refers to a bunch of pictures and displays them repeatedly.
    plugin.activate('freevoscreensaver', args=('ssr','/usr/local/freevo_data/Images/blah.ssr',))

    Here is an image type fxd. Very similar to the ssr but taking the fxd
    playlist approach to showing the images. This way you can set random if
    you want it for example.
    plugin.activate('freevoscreensaver', args=('fxd','/usr/local/freevo_data/Images/saver.fxd','image',))

    A video version of the fxd type screensaver. It repeatedly shows a movie
    in a loop with no sound.
    plugin.activate('freevoscreensaver', args=('fxd','/usr/local/freevo_data/Movies/saver.fxd','video',))
    """
    def __init__(self, sstype, ssarg1, ssarg2=None):
        plugin.DaemonPlugin.__init__(self)
        self.plugin_name = 'SCREENSAVER'
	self.last_event = 0
        self.screensaver_showing = False
	self.vitem = None
	self.pl = None
	self.poll_interval = config.SSAVER_POLL
	self.saver_delay = config.SSAVER_DELAY
	self.saver_type = sstype
	self.arg1 = ssarg1
        self.arg2 = ssarg2

    def config(self):
        return [ ('SSAVER_DELAY', 300, '# of seconds to wait to start saver.'),
	         ('SSAVER_POLL', 600, '# of seconds to wait between polling.') ]

    def eventhandler(self, event):
        """
        eventhandler to handle the events. Always return false since we
	are just a listener and really can't send back true.
        """
        log.info("Saver saw %s" % event.name)

        if event.name == 'SCREENSAVER_START':
	    self.start_saver()
	    return True

        if event.name == 'SCREENSAVER_STOP' and self.screensaver_showing :
	    self.stop_saver()
	    return True

        # gotta ignore these or video screensavers shutoff before they begin
	if event.name == 'VIDEO_START' or event.name == 'PLAY_START' or event.name == 'VIDEO_END' or event.name == 'PLAY_END':
	    return True

        if self.screensaver_showing :
	    self.stop_saver()

	if not event.name == 'IDENTIFY_MEDIA':
	    self.last_event = time.time()

        return True

    def poll(self):
        log.info("Saver got polled %f" % time.time())
	if not self.screensaver_showing and (time.time() - self.last_event) > self.saver_delay :
	    em.Event("SCREENSAVER_START").post()

    def start_saver (self):
        log.info("start screensaver")
        self.screensaver_showing = True
        if self.saver_type == 'xscreensaver':
            os.system('%s -no-splash &' % self.arg1)
            os.system('sleep 5 ; %s -activate' % self.arg2)
        elif self.saver_type == 'script':
            os.system('%s' % self.arg1)
        elif self.saver_type == 'ssr':
            self.pl = Playlist('ScreenSaver', playlist=self.arg1, type='image', repeat=True)
            self.pl.play()
        elif self.saver_type == 'fxd':
            mylist = fxditem.mimetype.parse(None, [self.arg1], display_type=self.arg2)
            if len(mylist) > 0:
                self.pl = mylist[0]
                arg = None
                if self.arg2 == 'image':
                    self.pl.repeat = 1
                elif self.arg2 == 'video':
                    arg = '-nosound -loop 0'
                self.pl.play(arg=arg)
            else:
                log.warning("saver thinks fxd blew up trying to parse?")
        else:
            log.error("Unknown saver type to start.")

    
    def stop_saver (self):
        log.info("stop screensaver")
        self.screensaver_showing = False
        if self.saver_type == 'xscreensaver':
            os.system('%s -exit' % self.arg2)
        elif self.saver_type == 'script':
            os.system('%s' % self.arg2)
        elif self.saver_type == 'ssr':
            em.STOP.post()
        elif self.saver_type == 'fxd':
            em.STOP.post()
        else:
            log.error("Unknown saver type to stop.")

