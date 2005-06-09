# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# infotext.py - A infox text canvas
# -----------------------------------------------------------------------------
# $Id$
#
# This widget can draw expressions from the skin fxd file.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
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

__all__ = [ 'InfoText' ]


# python imports
import logging

# gui imports
from mevas.container import CanvasContainer
from text import Text
from textbox import Textbox


# get logging object
log = logging.getLogger('gui')


class InfoText(CanvasContainer):
    """
    A CanvasContainer for formated text layout. It needs an item and
    and fxd settings parsed expression list to be used on the items attributes.
    """
    def __init__(self, pos, size, item, expression_list, function_calls):
        CanvasContainer.__init__(self)
        self.size = size
        self.item = item
        self.expression_list = expression_list
        self.function_calls  = function_calls
        self.old_content     = None
        self.rebuild()
        self.set_pos(pos)


    def rebuild(self):
        """
        Update the container items to attribute changes
        FIXME: right now, this is a complete redraw
        """
        exp_list = self.__eval(self.item, self.expression_list,
                               self.function_calls)
        if exp_list == self.old_content:
            return
        self.clear()
        if exp_list:
            self.__format(self.size, self.item, exp_list)
        self.old_content = exp_list


    def __getattr(self, attr):
        """
        wrapper for __getitem__ to return the attribute as string or
        an empty string if the value is 'None'
        """
        if attr[:4] == 'len(' and attr[-1] == ')':
            return self.__item[attr]
        r = self.__item[attr]
        if r == None:
            return ''
        return Unicode(r)


    def __eval(self, item, expression_list, function_calls):
        """
        travesse the list evaluating the expressions,
        """
        ret_list = []

        if not expression_list:
            return

        # remember the item for __getattr
        self.__item = item

        for expression in expression_list:
            if expression.type == 'if':
                exp = expression.expression
                # Evaluate the expression:
                try:
                    if exp and eval(exp, {'attr': self.__getattr},
                                    function_calls):
                        # It's true, we should recurse into children
                        ret_list += self.__eval(item, expression.content,
                                                function_calls)
                except Exception, e:
                    log.error('infotext eval error: %s' % e)
                    log.error('expression: %s' % exp)
                    log.error('item: %s' % item)

            elif expression.type == 'text':
                if expression.expression:
                    # evaluate the expression:
                    exp = eval(expression.expression, {'attr': self.__getattr},
                               function_calls)
                    if not isinstance(exp, (str, unicode)):
                        exp = str(exp)
                    if exp:
                        ret_list.append((expression, exp))
                else:
                    ret_list.append((expression, expression.text))
            else:
                ret_list.append((expression, None))

        return ret_list



    def __format(self, size, item, exp_list):
        """
        Use the 'eval'ed list with the expressions to add all needed
        childs to this container
        """
        x = 0
        y = 0

        line_height = 0

        for element, text in exp_list:
            if y >= size[1]:
                # no space left
                return

            #
            # Tag: <goto_pos>
            #
            if element.type == 'goto':
                # move to pos
                if element.mode == 'absolute':
                    if element.x != None:
                        x = element.x
                    if element.y != None:
                        y = element.y
                else: # relative
                    if element.x != None:
                        x += element.x
                    if element.y != None:
                        y = y + element.y
            #
            # Tag: <img>
            #
            elif element.type == 'image':
                log.error('FIXME: image tag not supported by infotext')

            #
            # Tag: <newline>
            #
            elif element.type == 'newline':
                x = 0
                y = y + line_height
                line_height = 0

            #
            # Tag: <text>, one line text
            #
            elif element.type == 'text' and element.height == -1:
                font = element.font
                w = element.width
                if isinstance(w, str):
                    w = int(eval(w, {'MAX': (size[0] - x)}))
                elif w == 0:
                    # use the complete free space
                    w = size[0] - x
                else:
                    w = min(w, size[0] - x)
                if w > 0:
                    t = Text(text, (x,y), (w, font.height), font,
                             element.align, element.valign,
                             element.mode, element.ellipses, element.dim)
                    if y + t.get_size()[1] <= size[1]:
                        self.add_child(t)
                    line_height = max(line_height, t.get_size()[1])
                    if element.width == 0:
                        # flow text
                        x += t.get_size()[0]
                    else:
                        x += w

            #
            # Tag: <text> as textbox
            #
            elif element.type == 'text':
                font = element.font
                w = element.width
                h = element.height
                if isinstance(w, str):
                    w = int(eval(w, {'MAX': size[0]}))
                elif w == 0:
                    # use the complete free space
                    w = size[0] - x
                if isinstance(h, str):
                    h = min(int(eval(h, {'MAX': size[1]})), (size[1] - y))
                elif h == 0:
                    # use the complete free space
                    h = size[1] - y
                t = Textbox(text, (x,y), (w, h), font,
                            element.align, element.valign,
                            element.mode, element.ellipses)
                self.add_child(t)
                line_height = max(line_height, t.get_size()[1])
                x += t.get_size()[0]
                y += t.get_size()[1] - line_height
