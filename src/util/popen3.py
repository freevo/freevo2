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
# Revision 1.11  2004/07/10 12:33:42  dischi
# header cleanup
#
# Revision 1.10  2004/05/28 20:22:32  dischi
# add run function as better os.system
#
# Revision 1.9  2004/01/04 13:07:32  dischi
# close file handlers
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


import time
import traceback
import popen2
import os
import time
import thread
import types

import config
import rc
from event import *

class child_handler:
    child   = ''


class Popen4(popen2.Popen3):
    """
    Like popen2.Popen3 but without the capturestderr and the bufsize parameter.
    A new optional parameter is cwd, the child will change the working directory
    after fork and before exec.
    """
    def __init__(self, cmd, cwd=None):
        self._cwd = cwd
        popen2.Popen3.__init__(self, cmd, 1, 100)
        
    def _run_child(self, cmd):
        if self._cwd:
            os.chdir(self._cwd)
        if isinstance(cmd, types.StringTypes):
            cmd = ['/bin/sh', '-c', cmd]
        for i in range(3, popen2.MAXFD):
            try:
                os.close(i)
            except:
                pass
        try:
            os.execvp(cmd[0], cmd)
        finally:
            os._exit(1)
    

def Popen3(cmd, cwd = None):
    """
    Wrapper for the thread problem. It looks like the class Popen4
    """
    # do not use this for helpers
    if config.HELPER and not config.IS_RECORDSERVER:
        return Popen4(cmd, cwd=cwd)

    # do not use this for the main thread
    if traceback.extract_stack()[0][0].find('thread') == -1:
        return Popen4(cmd, cwd=cwd)
        
    childapp = child_handler()
    
    rc.post_event(Event(OS_EVENT_POPEN2, (childapp, cmd)))
    while(childapp.child == ''):
        time.sleep(0.01)
    
    return childapp.child



dead_childs = []
wait_lock   = thread.allocate_lock()


def waitpid(pid=0):
    """
    waitpid wrapper
    """
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
        rc.post_event(Event(OS_EVENT_WAITPID, (pid,)))
        return True

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
    

def stdout(app):
    """
    start app and return the stdout
    """
    ret = []
    child = popen2.Popen3(app, 1, 100)
    while(1):
        data = child.fromchild.readline()
        if not data:
            break
        ret.append(data)
    child.wait()
    child.fromchild.close()
    child.childerr.close()
    child.tochild.close()
    return ret


def run(app, object, signal=15):
    """
    run a child until object.abort is True. Than kill the child with
    the given signal
    """
    if isinstance(app, str) or isinstance(app, unicode):
        print 'WARNING: popen.run with string as app'
        print 'This may cause some problems with threads'
        
    child = popen2.Popen3(app, 1, 100)
    child.childerr.close()
    child.fromchild.close()
    while(1):
        time.sleep(0.1)
        if object.abort:
            os.kill(child.pid, signal)

        try:
            pid = os.waitpid(child.pid, os.WNOHANG)[0]
        except OSError:
            break
        
        if pid:
            break
        
    child.tochild.close()
