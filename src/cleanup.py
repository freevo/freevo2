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
# Revision 1.5  2005/04/10 18:08:05  dischi
# switch to new mediainfo module
#
# Revision 1.4  2004/12/18 13:39:08  dischi
# wait using the notifier, stop popen children
#
# Revision 1.3  2004/11/20 18:22:58  dischi
# use python logger module for debug
#
# Revision 1.2  2004/10/08 20:18:52  dischi
# plugins register to cleanup, no need to call plugin.cleanup()
#
# Revision 1.1  2004/10/06 18:44:51  dischi
# move shutdown code from plugin to cleanup.py
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

import os
import time
import sys
import copy
import notifier
import config

import logging
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


def shutdown(menuw=None, argshutdown=None, argrestart=None, exit=False):
    """
    Function to shut down freevo or the whole system. This system will be
    shut down when argshutdown is True, restarted when argrestart is true,
    else only Freevo will be stopped.
    """
    import util.popen
    import mediadb
    import gui

    global _callbacks
    
    mediadb.save()
    if not gui.displays.active():
        # this function is called from the signal handler, but
        # we are dead already.
        sys.exit(0)

    gui.display.clear()
    msg = gui.Text(_('shutting down...'), (0, 0), (gui.width, gui.height),
                   gui.get_font('default'), align_h='center', align_v='center')
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
        util.popen.killall()
        _callbacks = []
        gui.displays.shutdown()

        if argshutdown and not argrestart:
            os.system(config.SHUTDOWN_SYS_CMD)
        elif argrestart and not argshutdown:
            os.system(config.RESTART_SYS_CMD)
        # let freevo be killed by init, looks nicer for mga
        notifier.loop()
        return

    #
    # Exit Freevo
    #

    # Shutdown all children still running
    for c in copy.copy(_callbacks):
        log.debug( 'shutting down %s' % c[ 0 ])
        c[ 0 ]( *c[ 1 ] )
    _callbacks = []

    util.popen.killall()

    # Shutdown the display
    gui.displays.shutdown()

    if exit:
        # realy exit, we are called by the signal handler
        sys.exit(0)

    os.system('%s stop' % os.environ['FREEVO_SCRIPT'])

    # Just wait until we're dead. SDL cannot be polled here anyway.
    notifier.loop()
