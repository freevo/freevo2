# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# main.py - This is the Freevo main application code
# -----------------------------------------------------------------------------
# $Id$
#
# This file is the python start file for Freevo. It handles the init phase like
# checking the python modules, loading the plugins and starting the main menu.
#
# It also contains the splashscreen.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
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
# -----------------------------------------------------------------------------

# python imports
import os
import sys, time
import traceback
import signal

import logging
import logging.config

# get logging object
log = logging.getLogger()

#
# notifier version checking
#
try:
    import notifier
    if notifier.VERSION < '0.3.0':
        raise ImportError('found version %s' % notifier.VERSION)
    notifier.init(notifier.GENERIC)
except Exception, e:
    print 'Error: This version of Freevo requires pyNotifier >= 0.3.0'
    print 'To download and install pyNotifier to ./site-packages run \'make\''
    sys.exit(0)

#
# imlib2 checking
#
try:
    import Imlib2
except:
    print 'The python Imlib2 bindings could not be loaded!'
    print 'To compile pyimlib run \'make\''
    sys.exit(1)



try:
    # i18n support

    # First load the xml module. It's not needed here but it will mess
    # up with the domain we set (set it from freevo 4Suite). By loading it
    # first, Freevo will override the 4Suite setting to freevo
    try:
        from xml.utils import qp_xml
        from xml.dom import minidom
    except ImportError:
        raise ImportError('No module named pyxml')

    # now load other modules to check if all requirements are installed
    import Image
    import sqlite

    import config
    if config.GUI_DISPLAY == 'SDL':
        import pygame

except ImportError, i:
    print 'ImportError: %s' % i
    print 'Not all requirements of Freevo are installed on your system.'
    print 'Please check the INSTALL file for more informations.'
    print
    sys.exit(0)


#
# checking for lsdvd to be used in mmpython
#
if not config.CONF.lsdvd:
    print
    print 'Can\'t find lsdvd. DVD support will be limited and maybe not'
    print 'all discs are detected. Please install lsdvd, you can get it'
    print 'from http://acidrip.thirtythreeandathird.net/lsdvd.html'
    print
    print 'After installing it, you should run \'freevo cache --rebuild\''
else:
    os.environ['LSDVD'] = config.CONF.lsdvd


#
# mmpython version checking
#
try:
    import mmpython.version
    if mmpython.version.CHANGED < 20040629:
        raise ImportError('found version %s' % mmpython.version.VERSION)
except ImportError:
    print 'Error: This version of Freevo requires mmpython >= 0.4.3'
    print 'You can download the latest release from'
    print 'http://sourceforge.net/project/showfiles.php?group_id=75590'
    print
    sys.exit(0)


#
# mbus version checking
#
try:
    import mbus
    if mbus.VERSION < '0.8.1':
        raise ImportError('found version %s' % mbus.VERSION)
except Exception, e:
    print 'Error: This version of Freevo requires pyMbus >= 0.8.1'
    print 'To download and install pyMbus to ./site-packages run \'make\''
    print e
    print
    sys.exit(0)


# freevo imports
import eventhandler
import gui
import gui.displays
import gui.areas
import gui.animation
import util
import plugin
import mcomm

from cleanup import shutdown
from mainmenu import MainMenu

# load the fxditem to make sure it's the first in the
# mimetypes list
import fxditem


class Splashscreen(gui.areas.Area):
    """
    A simple splash screen for osd startup
    """
    def __init__(self, text, max_value):
        gui.areas.Area.__init__(self, 'content')
        self.max_value = max_value
        self.text      = text
        self.bar       = None
        self.engine    = gui.areas.Handler('splashscreen', ('screen', self))
        self.engine.show()


    def clear(self):
        """
        clear all content objects
        """
        self.bar.unparent()
        self.text.unparent()


    def update(self):
        """
        update the splashscreen
        """
        if self.bar:
            return

        settings = self.settings
        x0, x1 = settings.x, settings.x + settings.width
        y = settings.y + settings.font.font.height + settings.spacing

        self.text = self.drawstring(self.text, settings.font, settings,
                                    height=-1, align_h='center')
        self.bar = gui.Progressbar((x0, y), (x1-x0, 20), 2, (0,0,0),
                                   None, 0, None, (0,0,0,95), 0,
                                   self.max_value)
        self.layer.add_child(self.bar)


    def progress(self):
        """
        set the progress position and refresh the screen
        """
        if self.bar:
            self.bar.tick()
        if self.engine:
            self.engine.draw(None)


    def hide(self):
        """
        fade out
        """
        self.engine.hide(config.GUI_FADE_STEPS)


    def destroy(self):
        """
        destroy the object
        """
        del self.engine


class RPCHandler(mcomm.RPCServer):
    """
    Handle some basic rpc commands.
    """
    def __rpc_status__(self, addr, val):
        """
        Send status on rpc status request.
        """
        idle = eventhandler.idle_time()
        status = { 'idle': idle }
        return mcomm.RPCReturn(status)


def signal_handler(sig, frame):
    """
    the signal handler to shut down freevo
    """
    if sig in (signal.SIGTERM, signal.SIGINT):
        shutdown(exit=True)



#
# Freevo main function
#

# parse arguments
if len(sys.argv) >= 2:

    # force fullscreen mode
    # deactivate screen blanking and set osd to fullscreen
    if sys.argv[1] == '-force-fs':
        os.system('xset -dpms s off')
        config.START_FULLSCREEN_X = 1

try:
    # signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # create gui
    gui.displays.create()
    
    # Fire up splashscreen and load the plugins
    splash = Splashscreen(_('Starting Freevo, please wait ...'),
                          plugin.get_number()-1)
    # laod mbus interface
    rpc = RPCHandler()
    # load plugins
    plugin.init(splash.progress)

    # fade out the splash screen
    splash.hide()

    # prepare again, now that all plugins are loaded
    gui.get_theme().prepare()

    # start menu
    MainMenu().getcmd()

    # Wait for the startup animation. This is a bad hack but we won't
    # be able to remove our splashscreen otherwise. Big FIXME!
    gui.animation.render().wait()

    # delete splash screen
    splash.destroy()
    del splash

    # kick off the main menu loop
    notifier.addDispatcher( eventhandler.get_singleton().handle )

    # start main loop
    notifier.loop()


except KeyboardInterrupt:
    log.info('Shutdown by keyboard interrupt')
    # Shutdown Freevo
    shutdown()

except SystemExit:
    pass

except:
    log.exception('Crash!')
    try:
        tb = sys.exc_info()[2]
        fname, lineno, funcname, text = traceback.extract_tb(tb)[-1]

        if config.FREEVO_EVENTHANDLER_SANDBOX:
            secs = 5
        else:
            secs = 1
        # for i in range(secs, 0, -1):
        #     osd.clearscreen(color=osd.COL_BLACK)
        #     osd.drawstring(_('Freevo crashed!'), 70, 70)
        #     osd.drawstring(_('Filename: %s') % fname, 70, 130)
        #     osd.drawstring(_('Lineno: %s') % lineno, 70, 160)
        #     osd.drawstring(_('Function: %s') % funcname, 70, 190)
        #     osd.drawstring(_('Text: %s') % text, 70, 220)
        #     osd.drawstring(str(sys.exc_info()[1]), 70, 280)
        #     osd.drawstring(_('Please see the logfiles for more info'),
        #                    70, 350)
        #     osd.drawstring(_('Exit in %s seconds') % i, 70, 410)
        #     osd.update()
        #     time.sleep(1)
    except:
        pass

    # Shutdown freevo
    shutdown()
