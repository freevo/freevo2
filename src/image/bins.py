#if 0 /*
# -----------------------------------------------------------------------
# bins.py - Python interface to bins data files.
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.1  2002/11/24 13:58:45  dischi
# code cleanup
#
#
# -----------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002 Krister Lagerstrom, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This file Copyright (C) 2002 John Cooper
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


from xml.sax import make_parser, ContentHandler
from xml.sax.handler import feature_namespaces
import string
import os

def normalize_whitespace(text):
    # Remove Redundant whitespace from a string
    return ' '.join(text.split())

class GetAlbum(ContentHandler):
    """
    This is a handler for getting the information from a bins Album.
    """
    def __init__(self):
        self.desc = {}
        self.inDisc = 0
        self.inField = 0

    def startElement(self,name,attrs):
        # Check that we  have a discription section
        if name == u'description':
            self.inDisc = 1
        if name == u'field':
            self.thisField = normalize_whitespace(attrs.get('name', ''))
            self.inField = 1
            self.desc[self.thisField] = ""

    def characters(self,ch):
        if self.inDisc:
            if self.inField:
                self.desc[self.thisField] = self.desc[self.thisField] + ch

 
    def endElement(self,name):
        if name == 'discription':
            self.inDisc = 0
        if name == 'field':
            self.inField = 0

def get_album_title(dirname):
     parser = make_parser()
     parser.setFeature(feature_namespaces,0)
     dh = GetAlbum()
     parser.setContentHandler(dh)
     parser.parse(dirname + '/album.xml')
     # Check that there is a title
     if dh.desc['title'] == '':
         dh.desc['title'] = os.path.basename(dirname)
     return dh.desc['title']

if __name__ == '__main__':
    parser = make_parser()
    parser.setFeature(feature_namespaces,0)
    dh = GetAlbum()
    parser.setContentHandler(dh)
    parser.parse('album.xml')
    print dh.desc
