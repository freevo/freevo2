# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# text.py - A text widget
# -----------------------------------------------------------------------------
# $Id$
#
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dmeyer@tzi.de>
# Maintainer:    Dirk Meyer <dmeyer@tzi.de>
#
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
# -----------------------------------------------------------------------------

__all__ = [ 'Text' ]

# python imports
import os
import logging

# mevas imports
import kaa.mevas
from kaa.mevas.image import CanvasImage

# get logging object
log = logging.getLogger('gui')

# alpha channel image for fading out text
_dim_image = None


class Text(CanvasImage):
    """
    A text object that can be drawn onto a layer
    """
    def __init__(self, text, (x, y), (width, height), font, align_h='left',
                 align_v='top', mode='hard', ellipses = '...', dim=True,
                 fgcolor=None, bgcolor=None):

        self.text = text
        if not text or height < font.height:
            CanvasImage.__init__(self, (1, 1))
            return

        if dim:
            ellipses = ''
            mode = 'hard'
            
        self.font  = font
        stringsize = font.stringsize(text)
        if stringsize > width:
            if mode == 'hard':
                text = self._cut_string(text, width, '', ellipses)[0]
            else:
                t = self._cut_string(text, width, ' ', ellipses)[0]
                if not t:
                    # nothing fits? Try to break words at ' -_'
                    t = self._cut_string(text, width, '-_ ', ellipses)[0]
                    if not t:
                        # still nothing? Try the 'hard' way:
                        t = self._cut_string(text, width, '', ellipses)[0]
                text = t
            stringsize = font.stringsize(text)
        else:
            dim = False
            
        if align_h == 'center':
            x += (width - stringsize) / 2
        if align_h == 'right':
            x += width - stringsize
        if align_v == 'center':
            y += (height - font.height) / 2
        if align_v == 'bottom':
            y += height - font.height

        self.dim     = dim
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        
        try:
            self._calculate_vars()
        except Exception, e:
            log.exception(e)

        if stringsize == 0:
            CanvasImage.__init__(self, (1, 1))
            return
            
        CanvasImage.__init__(self, (stringsize, font.height))

        if self.bgcolor:
            self.draw_rectangle((0, 0), (stringsize, font.height),
                                self.bgcolor, 1)

        try:
            self._render(text, (0, 0), (stringsize, font.height))
        except Exception, e:
            log.exception(e)

        if dim:
            global _dim_image
            if not _dim_image:
                image_data = ''
                for i in range(250, 9, -10):
                    image_data += '%c%c%c' % (chr(i), chr(i), chr(i))
                _dim_image = kaa.mevas.imagelib.new((25, 1), image_data, 'RGB')
                _dim_image.scale((25, 1000))
            self.image.draw_mask(_dim_image, (stringsize - 25, 0))

        self.set_pos((x, y))

        

    def _cut_string(self, text, max_width, word_splitter, ellipses):
        """
        Cut the string and return both halfs of it. 
        Only call this function when the string doesn't fit!
        """
        c      = 0                      # num of chars fitting
        space  = 0                      # position of last space
        width  = 0                      # current used width

        ellipses_c     = 0
        ellipses_space = 0
        ellipses_width = 0

        while(True):
            # add a character to the string and calculate the
            # new width for the text
            c += 1
            width = self.font.stringsize(text[:c])
            if ellipses:
                ellipses_width = self.font.stringsize(text[:c] + ellipses)

            # check were the last position would be if we have to use the
            # ellipses
            if ellipses and ellipses_c == 0 and ellipses_width > max_width:
                # if we use ellipses, this is the max position
                ellipses_c = c
            if width > max_width:
                # ok, that's it. We don't have any space left
                break
            if c == len(text):
                # everything fits
                return text, ''
            if word_splitter and text[c] in word_splitter:
                # rememeber the last space for mode == 'soft' (not hard)
                space = c
                if ellipses_c == 0:
                    ellipses_space = c
            if text[c-1] == '\n':
                # Oops, line break, stop right here
                return text[:c-1], text[c:]
            
        # now we a have string that is too long, shorten it again
        if ellipses:
            # we have ellipses so the latest positions are not 'c' and
            # 'space' but 'ellipses_c' and 'ellipses_space'
            if ellipses_c == 1:
                # nothing fits at all, maybe not even the ellipses.
                # shorten the ellipses until it fits the width,
                # return the ellipses and the complete text as rest
                while ellipses and self.font.stringsize(ellipses) > max_width:
                    ellipses = ellipses[:-1]
                return ellipses, text
            if not word_splitter:
                # no word splitter, use latest fitting position
                return text[:ellipses_c-1] + ellipses, text[ellipses_c-1:]
            else:
                # use latest word splitter position
                return text[:ellipses_space] + ellipses, text[ellipses_space:]
        if not word_splitter:
            # no word splitter, use latest fitting position
            return text[:c-1], text[c-1:]
        else:
            # use latest word splitter position
            return text[:space], text[space:]


    def _calculate_vars(self):
        """
        calculate some variables for drawing the string
        """
        self.shadow_x      = 0
        self.shadow_y      = 0
        self.border_color  = None
        self.border_radius = 0
        self.shadow_color  = None

        if hasattr(self.font, 'shadow'):
            # This font object is a skin font object, based on
            # fxd file settings
            if self.font.shadow.visible:
                if self.font.shadow.border:
                    self.border_color  = self.font.shadow.color
                    self.border_radius = int(self.font.font.ptsize/10)
                else:
                    self.shadow_x     = self.font.shadow.y
                    self.shadow_y     = self.font.shadow.x
                    self.shadow_color = self.font.shadow.color
            if not self.fgcolor:
                self.fgcolor = self.font.color
            if not self.bgcolor:
                self.bgcolor = self.font.bgcolor
            self.font = self.font.font

        # save the new values
        self.font = self.font.font


    def _render(self, text, (x, y), (w, h)):
        if self.border_color and self.border_radius:
            x += self.border_radius
            y += self.border_radius
            border = CanvasImage((w, h))
            border.draw_text(text, (0, 0), font=self.font,
                             color=self.border_color)
            for bx in range(-self.border_radius, self.border_radius+1):
                for by in range(-self.border_radius, self.border_radius+1):
                    if bx or by:
                        self.draw_image(border, (x+bx, y+by))
        if self.shadow_color and (self.shadow_x or self.shadow_y):
            self.draw_text(text, (x+self.shadow_x, y+self.shadow_y),
                           font=self.font, color=self.shadow_color)
        self.draw_text(text, (x, y), font=self.font, color=self.fgcolor)


    def __str__(self):
        if len(self.text) > 20:
            t = self.text[:20]
        else:
            t = self.text
        return 'Text: "%s", zindex=%s' % (String(t), self.get_zindex())
    
