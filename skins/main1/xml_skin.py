#if 0
# -----------------------------------------------------------------------
# xml_skin.py - XML reader for the skin
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/08/11 08:11:03  dischi
# moved the XML parsing to an extra file and the file 768x576.xml
# to the directory skins/xml
#
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



# some python stuff
import sys, socket, random, time, os, copy, re

# XML support
from xml.utils import qp_xml


# XXX Shouldn't this be moved to the config file?

OSD_FONT_DIR = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/SF Arborcrest Medium.ttf'



#
# data structures
#

class XML_data:
    color = sel_color = 0
    x = y = height = width = size = sel_length = 0
    visible = 1
    text = None
    font = OSD_DEFAULT_FONT
    
    
class XML_menu:
    bgbitmap = ''
    title = XML_data()
    items = XML_data()
    cover_movie = XML_data()
    cover_music = XML_data()
    cover_image = XML_data()
    submenu = XML_data()
    
class XML_mp3:
    bgbitmap = ''




class XMLSkin:


    menu = XML_menu()
    mp3  = XML_mp3()

    #
    # Help functions
    #
    def attr_int(self, node, attr, default):
        try:
            if node.attrs.has_key(('', attr)):
                return int(node.attrs[('', attr)])
        except ValueError:
            pass
        return default

    def attr_hex(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            return int(node.attrs[('', attr)], 16)
        return default

    def attr_bool(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            if node.attrs[('', attr)] == "yes":
                return 1
            elif node.attrs[('', attr)] == "no":
                return 0
        return default

    def attr_font(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] + '.ttf').encode()
            if not os.path.isfile(font):
                font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)] + '.TTF')
            if not font:
                print "can find font >%s<" % font
                font = OSD_DEFAULT_FONT
            return font
        return default



    #
    # parse one node
    #
    def parse_node(self, node, data):
        data.x = self.attr_int(node, "x", data.x)
        data.y = self.attr_int(node, "y", data.y)
        data.height = self.attr_int(node, "height", data.height)
        data.width = self.attr_int(node, "width", data.width)
        data.visible = self.attr_bool(node, "visible", data.visible)

        for subnode in node.children:
            if subnode.name == u'font':
                data.color = self.attr_hex(subnode, "color", data.color)
                data.size = self.attr_int(subnode, "size", data.size)
                data.font = self.attr_font(subnode, "name", data.font)
            if subnode.name == u'selection':
                data.sel_color = self.attr_hex(subnode, "color", data.sel_color)
                data.sel_length = self.attr_int(subnode, "length", data.sel_length)
            if subnode.name == u'text':
                data.text = subnode.textof()


    #
    # read the skin informations for menu
    #
    def read_menu(self, file, menu_node, copy_content):
        if copy_content: self.menu = copy.copy(self.menu)
        for node in menu_node.children:

            if node.name == u'bgbitmap':
                self.menu.bgbitmap = os.path.join(os.path.dirname(file), node.textof())

            elif node.name == u'title':
                if copy_content: self.menu.title = copy.copy(self.menu.title)
                self.parse_node(node, self.menu.title)

            elif node.name == u'items':
                if copy_content: self.menu.items = copy.copy(self.menu.items)
                self.parse_node(node, self.menu.items)

            elif node.name == u'cover':
                for subnode in node.children:
                    if subnode.name == u'movie':
                        if copy_content:
                            self.menu.cover_movie = copy.copy(self.menu.cover_movie)
                        self.parse_node(subnode, self.menu.cover_movie)
                    if subnode.name == u'music':
                        if copy_content:
                            self.menu.cover_music = copy.copy(self.menu.cover_music)
                        self.parse_node(subnode, self.menu.cover_music)
                    if subnode.name == u'image':
                        if copy_content:
                            self.menu.cover_image = copy.copy(self.menu.cover_image)
                        self.parse_node(subnode, self.menu.cover_image)

            elif node.name == u'submenu':
                if copy_content: self.menu.submenu = copy.copy(self.menu.submenu)
                self.parse_node(node, self.menu.submenu)



    #
    # read the skin informations for the mp3 player
    #
    def read_mp3(self, file, menu_node, copy_content):
        if copy_content: self.mp3 = copy.copy(self.mp3)
        for node in menu_node.children:
            if node.name == u'bgbitmap':
                self.mp3.bgbitmap = os.path.join(os.path.dirname(file), node.textof())


    #
    # parse the skin file
    #
    def load(self, file, copy_content = 0):
        try:
            parser = qp_xml.Parser()
            box = parser.parse(open(file).read())
            if box.children[0].name == 'skin':
                for node in box.children[0].children:
                    if node.name == u'menu':
                        self.read_menu(file, node, copy_content)
                    if node.name == u'mp3':
                        self.read_mp3(file, node, copy_content)
        except:
            print "ERROR: XML file corrupt"
            
