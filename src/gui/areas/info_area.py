# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------
# info_area.py - An info area for the Freevo skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2004/07/24 12:21:31  dischi
# use new renderer and screen features
#
# Revision 1.1  2004/07/22 21:13:39  dischi
# move skin code to gui, update to new interface started
#
# Revision 1.24  2004/07/10 12:33:41  dischi
# header cleanup
#
# Revision 1.23  2004/06/02 19:04:35  dischi
# translation updates
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


import copy
import util
import re

from area import Skin_Area
from skin_utils import *
import gui.fxdparser as fxdparser
from area import Geometry

import traceback

# function calls to get more info from the skin
function_calls = { 'comingup': util.comingup }

class Info_Area(Skin_Area):
    """
    this call defines the view area
    """

    def __init__(self):
        Skin_Area.__init__(self, 'info')
        self.last_item = None
        self.content = None
        self.layout_content = None
        self.list = None
        self.updated = 0
        self.sellist = None
        self.i18n_re = re.compile('^( ?)(.*?)([:,]?)( ?)$')

    def update_content_needed( self ):
        """
        check if the content needs an update
        """
        update = 0

        if self.layout_content is not self.layout.content:
            return True

        if self.last_item != self.infoitem:
            return True

        update += self.set_content()    # set self.content
        update += self.set_list(update) # set self.list

        try:
            list = self.eval_expressions( self.list )
        except:
            print "skin error: unable to parse expression in info_area"
            traceback.print_exc()
            return 0
        
        if self.sellist  != list:
            self.sellist = list
            update += 1

        if update:
            self.updated = 1
        return update


    def update_content( self ):
        """
        update the info area
        """
        if not self.updated: # entered a menu for the first time
            self.set_list(self.set_content())
            try:
                self.sellist = self.eval_expressions( self.list )
            except:
                print "skin error: unable to parse expression in info_area"
                traceback.print_exc()
                return 0

        self.last_item = self.infoitem
        if not self.list: # nothing to draw
            self.updated = 0
            return

        # get items to be draw
        list = self.return_formatedtext( self.sellist )

        for i in list:
            if isinstance( i, fxdparser.FormatText ):
                if i.y + i.height > self.content.height:
                    break
                self.drawstring( i.text,
                                 i.font, self.content,
                                 ( self.content.x + i.x), ( self.content.y + i.y ),
                                 i.width , i.height,
                                 align_v = i.valign, align_h = i.align,
                                 mode = i.mode,
                                 ellipses = i.ellipses,
                                 dim = i.dim )

            elif isinstance( i, fxdparser.FormatImg ):
                if i.src:
                    tmp = ( self.content.x + i.x, self.content.y + i.y,
                            i.width, i.height )
                    self.drawimage( i.src, tmp )
                else:
                    print String(_( "ERROR" )) + ": " + String(_("missing 'src' attribute in skin tag!"))


        self.last_item = self.infoitem

        # always set this to 0 because we don't call update_content
        # when everything changes
        self.updated = 0


    def set_content( self ):
        """
        set self.content and self.layout_content if they need to be set (return 1)
        or does nothing (return 0)
        """
        update=0
        if self.content and self.area_val and \
               (self.content.width != self.area_val.width or \
                self.content.height != self.area_val.height or \
                self.content.x != self.area_val.x or \
                self.content.y != self.area_val.y):
            update=1

        if self.layout_content is not self.layout.content or update:
            types = self.layout.content.types
            self.content = self.calc_geometry( self.layout.content, copy_object=True )
            # backup types, which have the previously calculated fcontent
            self.content.types = types
            self.layout_content = self.layout.content
            return 1
        return 0


    def set_list( self, force = 0 ):
        """
        set self.list if need (return 1) or does nothing (return 0)
        """
        if force or self.infoitem is not self.last_item or self.infoitem != self.last_item:
            key = 'default'
            if hasattr( self.infoitem, 'info_type'):
                key = self.infoitem.info_type or key

            elif hasattr( self.infoitem, 'type' ):
                key = self.infoitem.type or key

            if self.content.types.has_key(key):
                val = self.content.types[ key ]
            else:
                val = self.content.types[ 'default' ]

            if not hasattr( val, 'fcontent' ):
                self.list = None
                return 1

            self.list = val.fcontent
            return 1

        return 0



    def get_expression( self, expression ):
        """
        create the python expression
        """
        exp = ''
        for b in expression.split( ' ' ):
            if b in ( 'and', 'or', 'not', '==', '!=' ):
                # valid operator
                exp += ' %s' % ( b )

            elif b.startswith('\'') and b.endswith('\''):
                # string
                exp += ' %s' % ( b )
                
            elif b.startswith('function:'):
                exp += ' %s()' % b[9:]
                
            elif b[ :4 ] == 'len(' and b.find( ')' ) > 0 and \
                     len(b) - b.find(')') < 5:
                # lenght of something
                exp += ' attr("%s") %s' % ( b[ : ( b.find(')') + 1 ) ],
                                                    b[ ( b.find(')') + 1 ) : ])
            else:
                # an attribute
                exp += ' attr("%s")' % b

        return exp.strip()




    def eval_expressions( self, list, index = [ ] ):
        """
        travesse the list evaluating the expressions,
        return a flat list with valid elements indexes only
        (false 'if' expressions eliminated). Also, text elements
        are in the list too in a tuple:
           ( index, 'text value' )
        so you can check if it changed just comparing two lists
        (useful in music player, to update 'elapsed')
        """
        item = self.infoitem
        ret_list = [ ]

        if not list:
            return

        rg = range( len( list ) )
        for i in rg:
            if isinstance( list[ i ], fxdparser.FormatIf ):
                if list[ i ].expression_analized == 0:
                    list[ i ].expression_analized = 1
                    exp = self.get_expression( list[ i ].expression )
                    list[ i ].expression = exp
                else:
                    exp = list[ i ].expression

                # Evaluate the expression:
                if exp and eval(exp, {'attr': item.getattr}, function_calls):
                    # It's true, we should recurse into children
                    ret_list += self.eval_expressions( list[ i ].content, index + [ i ] )
                continue

            elif isinstance( list[ i ], fxdparser.FormatText ):
                exp = None
                if list[ i ].expression:
                    if list[ i ].expression_analized == 0:
                        list[ i ].expression_analized = 1
                        exp = self.get_expression( list[ i ].expression )
                        list[ i ].expression = exp
                    else:
                        exp = list[ i ].expression
                    # evaluate the expression:
                    if exp:
                        exp = eval(exp, {'attr': item.getattr}, function_calls)
                        if not isstring(exp):
                            exp = str( exp )
                        if exp:
                            list[ i ].text = exp
                else:
                    # translate the text in the FormatText
                    if list[ i ].expression_analized == 0:
                        # not translated yet
                        list[ i ].expression_analized = 1
                        m = self.i18n_re.match(list[i].text).groups()
                        # translate
                        list[i].text = m[0] + _(m[1]) + m[2] + m[3]
                # I add a tuple here to be able to compare lists and know if we need to
                # update, this is useful in the mp3 player
                ret_list += [ index + [ ( i, list[ i ].text ) ] ]
            else:
                ret_list += [ index + [ i ] ]

        return ret_list





    def return_formatedtext( self, sel_list ):
        """
        receives a list of indexex of elements to be used and
        returns a array with FormatText ready to print (with its elements
        x, y, width and height already calculated)
        """
        x, y = 0, 0

        item = self.infoitem

        list = self.list
        ret_list = [ ]
        last_newline = 0 # index of the last line
        for i in sel_list:
            newline = 0

            # find the element
            element = self.list
            for j in range( len( i ) - 1 ):
                element = element[ i[ j ] ].content
            if isinstance( i[ -1 ], tuple ):
                element = element[ i[ -1 ][ 0 ] ]
            else:
                element = element[ i[ -1 ] ]

            #
            # Tag: <goto_pos>
            #
            if isinstance( element, fxdparser.FormatGotopos ):
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
            elif isinstance( element, fxdparser.FormatImg ):
                # Image is a float object
                if element.x == None:
                    element.x = x

                if element.y == None:
                    element.y = y
                else:
                    my_y = y

                if element.width == None or element.height == None:
                    image = self.screen.renderer.loadbitmap( element.src, True )
                    size = image.get_size()

                    if element.width == None:
                        element.width = size[ 0 ]

                    if element.height == None:
                        element.height = size[ 1 ]

                ret_list += [ element ]

            #
            # Tag: <newline>
            #
            elif isinstance( element, fxdparser.FormatNewline ):
                newline = 1 # newline height will be added later
                x = 0

            #
            # Tag: <text>
            #
            elif isinstance( element, fxdparser.FormatText ):
                element = copy.copy( element )
                # text position is the current position:
                element.x = x
                element.y = y

                # Calculate the geometry
                r = Geometry( x, y, element.width, element.height)
                r = self.get_item_rectangle(r, self.content.width - x,
                                            self.content.height - y )[ 2 ]
                if element.height > 0:
                    height = min(r.height, element.height)
                else:
                    height = -1

                size = self.screen.renderer.drawstringframed( element.text, 0, 0,
                                             r.width, r.height,
                                             element.font, None, None,
                                             element.align, element.valign,
                                             element.mode, ellipses=element.ellipses,
                                             dim=element.dim, layer='' )[ 1 ]
                m_width  = size[ 2 ] - size[ 0 ]
                m_height = size[ 3 ] - size[ 1 ]

                if isinstance( element.width, int ):
                    if element.width <= 0:
                        element.width = min( m_width, r.width )
                elif element.align == 'left':
                    element.width = min( m_width, r.width )
                else:
                    element.width = r.width
                    
                if isinstance( element.height, int ) or element.height == 'line_height':
                    if element.height <= 0 or element.height == 'line_height':
                        element.height = m_height
                else:
                    element.height = min( m_height, r.height )

                x += element.width
                ret_list.append(element)


            # We should shrink the width and go next line (overflow)
            if x > self.content.width:
                x = 0
                newline = 1
                element.width = self.content.width - element.x


            # Need to recalculate line height?
            if newline and ret_list:
                newline_height = 0
                # find the tallest string
                new_last_newline = len( ret_list )
                last_line = ret_list[ last_newline : new_last_newline ]
                for j in last_line:
                    if isinstance( j, fxdparser.FormatText ):
                        font = j.font
                        if j.text and j.height > newline_height:
                            newline_height = j.height

                y = y + newline_height
                last_newline = new_last_newline
                # update the height of the elements in this line,
                # so vertical alignment will be respected
                for j in last_line:
                    j.height = newline_height


        return ret_list
