# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# tvstat.py - A small helper to get some information on your 
#             v4l2 and DVB devices.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.4  2004/11/19 02:18:22  rshortt
# Changes for moving TV cards autodetection into system.
#
# Revision 1.3  2004/11/13 15:58:01  dischi
# more dvb info
#
# Revision 1.2  2004/08/13 16:17:33  rshortt
# More work on tv settings, configuration of v4l2 devices based on TV_SETTINGS.
#
# Revision 1.1  2004/08/12 16:58:58  rshortt
# Run this helper to see how freevo autodetected your tv/dvb cards.  This will be changing slightly and will be a good tool to get debug information from users.
#
#
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

import time, string, sys

import config
import system
import tv.v4l2
import tv.ivtv

from system.tvcards import TVCard, IVTVCard, DVBCard

system.detect('tvcards')


def main():

    for key, card in config.TV_SETTINGS.items():
        print '\n*** %s ***' % key
        v4l2 = None

        if isinstance(card, IVTVCard):
            v4l2 = tv.ivtv.IVTV(key)
            print 'vdev: %s' % v4l2.settings.vdev

        elif isinstance(card, TVCard):
            v4l2 = tv.v4l2.Videodev(key)
            print 'vdev: %s' % v4l2.settings.vdev

        elif isinstance(card, DVBCard):
            print 'adapter: %s' % card.adapter
            print 'Card: %s' % card.name
            print 'Type: %s' % card.type
        if v4l2:
            v4l2.init_settings()
            v4l2.print_settings()
            v4l2.close()
    

if __name__ == '__main__':
    main()
