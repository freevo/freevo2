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
# Revision 1.3  2002/12/02 18:25:22  dischi
# Added bins/exif patch from John M Cooper
#
# Revision 1.2  2002/11/26 16:28:10  dischi
# added patch for better bin support
#
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

class BinsDiscription(ContentHandler):
    """
    This is a handler for getting the information from a bins Album.
    """
    def __init__(self):
        self.desc = {}
	self.exif = {}
        self.inDisc = 0
        self.inField = 0
	self.inExif = 0
	self.inTag = 0


    def startElement(self,name,attrs):
        # Check that we  have a discription section
        if name == u'description':
            self.inDisc = 1
        if name == u'field':
            self.thisField = normalize_whitespace(attrs.get('name', ''))
            self.inField = 1
            self.desc[self.thisField] = ''
	if name == u'exif':
	    self.inExif = 1
	if name == u'tag':
	    self.inTag = 1
	    self.thisTag = normalize_whitespace(attrs.get('name', ''))
	    self.exif[self.thisTag] = ''


    def characters(self,ch):
        if self.inDisc:
            if self.inField:
                self.desc[self.thisField] = self.desc[self.thisField] + ch
        if self.inExif:
	    if self.inTag:
	        self.exif[self.thisTag] = self.exif[self.thisTag] + ch

 
    def endElement(self,name):
        if name == 'discription':
            self.inDisc = 0
        if name == 'field':
            self.inField = 0
	if name == 'exif':
	    self.inExif = 0
	if name == 'tag':
	    self.inTag = 0

def get_bins_desc(binsname):
     parser = make_parser()
     parser.setFeature(feature_namespaces,0)
     dh = BinsDiscription()
     parser.setContentHandler(dh)
     # check that the xml file exists for a dir or image
     if os.path.isfile(binsname + '/album.xml'):
         binsname = binsname + '/album.xml'
     elif os.path.isfile(binsname + '.xml'):
         binsname = binsname + '.xml'
     else:
         dh.desc['title'] == os.path.basename(dirname)

     # Check that there is a title
     parser.parse(binsname)

     return {'desc':dh.desc , 'exif':dh.exif}


if __name__ == '__main__':
    parser = make_parser()
    parser.setFeature(feature_namespaces,0)
    dh = GetAlbum()
    parser.setContentHandler(dh)
    parser.parse('album.xml')
    print dh.desc
