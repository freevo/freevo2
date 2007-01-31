# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# idlebar/MultiMail - IdleBar plugins for checking email accounts
# -----------------------------------------------------------------------
#
# Author : Chris Griffiths (freevo@y-fronts.com)
# Date   : Nov 8th 2003
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.9  2005/06/04 17:18:14  dischi
# adjust to gui changes
#
# Revision 1.8  2004/11/20 18:23:03  dischi
# use python logger module for debug
#
# Revision 1.7  2004/09/08 08:33:13  dischi
# patch from Viggo Fredriksen to reactivate the plugins
#
# Revision 1.6  2004/08/01 10:48:47  dischi
# deactivate plugin because of interface change
#
# Revision 1.5  2004/07/24 17:49:48  dischi
# rename or deactivate some stuff for gui update
#
# Revision 1.4  2004/07/10 12:33:41  dischi
# header cleanup
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

import os
from freevo.ui import config, gui
import imaplib
import poplib
import mailbox
import threading
import time
from freevo.ui.gui import theme, imagelib, widgets

from freevo.ui.plugins.idlebar import IdleBarPlugin

import logging
log = logging.getLogger()

class MultiMail(IdleBarPlugin):
    """
    Displays an icon in the idlebar representing the number of emails for a specified account. In the case of IMAP, it only lists unread messages

    Activate with:
    plugin.activate('idlebar.MultiMail.Imap',    level=10, args=('username', 'password', 'host', 'port', 'folder')) (port and folder are optional)
    plugin.activate('idlebar.MultiMail.Pop3',    level=10, args=('username', 'password', 'host', 'port')) (port is optional)
    plugin.activate('idlebar.MultiMail.Mbox',    level=10, args=('path to mailbox file')

    """
    def __init__(self):

        IdleBarPlugin.__init__(self)
        self.NO_MAILIMAGE = os.path.join(config.ICON_DIR, 'status', 'newmail_dimmed.png')
        self.MAILIMAGE = os.path.join(config.ICON_DIR, 'status', 'newmail_active_small.png')
        self.FREQUENCY = 20 # seconds between checks
        self.unread = 0
        self.last_unread = -1
        self.bg_thread = threading.Thread(target=self._bg_function, name='MultiMail Thread')
        self.bg_thread.setDaemon(1)
        self.bg_thread.start() # Run self._bg_function() in a separate thread

    def _bg_function(self):
        while 1:
            self.unread = self.checkmail()
            time.sleep(self.FREQUENCY)

    def checkmail(self):
        return 0

    def draw(self, width, height):
        if self.last_unread == self.unread:
            return self.NO_CHANGE

        self.clear()
        self.last_unread = self.unread

        if self.unread > 0:
            i = imagelib.load(self.MAILIMAGE, (None, None))
            self.objects.append(widgets.Image(i, (0, 2)))
            font  = theme.font('weather')
            str_unread = '%3s' % self.unread
            text_width = font.stringsize(str_unread)
            t = widgets.Text(str_unread, (0, 55-font.height), (text_width, font.height),
                         font, 'left', 'top')
            self.objects.append(t)
            return max(i.width, t.width)

        i = imagelib.load(self.NO_MAILIMAGE, (None, None))
        self.objects.append(widgets.Image(i, (0, 10)))
        return i.width

class Imap(MultiMail):
    def __init__(self, username, password, host, port=143, folder="INBOX"):
        self.USERNAME = username
        self.PASSWORD = password
        self.HOST = host
        self.PORT = port
        self.FOLDER = folder
        MultiMail.__init__(self)

    def checkmail(self):
        try:
            imap = imaplib.IMAP4(self.HOST)
            imap.login(self.USERNAME,self.PASSWORD)
            imap.select(self.FOLDER)
            unread = len(imap.search(None,"(UNSEEN)")[1][0].split())
            imap.logout()
            return unread
        except:
            log.error('IMAP exception')
            return 0

class Pop3(MultiMail):
    def __init__(self, username, password, host, port=110):
        self.USERNAME = username
        self.PASSWORD = password
        self.HOST = host
        self.PORT = port
        MultiMail.__init__(self)

    def checkmail(self):
        try:
            pop = poplib.POP3(self.HOST, self.PORT)
            pop.user(self.USERNAME)
            pop.pass_(self.PASSWORD)
            unread = len(pop.list()[1])
            pop.quit()
            return unread
        except:
            return 0

class Mbox(MultiMail):
    def __init__(self, mailbox):
        self.MAILBOX = mailbox
        MultiMail.__init__(self)

    def checkmail(self):
        if os.path.isfile(self.MAILBOX):
            mb = mailbox.UnixMailbox (file(self.MAILBOX,'r'))
            msg = mb.next()
            count = 0
            while msg is not None:
                count = count + 1
                msg = mb.next()
            return count
        else:
            return 0

