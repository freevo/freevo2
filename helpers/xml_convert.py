#!/usr/bin/env python

#if 0 /*
#-------------------------------------------------------------------------
# xml_convert.py - Converts old XML format into the new one
#-------------------------------------------------------------------------
# $Id$
#
# Notes:
# Todo: more testing
#
#-------------------------------------------------------------------------
# $Log$
# Revision 1.2  2003/02/19 08:03:38  krister
# Changed the program to accept a list of XML-filenames to convert.
#
# Revision 1.1  2003/02/12 10:30:57  dischi
# Script to convert old xml files to the new fxd format
#
# Revision 1.1  2003/02/08 12:08:07  dischi
# Script to convert the old xml files into the new format. The new suffix
# is fxd (Freevo Xml Data). You can convert all your files and try the
# patch. If you reverse the patch, freevo still works because of the new
# suffix
#
#
#-------------------------------------------------------------------------
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
#-------------------------------------------------------------------------*/
#endif

from xml.utils import qp_xml

import os
import sys
import re
import codecs


skin = ''

def xml_parseVideo(video_node, result):
    result['dvd'] = None
    result['vcd'] = None
    result['cd'] = None
    result['mplayer-options'] = None
    result['files'] = []
    for node in video_node.children:
        if node.name == u'dvd':
            result['dvd'] = 1
        elif node.name == u'vcd':
            result['vcd'] = 1
        elif node.name == u'cd':
            result['cd'] = 1
        elif node.name == u'mplayer_options':
            result['mplayer-options'] = node.textof()
        elif node.name == u'files':
            for file_nodes in node.children:
                if file_nodes.name == u'filename' and not file_nodes.textof() == '-cd':
                    result['files'] += [ file_nodes.textof() ]



def xml_parseInfo(info_node, i): 
    for node in info_node.children:
        if node.name == u'url':
            i['url'] = node.textof()
        elif node.name == u'genre':
            i['genre'] = node.textof()
        elif node.name == u'runtime':
            i['runtime'] = node.textof()
        elif node.name == u'tagline':
            i['tagline'] = node.textof()
        elif node.name == u'plot':
            i['plot'] = node.textof()
        elif node.name == u'year':
            i['year'] = node.textof()
        elif node.name == u'rating':
            i['rating'] = node.textof()



def parse_file(file, tree):
    try:
        parser = qp_xml.Parser()
        # Let's name node variables after their XML names
        freevo = parser.parse(open(file).read())
    except:
        print "XML file %s corrupt" % file
        return []
    
    for freevo_child in freevo.children:
        if freevo_child.name == u'copyright':
            tree['copyright'] = freevo_child.textof()
        elif freevo_child.name == u'movie':
            m = {}
            m['video'] = {}
            m['info'] = {}
            m['cover'] = {}
            m['id'] = []
            m['label'] = []
            m['title'] = ''
            
            for movie_child in freevo_child.children:
                if movie_child.name == u'title':
                    m['title'] = movie_child.textof()
                elif movie_child.name == u'cover':
                    m['cover']['text-data'] = movie_child.textof()
                    m['cover']['source'] = None
                    try:
                        m['cover']['source'] = movie_child.attrs[('',u'source')]
                    except KeyError:
                        pass
                elif movie_child.name == u'video':
                    xml_parseVideo(movie_child, m['video'])
                elif movie_child.name == u'info':
                    xml_parseInfo(movie_child, m['info'])
                elif movie_child.name == u'id':
                    m['id'] += [ movie_child.textof() ]
                elif movie_child.name == u'label':
                    m['label'] += [ movie_child.textof() ]

            tree['movie'] += [ m ]

            
def print_tree(filename, t):
    i = codecs.open(filename, 'w', encoding='utf-8')
    
    i.write ('<?xml version="1.0" ?>\n')
    i.write('<freevo>\n')
    idnum=1
    for movie in t['movie']:
        if (not movie['video'] or not movie['video']['files']) and (movie['id'] or movie['label']):
            # XML file was about identifying a set of CDs
            if movie['title']:
                i.write('  <disc-set title="%s">\n' % movie['title'])
            else:
                i.write('  <disc-set>\n')
            for id in movie['id']:
                i.write('    <disc media-id="%s"/>\n' % (id))
            for l in movie['label']:
                i.write('    <disc label-regexp="%s"/>\n' % (l))
            if movie['cover']:
                i.write('    <cover-img source="%s">%s</cover-img>\n' % (movie['cover']['source'], movie['cover']['text-data']))
            if movie['info']:
                i.write('    <info>\n')
                for k in movie['info'].keys():
                    i.write('      <%s>%s</%s>\n' % (k,movie['info'][k],k))
                i.write('    </info>\n')
            i.write('  </disc-set>\n')
        else:
            # XML file was about a movie
            i.write('  <movie ')
            if movie['title']:
                i.write('title="%s"' % (movie['title'])),
            i.write('>\n')
            if movie['cover']:
                i.write('    <cover-img ')
                if movie['cover']['source']:
                    i.write('source="%s"' % movie['cover']['source'])
                i.write('>%s</cover-img>\n' % movie['cover']['text-data'])
            i.write('    <video')
            if movie['video']['mplayer-options']:
                i.write('mplayer-options="%s"' % (movie['video']['mplayer-options'])),
            i.write('>\n')
            for f in movie['video']['files']:
                tag = ""
                if movie['video']['dvd']:
                    tag = "dvd"
                elif movie['video']['vcd']:
                    tag = "vcd"
                else:
                    tag = "file"
                i.write('      <%s id="p%s"' % (tag,idnum))
                if movie['id']:
                    i.write('media-id="%s"' % movie['id'][0])
                elif movie['label']:
                    i.write('label="%s"' % movie['label'][0])
                i.write('>%s</%s>\n' % (f,tag))
                idnum += 1
            i.write('    </video>\n')
            if movie['info']:
                i.write('    <info>\n')
                for k in movie['info'].keys():
                    i.write('      <%s>%s</%s>\n' % (k,movie['info'][k],k))
                i.write('    </info>\n')
            i.write('  </movie>\n')
    if skin:
        i.write('\n'+skin)
    i.write('</freevo>\n')




if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Syntax: xml_convert.py file.xml..."
        sys.exit(1)

    filenames = sys.argv[1:]

    for filename in filenames:

        tree = {}
        tree['movie'] = []
        
        parse_file(filename, tree)

        in_skin = 0
        for line in open(filename).readlines():
            if re.compile('^[ \t]+<skin', re.I).match(line):
                in_skin = 1
            if in_skin:
                skin += line
            if re.compile('^[ \t]+</skin', re.I).match(line):
                in_skin = 0

        print_tree(filename[:-3]+'fxd', tree)
