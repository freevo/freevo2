# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxdparser.py - Freevo FXD parser
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2007 Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file AUTHORS for a complete list of authors.
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

# python imports
import os
import codecs
from xml.dom import minidom

def _write_data(writer, data):
    "Writes datachars to writer."
    data = data.replace("&", "&amp;").replace("<", "&lt;")
    data = data.replace("\"", "&quot;").replace(">", "&gt;")
    writer.write(data)

class Wrapper(object):
    def __init__(self, node):
        self._node = node

    def __getattr__(self, attr):
        if attr == 'name':
            return self._node.nodeName
        if attr == 'getattr':
            return self._node.getAttribute
        if attr == 'children':
            return self
        if attr == 'root':
            node = self._node
            while node.parentNode:
                node = node.parentNode
            return node
        return getattr(self._node, attr)

    def __iter__(self):
        for n in self._node.childNodes:
            if isinstance(n, minidom.Element):
                yield Wrapper(n)

    def _get_content(self):
        if len(self._node.childNodes):
            return self._node.childNodes[0].data
        return u''

    def _set_content(self, value):
        if not isinstance(value, (unicode, str)):
            value = str(value)
        node = self.root.createTextNode(value)
        self._node.appendChild(node)
        
    content = property(_get_content, _set_content, None, 'cdata content')

    def add_child(self, name, content=None, **kwargs):
        node = self.root.createElement(name)
        self._node.appendChild(node)
        node = Wrapper(node)
        if content is not None:
            node.content = content
        for key, value in kwargs.items():
            if not isinstance(value, (unicode, str)):
                value = str(value)
            node.setAttribute(key, value)
        return node

    def _writexml(self, writer, indent="", addindent="", newl=""):
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(indent+"<" + self.tagName)

        attrs = self.attributes
        a_names = attrs.keys()
        a_names.sort()

        for a_name in a_names:
            writer.write(" %s=\"" % a_name)
            _write_data(writer, attrs[a_name].value)
            writer.write("\"")
        if len(self.childNodes) == 1 and \
           self.childNodes[0].nodeType == self._node.TEXT_NODE:
            writer.write(">")
            _write_data(writer, self.childNodes[0].data)
            writer.write("</%s>%s" % (self.tagName,newl))
        elif self.childNodes:
            writer.write(">%s"%(newl))
            for node in self.children:
                node._writexml(writer,indent+addindent,addindent,newl)
            writer.write("%s</%s>%s" % (indent,self.tagName,newl))
        else:
            writer.write("/>%s"%(newl))

    def save(self, filename):
        f = codecs.open(filename, 'w', 'utf8')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        self._writexml(f, '', '    ', '\n')


def Document(filename=None):
    if filename:
        doc = minidom.parse(filename)
        doc.dirname = os.path.dirname(filename)
        tree = doc.firstChild
        if tree.nodeName != 'freevo':
            raise RuntimeError('%s is not fxd file' % filename)
        return Wrapper(tree)
    doc = minidom.Document()
    doc.dirname = ''
    tree = doc.createElement('freevo')
    doc.appendChild(tree)
    return Wrapper(tree)
