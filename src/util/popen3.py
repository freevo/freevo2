#if 0 /*
# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# util/popen3.py - popen2 warpper
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2003/10/18 21:34:19  rshortt
# recordserver now handles events like main.
#
# Revision 1.2  2003/10/18 17:56:58  dischi
# more childapp fixes
#
# Revision 1.1  2003/10/18 10:45:46  dischi
# our own thread working version of popen and waitpid
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


import time
import traceback
import popen2
import os
import time
import thread

import config
import rc
from event import *

class child_handler:
    child   = ''


def Popen3(program):

    # do not use this for helpers
    if config.HELPER and not config.IS_RECORDSERVER:
        return popen2.Popen3(program, 1, 100)

    # do not use this for the main thread
    if traceback.extract_stack()[0][0].find('thread') == -1:
        return popen2.Popen3(program, 1, 100)
        
    childapp = child_handler()
    
    rc.post_event(Event(OS_EVENT_POPEN2, (childapp, program)))
    while(childapp.child == ''):
        time.sleep(0.01)
    
    return childapp.child



dead_childs = []
wait_lock   = thread.allocate_lock()


def waitpid(pid=0):
    global dead_childs
    if pid == 0:
        _debug_('main checking childs', 2)
        try:
            pid = os.waitpid(pid, os.WNOHANG)[0]
        except OSError:
            # child anymore
            return
        
        if pid:
            wait_lock.acquire()
            dead_childs.append(pid)
            wait_lock.release()
        return
    
    if config.IS_RECORDSERVER:
        # add handling for recordserver here
        return os.waitpid(pid, os.WNOHANG)[0] == pid

    # do not use this for helpers
    if config.HELPER:
        return os.waitpid(pid, os.WNOHANG)[0] == pid

    # do not use this for the main thread
    if traceback.extract_stack()[0][0].find('thread') == -1:
        return os.waitpid(pid, os.WNOHANG)[0] == pid
        
    _debug_('poll', 2)
    wait_lock.acquire()
    if pid in dead_childs:
        dead_childs.remove(pid)
        wait_lock.release()
        return 1
    wait_lock.release()
    return 0
    
