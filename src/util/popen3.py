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
# Revision 1.10  2004/05/28 20:22:32  dischi
# add run function as better os.system
#
# Revision 1.9  2004/01/04 13:07:32  dischi
# close file handlers
#
# Revision 1.8  2003/12/10 19:46:35  dischi
# add function to get the stdout of a command call
#
# Revision 1.7  2003/10/19 14:19:44  rshortt
# Added OS_EVENT_WAITPID event for popen3.waitpid() to post so that recordserver
# can pick it up and wait on its own child.  Child processes from recordserver
# now get signals and clean up properly.
#
# Revision 1.6  2003/10/19 12:42:19  rshortt
# Oops.
#
# Revision 1.5  2003/10/19 12:41:13  rshortt
# in waitpid handle recordserver like main.
#
# Revision 1.4  2003/10/19 09:08:14  dischi
# support for changing the working directory before exec, some cleanup changes
#
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
