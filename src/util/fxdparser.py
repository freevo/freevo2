# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# fxdparser.py - Parser for fxd files
# -----------------------------------------------------------------------------
# $Id$
#
# This file handles the basic fxd fileparsing. It is possible to register
# specific handlers for parsing the different subnodes after <freevo>.
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2005 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Dirk Meyer <dischi@freevo.org>
# Maintainer:    Dirk Meyer <dischi@freevo.org>
#
# Please see the file doc/CREDITS for a complete list of authors.
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
import stat
import traceback
import codecs
import re

# xml support
from xml.utils import qp_xml

# freevo utils
import fileops
import cache
import sysconfig

class XMLnode(object):
    """
    One node for the FXDtree
    """
    def __init__(self, name, attr = [], first_cdata=None,
                 following_cdata=None):
        self.name = name
        self.attr_list = []
        for name, val in attr:
            self.attr_list.append(((None, name), val))
        self.attrs = self
        self.children = []
        self.first_cdata = first_cdata
        self.following_cdata = following_cdata

    def items(self):
        return self.attr_list


class FXDtree(qp_xml.Parser):
    """
    Class to parse and write fxd files
    """
    def __init__(self, filename, use_cache=True):
        """
        Load the file and parse it. If the file does not exists, create
        an empty <freevo> node.
        """
        qp_xml.Parser.__init__(self)
        self.filename = filename
        if not os.path.isfile(filename):
            self.tree = XMLnode('freevo')
        else:
            self.tree = None
            if not self.tree:
                f = open(filename)
                self.tree = self.parse(f)
                f.close()


    def add(self, node, parent=None, pos=None):
        """
        add a node to the parent at position pos. If parent is None, the
        <freevo> node fil be taken, if pos is None, the node will be inserted
        at the end of the children list.
        """
        if not parent:
            parent = self.tree
        if pos == None:
            parent.children.append(node)
        else:
            parent.children.insert(pos, node)


    def save(self, filename=None):
        """
        Save the tree
        """
        if not filename:
            filename = self.filename
        if os.path.isfile(filename):
            os.unlink(filename)
        f = codecs.open(filename, 'wb', sysconfig.ENCODING)
        f.write('<?xml version="1.0" encoding="%s" ?>\n' % sysconfig.ENCODING)
        self._dump_recurse(f, self.tree)

        f.write('\n')
        f.close()

        f = open(filename)
        self.tree = self.parse(f)
        f.close()


    def _dump_recurse(self, f, elem, depth=0):
        """
        Help function to dump all elements
        """
        if not elem:
            return
        f.write('<' + elem.name)
        for (ns, name), value in elem.attrs.items():
            f.write(u' ' + Unicode(name) + u'="' + Unicode(value) + '"')
        if elem.children != [] or elem.first_cdata != None:
            if elem.first_cdata == None:
                f.write('>\n  ')
                for i in range(depth):
                    f.write('  ')
            else:
                data = Unicode(elem.first_cdata).replace(u'&', u'&amp;')
                f.write(u'>' + data)

            for child in elem.children:
                self._dump_recurse(f, child, depth=depth+1)
                if child.following_cdata == None:
                    if child == elem.children[-1]:
                        f.write('\n')
                    else:
                        f.write('\n  ')
                    for i in range(depth):
                        f.write('  ')
                else:
                    f.write(child.following_cdata.replace('&', '&amp;'))
            f.write('</%s>' % elem.name)
        else:
            f.write('/>')


class FXD(object):
    """
    class to help parsing fxd files
    """

    class XMLnode(XMLnode):
        """
        a new node
        """
        pass

    def __init__(self, filename):
        self.tree = FXDtree(filename)
        self.filename = filename
        self.read_callback  = {}
        self.write_callback = {}
        self.user_data      = {}
        self.is_skin_fxd    = False


    def set_handler(self, name, callback, mode='r', force=False):
        """
        create callbacks for a node named 'name'. Mode can be 'r' when
        reading the node (parse), or 'w' for writing (save). The reading
        callback can return a special callback used for writing this node
        again. If force is true and an element for a write handler doesn't
        exists, it will be created.
        """
        if mode == 'r':
            self.read_callback[name]  = callback
        elif mode == 'w':
            self.write_callback[name] = [ callback, force ]
        else:
            print 'fxdparser.set_handler: unknown mode %s' % mode


    def __format_text(self, text):
        while len(text) and text[0] in (u' ', u'\t', u'\n'):
            text = text[1:]
        text = re.sub(u'\n[\t *]', u' ', text)
        while len(text) and text[-1] in (u' ', u'\t', u'\n'):
            text = text[:-1]
        return text


    def parse(self):
        """
        parse the tree and call all the callbacks
        """
        if self.tree.tree.name != 'freevo':
            print 'fxdparser.parse: ERROR: first node not <freevo>'
            return
        for node in self.tree.tree.children:
            if node.name == 'skin':
                self.is_skin_fxd = True
                break
        for node in self.tree.tree.children:
            if node.name in self.read_callback:
                callback = self.read_callback[node.name](self, node)
                if callback:
                    node.callback = callback


    def save(self):
        """
        save the tree and call all write callbacks before
        """
        # create missing but forces elements
        for name in self.write_callback:
            callback, force = self.write_callback[name]
            if force:
                for node in self.tree.tree.children:
                    if node.name == name:
                        break
                else:
                    # forced and missing
                    self.add(XMLnode(name), pos=0)

        # now run all callbacks
        for node in self.tree.tree.children:
            if hasattr(node, 'callback'):
                node.callback(self, node)
            elif node.name in self.write_callback:
                self.write_callback[node.name][0](self, node)

        # and save
        self.tree.save()


    def get_children(self, node, name, deep=1):
        """
        deep = 0, every deep, 1 = children, 2 = childrens children, etc.
        """
        ret = []
        for child in node.children:
            if deep < 2 and child.name == name:
                ret.append(child)
            if deep == 0:
                ret += self.get_children(child, name, 0)
            elif deep > 1:
                ret += self.get_children(child, name, deep-1)
        return ret


    def get_or_create_child(self, node, name):
        """
        return the first child with name or create it (and add it)
        """
        for child in node.children:
            if child.name == name:
                return child
        child = XMLnode(name)
        self.add(child, node)
        return child


    def childcontent(self, node, name):
        """
        return the content of the child node with the given name
        """
        for child in node.children:
            if child.name == name:
                return self.__format_text(child.textof())
        return ''


    def getattr(self, node, name, default=''):
        """
        return the attribute of the node or the 'default' if the atrribute
        is not set. If 'node' is 'None', it return the user defined data
        in the fxd object.
        """
        r = default
        if node:
            try:
                r = node.attrs[('',name)]
            except KeyError:
                pass
        else:
            try:
                r = self.user_data[name]
            except KeyError:
                pass
        if isinstance(default, int):
            try:
                r = int(r)
            except:
                r = default
        return r


    def setcdata(self, node, cdata):
        """
        set cdata for a node
        """
        if node:
            node.first_cdata = cdata


    def setattr(self, node, name, value):
        """
        sets the attribute of the node or if node is 'None', set user
        defined data for the fxd parser.
        """
        if node:
            node.attr_list.append(((None, name), value))
            #node.attrs[('',name)] = value
        else:
            self.user_data[name] = value


    def gettext(self, node):
        """
        rerurn the text of the node
        """
        return self.__format_text(node.textof())


    def parse_info(self, nodes, object, map={}):
        """
        map is a hash, the keys are the names in the fxd file,
        the content the variable names, e.g. {'content': 'description, }
        All tags not in the map are stored with the same name in info.
        """
        if not nodes:
            return

        if hasattr(nodes, 'children'):
            for node in nodes.children:
                if node.name == 'info':
                    nodes = [ node ]
                    break
            else:
                nodes = []

        # create a new dict to avoid messing up with default parameter
        # for items
        if not object.info:
            object.info = {}

        for node in nodes:
            for child in node.children:
                txt = child.textof()
                if not txt:
                    continue
                if child.name in map:
                    object.info[map[child.name]] = self.__format_text(txt)
                object.info[child.name] = self.__format_text(txt)


    def add(self, node, parent=None, pos=None):
        """
        add an element to the tree
        """
        if not isinstance(node, XMLnode):
            node = node.__fxd__(self)
        self.tree.add(node, parent, pos)
