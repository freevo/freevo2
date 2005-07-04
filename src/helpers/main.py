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
    import kaa.notifier
    if kaa.notifier.VERSION < '0.3.0':
        raise ImportError('found version %s' % kaa.notifier.VERSION)
    kaa.notifier.init(kaa.notifier.GENERIC)
except Exception, e:
    print 'Error: This version of Freevo requires pyNotifier >= 0.3.0'
    print 'To download and install pyNotifier to ./site-packages run \'make\''
    sys.exit(0)

#
# imlib2 checking
#
try:
    import kaa
except:
    d = os.path.dirname(__file__)[:-15]
    print 'The kaa module repository could not be loaded!'
    print
    print 'Please check out the kaa repository from Freevo cvs'
    print 'cvs -d:pserver:anonymous@cvs.sf.net:/cvsroot/freevo login'
    print 'cvs -z3 -d:pserver:anonymous@cvs.sf.net:/cvsroot/freevo co -P kaa'
    print
    print 'Please install it as root into your system or into the Freevo'
    print 'site-lisp directory be running setup in the kaa root directory:'
    print 'python setup.py install --install-lib=%s \\' % d
    print '    --install-scripts=%s/bin' % d
    print 'When using the command above, you need to reinstall kaa every time'
    print 'you run \'make clean\' in the freevo directory.'
    print
    print 'Kaa is under development right now. Make sure you update the kaa'
    print 'directory every time you update freevo cvs.'
    print
    sys.exit(1)


#
# check if a plugin.py* is in the current dir
#

p = os.path.join(os.path.dirname(__file__), 'plugins.')
for ext in ('py', 'pyc', 'pyo'):
    if os.path.isfile(p + ext):
        print 'Error: Old plugin helper detected. Please remove'
        print p + ext
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
# checking for lsdvd to be used in kaa.metadata
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
# kaa.metadata version checking
#
try:
    import kaa.metadata.version
    if kaa.metadata.version.CHANGED < 20040629:
        raise ImportError('found version %s' % kaa.metadata.version.VERSION)
except ImportError:
    print 'Error: This version of Freevo requires kaa.metadata >= 0.4.3'
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
import gui.widgets
import gui.theme
import util
import plugin
import mcomm

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
        self.bar = gui.widgets.Progressbar((x0, y), (x1-x0, 20), 2, (0,0,0),
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
    gui.theme.get().prepare()

    # start menu
    MainMenu()

    # Wait for the startup animation. This is a bad hack but we won't
    # be able to remove our splashscreen otherwise. Big FIXME!
    gui.animation.render().wait()

    # delete splash screen
    splash.destroy()
    del splash

    # kick off the main menu loop
    kaa.notifier.addDispatcher( eventhandler.get_singleton().handle )

    # start main loop
    kaa.notifier.loop()

except:
    log.exception('Crash!')
    kaa.notifier.shutdown()
