#if 0 /*
# -----------------------------------------------------------------------
# gphoto.py - Special handling for digi cams through gphoto
# -----------------------------------------------------------------------
# $Id$
#
# Notes: you need gphoto and the python bindings to get this working
#        add plugin.activate('image.gphoto') to your local_conf.py
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/07/14 18:25:17  rshortt
# Minor updates.
#
# Revision 1.1  2003/04/26 15:14:58  dischi
# renamed to gphoto
#
# Revision 1.1  2003/04/18 15:00:39  dischi
# camera (gphoto support) ist now a plugin
#
# Revision 1.1  2003/01/14 18:54:30  dischi
# Added gphoto support from Thomas Schüppel. You need gphoto and the
# Python bindings to get this working. I added try-except to integrate
# this without breaking anything.
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
# ----------------------------------------------------------------------- */
#endif


import menu
import util
import config
from item import Item
import pygame
import _pygphoto as pygphoto
import cStringIO
import image.viewer

import plugin

class PluginInterface(plugin.MainMenuPlugin):

    def detectCameras(self):
        gplist = pygphoto.gp_detectcameras( ) 
        count = pygphoto.gp_list_count( gplist )
        list = []
        while count > 0:
            count = count - 1
            list.append( [pygphoto.gp_name(gplist, count),pygphoto.gp_value(gplist,count)] )
        return list


    def cameraFactory( self, parent, name, port ):
        gCamera = pygphoto.gp_camera( name, port )
        folder = CameraFolder( parent, gCamera, "/", name )
        return folder


    def items(self, parent):
        items = []
        cams = self.detectCameras( )
        for c in cams:
            m = self.cameraFactory( parent, c[0], c[1] )
            m.type = 'camera'
            m.name = c[0]
            items.append(m)
        return items
    


class CameraFile( Item ):
    def __init__(self, parent, gcamera, path, name, duration=0):
        Item.__init__(self, parent)
        self.type = 'image'
        self.url = 'gphoto://%s/%s' % (path,name)
        self.gCamera = gcamera
        self.path = path
        self.name = name
        self.filename = None
        self.image_viewer = image.viewer.get_singleton()
        self.duration = duration
	self.binsexif = {}

    def loadimage(self):
        cfile = pygphoto.gp_getfile( self.gCamera, self.path, self.name )
        string = pygphoto.gp_readfile( cfile )
        file = cStringIO.StringIO( string )
        tmp = pygame.image.load(file)  # XXX Cannot load everything
        return tmp.convert_alpha()  # XXX Cannot load everything

    def copy(self, obj):
        """
        Special copy value DirItem
        """
        Item.copy(self,obj)
        self.gCamera = obj.gCamera
        self.path = obj.path
        self.name = obj.name
        self.image_viewer = obj.image_viewer

    def actions(self):
        """
        Retrieve and Show the Image
        """
        items = [ ( self.view, 'View Image' ) ]
	return items

    def cache(self):
        """
        caches (loads) the next image
        """
        self.image_viewer.cache(self)

    def view(self, arg=None, menuw=None):
        """
        view the image
        """
        self.parent.current_item = self
        self.image_viewer.view(self)



class CameraFolder( Item ):
    def __init__(self, parent, gcamera, path, name ):
        Item.__init__(self, parent)
        self.gCamera = gcamera
        self.path = path
        self.name = name
	self.type = 'folder'

    def copy(self, obj):
        """
        Special copy value DirItem
        """
        Item.copy(self,obj)
        self.gCamera = obj.gCamera
        self.path = obj.path
        self.name = obj.name

    def actions(self):
        items = [ ( self.cwd, 'Browse directory' ) ]
        return items

    def cwd(self, arg=None, menuw=None):
        """
        make a menu item for each file in the directory
        """
        items = []
        parentPath = self.path
        if len(parentPath) == 1:
            parentPath = ""
        print "cwd for" + parentPath
        # Append Folders
        folders = pygphoto.gp_getsubfolders( self.gCamera, self.path )
        number = pygphoto.gp_list_count( folders )
        while number > 0:
            number = number - 1
            name = pygphoto.gp_name( folders, number )
            subFolder = CameraFolder( self, self.gCamera, parentPath + "/" + name, name )
            items.append( subFolder )
        files = pygphoto.gp_getfiles( self.gCamera, self.path )
        number = pygphoto.gp_list_count( files )
        while number > 0:
            number = number - 1
            name = pygphoto.gp_name( files, number )
            subFile = CameraFile( self, self.gCamera, parentPath, name )
            items.append( subFile )
        item_menu = menu.Menu(self.name, items)
        menuw.pushmenu(item_menu)        
        return items
