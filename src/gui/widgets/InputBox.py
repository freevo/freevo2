# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# InputBox.py - a popup box that has a message and allows the user
#               to input using the remote control
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.3  2004/10/03 15:54:00  dischi
# make PopupBoxes work again as they should
#
# Revision 1.2  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
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


from event import *
from PopupBox import PopupBox

class InputBox(PopupBox):
    """
    """
    def __init__(self, text, handler=None, type='text', x=None, y=None, width=0, height=0,
                 icon=None, vertical_expansion=1, text_prop=None, input_text='',
                 numboxes=0, parent='osd'):

        PopupBox.__init__(self, 'input box not working', handler)
        
