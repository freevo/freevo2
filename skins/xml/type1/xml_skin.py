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
# Revision 1.2  2002/08/19 05:52:08  krister
# Changed to Gustavos new XML code for more settings in the skin. Uses columns for the TV guide.
#
# Revision 1.2  2002/08/18 06:12:57  krister
# Added load font with extension.
#
# Revision 1.1  2002/08/17 02:55:45  krister
# Submitted by Gustavo Barbieri.
#
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
import sys
import socket
import random
import time
import os
import copy
import re
import traceback

# XML support
from xml.utils import qp_xml


# XXX Shouldn't this be moved to the config file?

OSD_FONT_DIR = 'skins/fonts/'
OSD_DEFAULT_FONT = 'skins/fonts/arialbd.ttf'



#
# data structures
#

class XML_data:
    color = bgcolor = 0
    x = y = 0
    height = width = 0
    size = length = 0
    visible = 1
    text = None
    font = OSD_DEFAULT_FONT
    mode=''
    shadow_mode = ''
    shadow_visible = 0
    shadow_color = 0
    shadow_pad_x = shadow_pad_y = 1
    border_color = 0
    border_size = 0

class XML_menuitem(XML_data):
    selection = XML_data()

    
    
class XML_menu:
    bgbitmap = ''
    title = XML_data()
    items = XML_menuitem()
    item_dir = XML_menuitem()
    item_pl = XML_menuitem()
    item_main = XML_menuitem()    
    cover_movie = XML_data()
    cover_music = XML_data()
    cover_image = XML_data()
    submenu = XML_menuitem()

    
class XML_mp3:
    bgbitmap = ''
    progressbar = XML_data()
    shadow = XML_data()
    font = XML_data()
    title = XML_data()    
    
class XML_mainmenuitem:
    name = ''
    visible = 1
    icon = ''
    pos = 0
    action = None
    arg = None

class XML_mainmenu:
    items = []
    
class XMLSkin:
    menu = XML_menu()
    mp3  = XML_mp3()
    mainmenu = XML_mainmenu()
    
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

    def attr_str(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            return node.attrs[('', attr)]
        return default

    def attr_font(self, node, attr, default):
        if node.attrs.has_key(('', attr)):
            fontext = os.path.splitext(node.attrs[('', attr)])[1]
            if fontext:
                # There is an extension (e.g. '.pfb'), use the full name
                font = os.path.join(OSD_FONT_DIR, node.attrs[('', attr)]).encode()
            else:
                # '.ttf' is the default extension
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
        data.length = self.attr_int(node, "length", data.length)
        data.visible = self.attr_bool(node, "visible", data.visible)
        data.bgcolor = self.attr_hex(node, "bgcolor", data.bgcolor)
        data.color = self.attr_hex(node, "color", data.color) # will be overrided by font
        for subnode in node.children:
            if subnode.name == u'font':
                data.color = self.attr_hex(subnode, "color", data.color)
                data.size = self.attr_int(subnode, "size", data.size)
                data.font = self.attr_font(subnode, "name", data.font)
            if subnode.name == u'selection':
                data.selection = copy.copy(data.selection)
                self.parse_node(subnode, data.selection)
            if subnode.name == u'text':
                data.text = subnode.textof()
            if subnode.name == u'shadow':
                data.shadow_visible = self.attr_bool(subnode, "visible", data.shadow_visible)
                data.shadow_color = self.attr_hex(subnode, "color", data.shadow_color)
                data.shadow_mode = self.attr_str(subnode, "mode", data.shadow_mode)
                data.shadow_pad_x = self.attr_int(subnode, "x", data.shadow_pad_x)
                data.shadow_pad_y = self.attr_int(subnode, "y", data.shadow_pad_y)
                
                

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

            elif node.name == u'item_dir':
                if copy_content: self.menu.item_dir = copy.copy(self.menu.item_dir)
                self.parse_node(node, self.menu.item_dir)

            elif node.name == u'item_pl':
                if copy_content: self.menu.item_pl = copy.copy(self.menu.item_pl)
                self.parse_node(node, self.menu.item_pl)

            elif node.name == u'item_main':
                if copy_content: self.menu.item_main = copy.copy(self.menu.item_main)
                self.parse_node(node, self.menu.item_main)

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
    # parse one mp3 node
    #
    def parse_mp3node(self, node, data):
        data.x = self.attr_int(node, "x", data.x)
        data.y = self.attr_int(node, "y", data.y)
        data.height = self.attr_int(node, "height", data.height)
        data.width = self.attr_int(node, "width", data.width)
        data.visible = self.attr_bool(node, "visible", data.visible)
        data.mode = self.attr_str(node, "mode", data.mode)
        data.bgcolor = self.attr_hex(node, "bgcolor", data.bgcolor)
        data.color = self.attr_hex(node, "color", data.color)
        data.border_color = self.attr_hex(node, "border_color", data.border_color)
        data.border_size = self.attr_int(node, "border_size", data.border_size)


    #
    # read the skin informations for the mp3 player
    #
    def read_mp3(self, file, menu_node, copy_content):
        if copy_content: self.mp3 = copy.copy(self.mp3)
        for node in menu_node.children:
            if node.name == u'bgbitmap':
                self.mp3.bgbitmap = os.path.join(os.path.dirname(file), node.textof())

            elif node.name == u'title':
                if copy_content: self.mp3.title = copy.copy(self.mp3.title)
                self.parse_node(node, self.mp3.title)

            elif node.name == u'shadow':
                if copy_content: self.mp3.shadow = copy.copy(self.mp3.shadow)
                self.parse_mp3node(node, self.mp3.shadow)

            elif node.name == u'progressbar':
                if copy_content: self.mp3.progressbar = copy.copy(self.mp3.progressbar)
                self.parse_mp3node(node, self.mp3.progressbar)

            elif node.name == u'font':
                if copy_content: self.mp3.font = copy.copy(self.mp3.font)
                self.mp3.font.font = self.attr_font(node, "name", self.mp3.font.font)
                self.mp3.font.color = self.attr_hex(node, "color", self.mp3.font.color)
                self.mp3.font.size = self.attr_int(node, "size", self.mp3.font.size)


    #
    # parse one main menu node
    #
    def parse_mainmenunode(self, node, data):
        data.name = self.attr_str(node, "name", data.name)
        data.visible = self.attr_bool(node, "visible", data.visible)
        data.icon = self.attr_str(node, "icon", data.icon)
        data.pos = self.attr_int(node, "pos", data.pos)
        data.action = self.attr_str(node,"action", data.action)
        data.arg = self.attr_str(node,"arg", data.arg)

    #
    # read the main menu
    #
    def read_mainmenu(self, file, menu_node, copy_content):
        if copy_content: self.mainmenu = copy.copy(self.mainmenu)
        for node in menu_node.children:
            if node.name == u'item':
                item = XML_mainmenuitem()
                if copy_content:
                    item = copy.copy(item)
                    self.mainmenu.items = copy.copy(self.mainmenu.items)
                self.parse_mainmenunode(node, item)
                self.mainmenu.items.insert(item.pos,item)                


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
                    if node.name == u'main':
                        self.read_mainmenu(file, node, copy_content)
                    
        except:
            print "ERROR: XML file corrupt"
            traceback.print_exc()
         
