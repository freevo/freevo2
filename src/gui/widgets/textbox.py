# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# text.py - A text widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
#
# Revision 1.3  2004/08/01 10:37:08  dischi
# smaller changes to stuff I need
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
# -----------------------------------------------------------------------

from mevas.image import CanvasImage
import text

class Textbox(text.Text):
    """
    A multi line text object
    """
    def __init__(self, text, (x, y), (width, height), font, align_h='left',
                 align_v='top', mode='hard', ellipses = '...', 
                 fgcolor=None, bgcolor=None):

        if not text or height < font.height:
            CanvasImage.__init__(self, (1, 1))
            return

        self.font = font

        line_height = font.height * 1.1
        if int(line_height) < line_height:
            line_height = int(line_height) + 1
        max_lines = int((height + line_height - font.height) / line_height)
        max_width = 0
        
        # split the text into lines
        # FIXME: respect for '\n' is missing
        formated_text    = []
        current_ellipses = ''
        while text:
            if len(formated_text) == max_lines - 1:
                current_ellipses = ellipses
            if len(formated_text) == max_lines:
                break

            w = font.stringsize(text)
            if font.stringsize(text) <= width:
                formated_text.append((text, w))
                max_width = max(max_width, w)
                text = ''
            else:
                if mode == 'hard':
                    fit, rest = self._cut_string(text, width, '', current_ellipses)
                else:
                    fit, rest = self._cut_string(text, width, ' ', current_ellipses)
                    if not fit:
                        # nothing fits? Try to break words at ' -_'
                        fit, rest = self._cut_string(text, width, '-_ ', current_ellipses)
                        if not fit:
                            # still nothing? Try the 'hard' way:
                            fit, rest = self._cut_string(text, width, '', current_ellipses)
                w = font.stringsize(fit)
                formated_text.append((fit, w))
                max_width = max(max_width, w)
                text = rest.lstrip()

        # store not fitting text
        self.rest = text

        # calculate some internal variables
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self._calculate_vars()

        box_width  = max_width
        box_height = line_height * len(formated_text)

        # create the needed CanvasImage
        CanvasImage.__init__(self, (box_width, box_height))
        
        # set the box position
        if align_v == 'center':
            y += (height - box_height) / 2
        if align_v == 'bottom':
            y += height - box_height

        if align_h == 'center':
            x += (width - box_width) / 2
        if align_h == 'right':
            x += width - box_width

        self.set_pos((x, y))

        # create background
        if self.bgcolor:
            self.draw_rectangle((0, 0), (box_width, box_height), self.bgcolor, 1)

        # fill the box with text
        y0 = 0
        for text, width in formated_text:
            try:
                self._render(text, (0, y0), (box_width, line_height))
            except Exception, e:
                _debug_(e, 0)
            y0 += line_height

