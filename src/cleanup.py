# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# cleanup.py  -  shutdown handling
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2005/06/28 15:56:07  dischi
# use popen from notifier and remove util.popen
#
# Revision 1.8  2005/06/16 15:54:36  dischi
# update system exit
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

import os
import time
import sys
import copy
import logging

import kaa.notifier

log = logging.getLogger()

_callbacks = []

def register( function, *arg ):
    """
    """
    _callbacks.append( [ function, arg ] )

        
def unregister( function ):
    """
    """
    for c in _callbacks:
        if c[ 0 ] == function:
            log.debug('unregister shutdown callback: %s' % function)
            _callbacks.remove( c )


_exit = False

def shutdown(menuw=None, argshutdown=None, argrestart=None, exit=False):
    """
    Function to shut down freevo or the whole system. This system will be
    shut down when argshutdown is True, restarted when argrestart is true,
    else only Freevo will be stopped.
    """
    # Import all this stuff now we need for shutdown. It is not possible
    # to do this on startup (recursive imports)
    # FIXME: this is bad coding style
    import mediadb
    import gui
    import gui.widgets
    import gui.theme
    import config

    global _callbacks
    global _exit

    # FIXME: this is bad. The whole shutdown stuff needs a cleanup.
    # There are four ways of shutdown: exit(1) somewhere, an exception,
    # a signal (e.g. C-c) and a normal shutdown.
    if _exit:
        sys.exit(0)
    _exit = True
    
    mediadb.save()
    if not gui.displays.active():
        # this function is called from the signal handler, but
        # we are dead already.
        sys.exit(0)

    gui.display.clear()
    msg = gui.widgets.Text(_('shutting down...'), (0, 0),
                           (gui.width, gui.height), gui.theme.font('default'),
                           align_h='center', align_v='center')
    gui.display.add_child(msg)
    gui.display.update()
    time.sleep(0.5)

    if argshutdown or argrestart:  
        # shutdown dual head for mga
        if config.CONF.display == 'mga':
            os.system('%s runapp matroxset -f /dev/fb1 -m 0' % \
                      os.environ['FREEVO_SCRIPT'])
            time.sleep(1)
            os.system('%s runapp matroxset -f /dev/fb0 -m 1' % \
                      os.environ['FREEVO_SCRIPT'])
            time.sleep(1)

        # Shutdown all children still running
        for c in _callbacks:
            log.debug('shutting down %s' % c[ 0 ])
            c[ 0 ]( *c[ 1 ] )

        # shutdown processes
        kaa.notifier.shutdown()

        _callbacks = []
        gui.displays.shutdown()

        if argshutdown and not argrestart:
            os.system(config.SHUTDOWN_SYS_CMD)
        elif argrestart and not argshutdown:
            os.system(config.RESTART_SYS_CMD)
        # let freevo be killed by init, looks nicer for mga
        kaa.notifier.loop()
        return

    #
    # Exit Freevo
    #

    # Shutdown all children still running
    for c in copy.copy(_callbacks):
        log.debug( 'shutting down %s' % c[ 0 ])
        c[ 0 ]( *c[ 1 ] )
    _callbacks = []

    # shutdown processes
    kaa.notifier.shutdown()

    # Shutdown the display
    gui.displays.shutdown()

    if exit:
        # realy exit, we are called by the signal handler
        sys.exit(0)

    os.system('%s stop' % os.environ['FREEVO_SCRIPT'])

    # Just wait until we're dead. SDL cannot be polled here anyway.
    kaa.notifier.loop()
