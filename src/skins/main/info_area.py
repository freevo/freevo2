#if 0
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
# Revision 1.2  2003/08/23 12:51:42  dischi
# removed some old CVS log messages
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
#endif

from area import Skin_Area
from skin_utils import *
import xml_skin
import copy
from area import Geometry

import traceback

TRUE  = 1
FALSE = 0


class Info_Area(Skin_Area):
    """
    this call defines the view area
    """

    def __init__( self, parent, screen ):
        Skin_Area.__init__(self, 'info', screen)
        self.last_item = None
        self.content = None
        self.layout_content = None
        self.list = None
        self.updated = 0
        self.sellist = None

        
    def update_content_needed( self ):
        """
        check if the content needs an update
        """
        update = 0
    
        if self.layout_content is not self.layout.content:
            return TRUE

        if self.last_item != self.infoitem:
            return TRUE
        
        update += self.set_content()    # set self.content
        update += self.set_list(update) # set self.list

        list = self.eval_expressions( self.list )
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
            self.sellist = self.eval_expressions( self.list )

        self.last_item = self.infoitem
        if not self.list: # nothing to draw
            self.updated = 0
            return

        # get items to be draw
        list = self.return_formatedtext( self.sellist )

        for i in list:
            if i.y + i.height > self.content.height:
                break
            self.write_text( i.text,
                             i.font, self.content,
                             ( self.content.x + i.x), ( self.content.y + i.y ),
                             i.width , i.height,
                             align_v = i.valign, align_h = i.align,
                             mode = i.mode )    
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
        try:
            if self.content.width != self.area_val.width or \
               self.content.height != self.area_val.height or \
               self.content.x != self.area_val.x or \
               self.content.y != self.area_val.y:
                update=1
        except:
            pass
        
        if self.layout_content is not self.layout.content or update:
            types = self.layout.content.types
            self.content = self.calc_geometry( self.layout.content, copy_object=TRUE )
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

            try:
                val = self.content.types[ key ]
            except:
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
            if b in ( 'and', 'or', 'not' ):
                # valid operator
                exp += ' %s' % ( b )
                
            elif b[ :4 ] == 'len(' and b.find( ')' ) > 0 and \
                     len(b) - b.find(')') < 5:
                # lenght of something
                exp += ' item.getattr("%s") %s' % ( b[ : ( b.find(')') + 1 ) ],
                                                    b[ ( b.find(')') + 1 ) : ])
            else:
                # an attribute
                exp += ' item.getattr("%s")' % b
                
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
            if isinstance( list[ i ], xml_skin.XML_FormatIf ):
                if list[ i ].expression_analized == 0:
                    list[ i ].expression_analized = 1
                    exp = self.get_expression( list[ i ].expression )
                    list[ i ].expression = exp
                else:
                    exp = list[ i ].expression

                # Evaluate the expression:
                try:
                    if exp and eval( exp ):
                        # It's true, we should recurse into children
                        ret_list += self.eval_expressions( list[ i ].content, index + [ i ] )
                except:
                    print "ERROR: Could not evaluate 'if' condition in info_area"
                    print "expression was: 'if %s:', Item was: %s" % ( exp, item.type )
                    traceback.print_exc()
                    
                continue
            
            elif isinstance( list[ i ], xml_skin.XML_FormatText ):
                exp = None
                if list[ i ].expression:
                    if list[ i ].expression_analized == 0:
                        list[ i ].expression_analized = 1
                        exp = self.get_expression( list[ i ].expression )
                        list[ i ].expression = exp
                    else:
                        exp = list[ i ].expression
                    try:
                        # evaluate the expression:
                        if exp:
                            exp = eval( exp )
                            if exp:
                                list[ i ].text = str( exp )
                    except:
                        print "ERROR: Parsing XML in info_area:"
                        print "could not evaluate: '%s'" % ( exp )
                        traceback.print_exc()
                # I add a tuple here to be able to compare lists and know if we need to
                # update, this is useful in the mp3 player
                ret_list += [ index + [ ( i, list[ i ].text ) ] ]
            else:   
                ret_list += [ index + [ i ] ]

        return ret_list





    def return_formatedtext( self, sel_list ):
        """
        receives a list of indexex of elements to be used and
        returns a array with XML_FormatText ready to print (with its elements
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
            if isinstance( element, xml_skin.XML_FormatGotopos ):
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
            # Tag: <newline>
            # 
            elif isinstance( element, xml_skin.XML_FormatNewline ):
                newline = 1 # newline height will be added later
                x = 0
                
            #
            # Tag: <text>
            #
            elif isinstance( element, xml_skin.XML_FormatText ):
                element = copy.copy( element )
                # text position is the current position:
                element.x = x
                element.y = y

                shadow_x, shadow_y = 0, 0
                if element.font.shadow.visible == 'yes':
                    shadow_x = element.font.shadow.x
                    shadow_y = element.font.shadow.y
                    
                # Calculate the geometry
                r = Geometry( x, y, element.width, element.height)
                r = self.get_item_rectangle(r, self.content.width - x - shadow_x,
                                            self.content.height - y - shadow_y )[ 2 ]

                if element.height > 0:
                    height = min(r.height, element.height)
                else:
                    height = -1
                    
                size = osd.drawstringframed( element.text, 0, 0,
                                             r.width, r.height,
                                             element.font.font, None, None,
                                             element.align, element.valign,
                                             element.mode, layer='' )[ 1 ]
                try:
                    m_width  = size[ 2 ] - size[ 0 ]
                    m_height = size[ 3 ] - size[ 1 ]
                except:
                    m_width = r.width
                    m_height = r.height

                if isinstance( element.width, int ):
                    if element.width <= 0:
                        element.width = min( m_width, r.width )
                else:
                    element.width = min( m_width, r.width )

                if isinstance( element.height, int ) or element.height == 'line_height':
                    if element.height <= 0 or element.height == 'line_height':
                        element.height = m_height
                else:
                    element.height = min( m_height, r.height )

                element.width += shadow_x
                element.height += shadow_y

                x += element.width
                ret_list += [ element ]


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
