# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# infotext.py - A text canvas
# -----------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.5  2004/11/20 18:23:02  dischi
# use python logger module for debug
#
# Revision 1.4  2004/10/05 19:50:55  dischi
# Cleanup gui/widgets:
# o remove unneeded widgets
# o move window and boxes to the gui main level
# o merge all popup boxes into one file
# o rename popup boxes
#
# Revision 1.3  2004/08/27 14:16:10  dischi
# do not draw outside the given size
#
# Revision 1.2  2004/08/23 15:11:50  dischi
# avoid redraw when not needed
#
# Revision 1.1  2004/08/22 20:06:21  dischi
# Switch to mevas as backend for all drawing operations. The mevas
# package can be found in lib/mevas. This is the first version using
# mevas, there are some problems left, some popup boxes and the tv
# listing isn't working yet.
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

import config

from mevas.container import CanvasContainer
from text import Text
from textbox import Textbox

import logging
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
        
        
    def __eval(self, item, expression_list, function_calls):
        """
        travesse the list evaluating the expressions,
        """
        ret_list = []

        if not expression_list:
            return

        for i in range(len(expression_list)):
            if expression_list[i].type == 'if':
                exp = expression_list[i].expression
                # Evaluate the expression:
                try:
                    if exp and eval(exp, {'attr': item.getattr},
                                    function_calls):
                        # It's true, we should recurse into children
                        ret_list += self.__eval(item,
                                                expression_list[i].content,
                                                function_calls)
                except Exception, e:
                    print 'infotext eval error: %s', e
                    print 'expression:', exp
                    print 'item:      ', item
                    
            elif expression_list[i].type == 'text':
                if expression_list[i].expression:
                    # evaluate the expression:
                    exp = eval(expression_list[i].expression,
                               {'attr': item.getattr}, function_calls)
                    if not isstring(exp):
                        exp = str(exp)
                    if exp:
                        ret_list.append((expression_list[i], exp))
                else:
                    ret_list.append((expression_list[i],
                                     expression_list[i].text))
            else:
                ret_list.append((expression_list[i], None))

        return ret_list



    def __format(self, size, item, exp_list):
        """
        Use the 'eval'ed list with the expressions to add all needed
        childs to this conatiner
        """
        x = 0
        y = 0

        line_height = 0
        
        for element, text in exp_list:
            if y >= size[1]:
                return
            
            newline = 0

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
                log.info('FIXME: image tag not supported by infotext')

            #
            # Tag: <newline>
            #
            elif element.type == 'newline':
                x = 0
                y = y + line_height
                line_height = 0

            #
            # Tag: <text>
            #
            elif element.type == 'text':
                font = element.font
                if element.height == -1:
                    # simple text
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
                    else:
                        if config.DEBUG > 2:
                            print 'infotext warning: drawing text on negative'
                            print 'position width=%s' % w
                            print 'text:', text
                            print 'elem:', element.width
                else:
                    # text box
                    w = element.width
                    h = element.height
                    if isinstance(w, str):
                        w = int(eval(w, {'MAX': size[0]}))
                    elif w == 0:
                        # use the complete free space
                        w = size[0] - x
                    if isinstance(h, str):
                        h = min(int(eval(h, {'MAX': size[1]})), size[1])
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
