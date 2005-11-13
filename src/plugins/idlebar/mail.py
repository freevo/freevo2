# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# mail.py - IdleBarPlugin for showing mbox status
# -----------------------------------------------------------------------
# $Id:
#
# -----------------------------------------------------------------------
# $Log:
#
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
import mailbox

import gui.widgets
import gui.imagelib
import config
from plugins.idlebar import IdleBarPlugin

class PluginInterface(IdleBarPlugin):
    """
    Shows if new mail is in the mailbox.

    Activate with:
    plugin.activate('idlebar.mail',    level=10, args=('path to mailbox', ))

    """
    def __init__(self, mailbox):
        IdleBarPlugin.__init__(self)
        self.mails = -1
        self.NO_MAILIMAGE = os.path.join(config.ICON_DIR, 'status/newmail_dimmed.png')
        self.MAILIMAGE = os.path.join(config.ICON_DIR, 'status/newmail_active.png')
        self.MAILBOX = mailbox

    def checkmail(self):
        if not self.MAILBOX:
            return 0
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

    def draw(self, width, height):
        mails = self.checkmail()

        if self.mails == mails:
            return self.NO_CHANGE

        self.mails = mails
        self.clear()

        if mails > 0:
            m = gui.imagelib.load(self.MAILIMAGE, (None, None))
        else:
            m = gui.imagelib.load(self.NO_MAILIMAGE, (None, None))

        self.objects.append(gui.widgets.Image(m, (0, (height-m.height)/2)))

        return m.width
