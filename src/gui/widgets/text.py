# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# text.py - A text widget
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2004/07/25 18:14:05  dischi
# make some widgets and boxes work with the new gui interface
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
# -----------------------------------------------------------------------

import traceback
import config

from base import GUIObject

class Text(GUIObject):
    """
    A text object that can be drawn onto a layer
    """
    def __init__(self, x1, y1, x2, y2, text, font, height, align_h='left',
                 align_v='top', mode='hard', ellipses = '...', dim=True,
                 fgcolor=None, bgcolor=None):
        GUIObject.__init__(self, x1, y1, x2, y2)
        self.text     = text
        self.font     = font
        self.height   = height
        self.align_h  = align_h
        self.align_v  = align_v
        self.mode     = mode
        self.ellipses = ellipses
        self.dim      = dim
        self.fgcolor  = fgcolor
        self.bgcolor  = bgcolor

        self.render_information = None


    def __drawstringframed_line__(self, string, max_width, font, hard,
                                  ellipses, word_splitter):
        """
        calculate _one_ line for drawstringframed. Returns a list:
        width used, string to draw, rest that didn't fit and True if this
        function stopped because of a \n.
        """
        c = 0                           # num of chars fitting
        width = 0                       # width needed
        ls = len(string)
        space = 0                       # position of last space
        last_char_size = 0              # width of the last char
        last_word_size = 0              # width of the last word

        if ellipses:
            # check the width of the ellipses
            ellipses_size = font.stringsize(ellipses)
            if ellipses_size > max_width:
                # if not even the ellipses fit, we have not enough space
                # until the text is shorter than the ellipses
                width = font.stringsize(string)
                if width <= max_width:
                    # ok, text fits
                    return (width, string, '', False)
                # ok, only draw the ellipses, shorten them first
                while(ellipses_size > max_width):
                    ellipses = ellipses[:-1]
                    ellipses_size = font.stringsize(ellipses)
                return (ellipses_size, ellipses, string, False)
        else:
            ellipses_size = 0
            ellipses = ''

        data = None
        while(True):
            if width > max_width - ellipses_size and not data:
                # save this, we will need it when we have not enough space
                # but first try to fit the text without ellipses
                data = c, space, width, last_char_size, last_word_size
            if width > max_width:
                # ok, that's it. We don't have any space left
                break
            if ls == c:
                # everything fits
                return (width, string, '', False)
            if string[c] == '\n':
                # linebreak, we have to stop
                return (width, string[:c], string[c+1:], True)
            if not hard and string[c] in word_splitter:
                # rememeber the last space for mode == 'soft' (not hard)
                space = c
                last_word_size = 0

            # add a char
            last_char_size = font.charsize(string[c])
            width += last_char_size
            last_word_size += last_char_size
            c += 1

        # restore to the pos when the width was one char to big and
        # incl. ellipses_size
        c, space, width, last_char_size, last_word_size = data

        if hard:
            # remove the last char, than it fits
            c -= 1
            width -= last_char_size

        else:
            # go one word back, than it fits
            c = space
            width -= last_word_size

        # calc the matching and rest string and return all this
        return (width+ellipses_size, string[:c]+ellipses, string[c:], False)



    def calculate(self):
        x = self.x1
        y = self.y1

        height = self.height
        width  = self.x2 - self.x1
        font   = self.font
        
        if not self.text:
            return

        shadow_x      = 0
        shadow_y      = 0
        border_color  = None
        border_radius = 0
        shadow_color  = None
        
        dim = config.OSD_DIM_TEXT and self.dim
        # XXX pixels to dim, this should probably be tweaked
        dim_size = 25

        fgcolor = self.fgcolor
        bgcolor = self.bgcolor
        if hasattr(font, 'shadow'):
            # skin font
            if font.shadow.visible:
                if font.shadow.border:
                    border_color  = font.shadow.color
                    border_radius = int(font.font.ptsize/10)
                else:
                    shadow_x     = font.shadow.y
                    shadow_y     = font.shadow.x
                    shadow_color = font.shadow.color
            if not fgcolor:
                fgcolor = font.color
            if not bgcolor:
                bgcolor = font.bgcolor
            font    = font.font

        if height == -1:
            height = font.height
        elif border_color != None:
            height -= border_radius * 2
        else:
            height -= abs(shadow_y)

        width = width - (abs(shadow_x) + border_radius * 2)
        if shadow_x < 0:
            x -= shadow_x
        if shadow_y < 0:
            y -= shadow_y
        x += border_radius
        y += border_radius

        line_height = font.height * 1.1
        if int(line_height) < line_height:
            line_height = int(line_height) + 1

        if width <= 0 or height < font.height:
            return
            
        num_lines_left   = int((height+line_height-font.height) / line_height)
        lines            = []
        current_ellipses = ''
        mode = self.mode
        ellipses = self.ellipses
        hard = mode == 'hard'

        if num_lines_left == 1 and dim:
            ellipses = ''
            mode = hard = 'hard'
        else:
            dim = False

        string = self.text
        while(num_lines_left):
            # calc each line and put the rest into the next
            if num_lines_left == 1:
                current_ellipses = ellipses
            #
            # __drawstringframed_line__ returns a list:
            # width of the text drawn (w), string which is drawn (s),
            # rest that does not fit (r) and True if the breaking was because
            # of a \n (n)
            #
            (w, s, r, n) = self.__drawstringframed_line__(string, width, font, hard,
                                                          current_ellipses, ' ')
            if s == '' and not hard:
                # nothing fits? Try to break words at ' -_' and no ellipses
                (w, s, r, n) = self.__drawstringframed_line__(string, width, font, hard,
                                                              None, ' -_')
                if s == '':
                    # still nothing? Use the 'hard' way
                    (w, s, r, n) = self.__drawstringframed_line__(string, width, font,
                                                                  'hard', None, ' ')
            lines.append((w, s))
            while r and r[0] == '\n':
                lines.append((0, ' '))
                num_lines_left -= 1
                r = r[1:]
                n = True

            if n:
                string = r
            else:
                string = r.strip()

            num_lines_left -= 1

            if not r:
                # finished, everything fits
                break

        if len(r) == 0 and dim:
            dim = False

        # calc the height we want to draw (based on different align_v)
        height_needed = (len(lines) - 1) * line_height + font.height
        if self.align_v == 'bottom':
            y += (height - height_needed)
        elif self.align_v == 'center':
            y += int((height - height_needed)/2)

        if dim:
            dim = dim_size

        # calculate the position
        y0    = y
        min_x = 10000
        max_x = 0

        for w, l in lines:
            if not l:
                continue
            x0 = x
            if self.align_h == 'right':
                x0 = x + width - w
            elif self.align_h == 'center':
                x0 = x + int((width - w) / 2)
            if x0 < min_x:
                min_x = x0
            if x0 + w > max_x:
                max_x = x0 + w
            y0 += line_height

        # change max_x, min_x, y and height_needed to reflect the
        # changes from shadow
        if shadow_x:
            if shadow_x < 0:
                min_x += shadow_x
            else:
                max_x += shadow_x

        if shadow_y:
            if shadow_y < 0:
                y += shadow_y
                height_needed -= shadow_y
            else:
                height_needed += shadow_y

        # add border radius for each line
        if border_color != None:
            max_x += border_radius
            min_x -= border_radius
            y     -= border_radius
            height_needed += border_radius * 2

        self.render_information = x, y, lines, line_height, shadow_x, shadow_y, \
                                  border_color, border_radius, r, height_needed, dim, \
                                  font, fgcolor, bgcolor, width, shadow_color
        # return rest text and used space
        self.return_value = r, (min_x, y, max_x, y+height_needed)
        return self.return_value


    def __render__(self):
        if not self.render_information:
            self.calculate()

        if not self.render_information:
            return self.text, (self.x1, self.y1, self.x1, self.y1)

        x, y, lines, line_height, shadow_x, shadow_y, border_color, border_radius, \
           rest, height_needed, dim, font, fgcolor, bgcolor, width, \
           shadow_color = self.render_information

        y0    = y
        min_x = 10000
        max_x = 0

        for w, l in lines:
            if not l:
                continue

            x0 = x
            if self.layer:
                try:
                    # render the string. Ignore all the helper functions for that
                    # in here, it's faster because he have more information
                    # in here. But we don't use the cache, but since the skin only
                    # redraws changed areas, it doesn't matter and saves the time
                    # when searching the cache
                    render = font.render(l, fgcolor, bgcolor, border_color,
                                         border_radius, dim)

                    # calc x/y positions based on align
                    if self.align_h == 'right':
                        x0 = x + width - render.get_size()[0]
                    elif self.align_h == 'center':
                        x0 = x + int((width - render.get_size()[0]) / 2)

                    if shadow_x or shadow_y:
                        shadow = font.render(l, shadow_color, dim=dim)
                        self.layer.blit(shadow, (x0+shadow_x, y0+shadow_y))

                    self.layer.blit(render, (x0, y0))

                except Exception, e:
                    print 'Render failed, skipping \'%s\'...' % l
                    print e
                    if config.DEBUG:
                        traceback.print_exc()
                    
            if x0 < min_x:
                min_x = x0
            if x0 + w > max_x:
                max_x = x0 + w
            y0 += line_height

        return self.return_value


            
    def draw(self, rect=None):
        if not self.layer:
            raise TypeError, 'no layer defined for %s' % self
        self.__render__()

        
    def __cmp__(self, o):
        try:
            return self.x1 != o.x1 or self.y1 != o.y1 or self.x2 != o.x2 or \
                   self.y2 != o.y2 or self.text != o.text or self.font != o.font or \
                   self.height != o.height or self.align_h != o.align_h or \
                   self.align_v != o.align_v or self.mode != o.mode or \
                   self.ellipses != o.ellipses or self.dim != o.dim
        except:
            return 1
        

    def modified(self):
        """
        call this function to notify the layer that this object
        needs a redraw
        """
        self.render_information = None
        GUIObject.modified(self)


    def set_position(self, x1, y1, x2, y2):
        """
        change the position (will be done by the layer)
        """
        self.render_information = None
        GUIObject.set_position(self, x1, y1, x2, y2)
