# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# generic_record.py - A plugin to record tv using VCR_CMD.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/10/06 19:19:13  dischi
# use new childapp interface
#
# Revision 1.1  2004/08/05 17:35:40  dischi
# move recordserver and plugins into extra dir
#
# Revision 1.23  2004/07/26 18:10:19  dischi
# move global event handling to eventhandler.py
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2003 Krister Lagerstrom, et al. 
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


import sys
import time
import os

import config
import childapp 
import plugin 
import util.tv_util as tv_util

from event import *
from tv.channels import FreevoChannels

DEBUG = config.DEBUG


class PluginInterface(plugin.Plugin):
    def __init__(self):
        plugin.Plugin.__init__(self)
        plugin.register(Recorder(), plugin.RECORD)


class Recorder:

    def __init__(self):
        if DEBUG:
            print 'Activating Generic Record Plugin'

        self.fc = FreevoChannels()
        

    def start(self, rec_prog):
        frequency = self.fc.chanSet(str(rec_prog.tunerid), 'record plugin')

        rec_prog.filename = tv_util.getProgFilename(rec_prog)

        cl_options = { 'channel'  : rec_prog.tunerid,
                       'frequency' : frequency,
                       'filename' : rec_prog.filename,
                       'base_filename' : os.path.basename(rec_prog.filename),
                       'title' : rec_prog.title,
                       'sub-title' : rec_prog.sub_title,
                       'seconds'  : rec_prog.rec_duration }

        self.rec_command = config.VCR_CMD % cl_options

        self.app = childapp.Instance( self.rec_command )
        if DEBUG:
            print('Recorder::Record: %s' % self.rec_command)
        
        
    def stop(self):
        self.thread.mode = 'stop'
        self.thread.mode_flag.set()
