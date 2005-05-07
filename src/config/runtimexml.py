# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# runtimexml.py - read the freevo runtime configuration file
# -----------------------------------------------------------------------------
# $Id$
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al.
#
# First Edition: Eric Bus <eric@fambus.nl>
#
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
# -----------------------------------------------------------------------------

# python imports
import os
import stat
import types
import logging

# xml support
from xml.dom import minidom
from xml.dom.minidom import getDOMImplementation
from xml.dom.ext import PrettyPrint

# freevo imports
import mcomm

# get logging object
log = logging.getLogger('config')

class RuntimeXMLParser:
    """
    class to parse complex structures from the configuration file
    """
    def __init__(self, rtx):
        self.rtx = rtx


    def parseNode(self, node):
        """
        This function parses a node and returns it contents.
        """
        childTag = None

        if node.hasChildNodes():
            hasTextNodes = False
            hasNonTextNodes = False
            for child in node.childNodes:
                if child.nodeType == node.TEXT_NODE:
                    hasTextNodes = True
                else:
                    # Check if the childTag matches previous tags
                    if hasNonTextNodes:
                        log.error('Only one direct child is allowed')
                        return None
                    else:
                        childTag = child.tagName
                        childNode = child
                        hasNonTextNodes = True

            if hasTextNodes and not hasNonTextNodes:
                # We only have text nodes as children
                return self.__getText(node.childNodes)
            else:
                # We also have non-text nodes. Skip the text nodes.
                return self.__parseComplexNode(childNode)

        elif node.nodeType == node.TEXT_NODE:
            return node.data
        else:
            return None


    def __parseComplexNode(self, node):
        """
        Parse a complex node and return the result.
        """
        if node.tagName == 'item':
            # walk through all nodes and return the first non-text node.
            for child in node.childNodes:
                if child.nodeType != child.TEXT_NODE:
                    return self.__parseComplexNode(child)

            # if we only have text nodes, return the text
            return self.__getText(node.childNodes)

        elif node.tagName == 'list':
            return self.__parseList(node)
        elif node.tagName == 'dict':
            return self.__parseDict(node)
        elif node.tagName == 'tuple':
            return self.__parseTuple(node)
        else:
            log.error("Unknown variable type '%s'" % node.tagName)
            return None


    def __getText(self,nodelist):
        """
        Combine the texts of all the children into one string
        """
        lst = []

        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                lst.append(node.data)

        return ''.join(lst)


    def __parseList(self, node):
        """
        This function parses a <list> node and processes it children.
        """
        mylist = []

        if node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType != node.TEXT_NODE:
#                    if child.tagName == 'item':
#                        mylist.append( self.__getText(child.childNodes) )
#                    else:
                    mylist.append( self.__parseComplexNode(child) )

        return mylist


    def __parseDict(self, node):
        """
        This function parses a <dict> node and processes it children.
        """
        mydict = {}

        if node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType != node.TEXT_NODE:
#                    if child.tagName == 'item' and child.getAttribute('key'):
#                        mydict[child.getAttribute('key')] = \
#                          self.__getText(child.childNodes)
#                    else:
                    mydict[child.getAttribute('key')] = \
                      self.__parseComplexNode(child)

        return mydict


    def __parseTuple(self, node):
        """
        This function parses a <tuple> node and processes it children.
        """
        mylist = []

        if node.hasChildNodes():
            for child in node.childNodes:
                if child.nodeType != node.TEXT_NODE:
#                    if child.tagName == 'item':
#                        mylist.append( self.__getText(child.childNodes) )
#                    else:
                    mylist.append( self.__parseComplexNode(child) )

        return tuple(mylist)


    def __stringToType(self, s):
        """
        Convert the type of a variable to a valid Python type.
        """
        if s == 'list':
            return types.ListType
        elif s == 'dict':
            return types.DictType
        elif s == 'tuple':
            return types.TupleType
        elif s == 'integer':
            return types.IntType
        elif s == 'string':
            return types.StringType
        else:
            return types.NoneType


    def varToNode(self, itemNode, template, item, level = 0, typeList = []):
        """
        This function converts a variable to a node or tree of nodes.
        """

        # Initialize the type list
        if not level:
            typeList = []
            if template.getAttribute('types'):
                mytypes = template.getAttribute('types').split('|')
            elif template.getAttribute('type'):
                mytypes = [template.getAttribute('type')]

            for t in mytypes:
                ret = self.__stringToType(t)
                if ret != types.NoneType:
                    typeList.append(ret)

        t = type(item)

        if level >= len(typeList):
            log.warning("Invalid node-type '%s', to deep" % type(item))
            return False

        if t == types.NoneType:
            return False
        elif t == list and typeList[level] == t:
            itemNode.appendChild( self.__listToNode(item,template,level,
                                                    typeList) )
        elif t == dict and typeList[level] == t:
            itemNode.appendChild( self.__dictToNode(item,template,level,
                                                    typeList) )
        elif t == tuple and typeList[level] == t:
            itemNode.appendChild( self.__tupleToNode(item,template,level,
                                                     typeList) )
        elif typeList[level] == types.StringType or \
          typeList[level] == types.IntType:
            textNode = self.rtx.doc.createTextNode( str(item) )
            itemNode.appendChild(textNode)
        else:
            log.warning("Invalid node-type '%s'" % type(item))
            return False


    def __listToNode(self, mylist, template, level, typeList):
        """
        Convert a list to a <list> node with the corresponding items
        """
        level += 1
        node = self.rtx.doc.createElement('list');
        for item in mylist:
            itemNode = self.rtx.doc.createElement('item')
            self.varToNode(itemNode, template, item, level, typeList)
            node.appendChild(itemNode)

        return node


    def __dictToNode(self, mydict, template, level, typeList):
        """
        Convert a list to a <list> node with the corresponding items
        """
        level += 1
        node = self.rtx.doc.createElement('dict');
        for k in mydict:
            itemNode = self.rtx.doc.createElement('item')
            itemNode.setAttribute('key', k)
            self.varToNode(itemNode, template, mydict[k], level, typeList)
            node.appendChild(itemNode)

        return node


    def __tupleToNode(self, mytuple, template, level, typeList):
        """
        Convert a list to a <list> node with the corresponding items
        """
        level += 1
        node = self.rtx.doc.createElement('tuple')
        mylist = list(mytuple)
        for item in mylist:
            itemNode = self.rtx.doc.createElement('item')
            self.varToNode(itemNode, template, item, level, typeList)
            node.appendChild(itemNode)

        return node


class RuntimeXML:
    """
    class to load the runtime configuration file
    """
    def restore_config(self):
        """
        This function restores the config variables that the runtime
        configuration file has modified.
        """
        for orig in self.original:
            self.config_globals[orig] = self.original[orig]


    def _getParents(self, node):
        """
        Create a string of the names of all the parent nodes, but not
        including the root node
        """
        names = [];
        node = node.parentNode
        while node.tagName != 'freevo':
            names.insert(0, node.tagName)
            node = node.parentNode

        return names


    def __rescan(self):
        """
        Rescan if the configuration file has changed. If so, restore all
        the previous changes and reload the configuration file.
        """
        if self.loaded and os.stat(self.xmlfile)[stat.ST_MTIME] > \
               self.last_time:
            log.info('Reloading runtime xml overrides: %s' % self.xmlfile)
            self.restore_config()
            self.load()


    def __removeChildren(self, node):
        """
        Remove all children from the node.
        """
        while node.hasChildNodes():
            node.removeChild( node.firstChild )


    def __make_branch(self, path):
        """
        This function returns the node at the specified path.
        If the node already exist, it returns the instance.
        Otherwise, it creates a new node.
        """
        level = self.doc.documentElement
        for val in path:
            children = level.childNodes

            found = False
            for child in children:
                if child.nodeType != child.TEXT_NODE and child.tagName == val:
                    level = child
                    found = True
                    children = []

            if not found:
                elem = self.doc.createElement(val)
                level.appendChild(elem)
                level = elem

        return level


    def get_value(self, path, name):
        """
        Retrieve the value of a global varible
        """
        full_name = self.make_conf_name(path, name)

        # Check if we want to change the value of the variable
        if not self.config_globals.has_key(full_name):
            return None
        else:
            return self.config_globals[full_name]


    def set_value(self, path, name, value, node = None, write_delay = False):
        """
        Change a configuration value in both the active configuration
        as the on disk configuration file.
        """
        full_name = self.make_conf_name(path, name)

        # Check if we may set this variable
        if not self.variables.has_key(full_name):
            log.warning("Template doesn't allow config.%s to be set" % \
                        full_name)
            return False

        # Check if we want to change the value of the variable
        if self.config_globals.has_key(full_name) and \
          self.config_globals[full_name] == value:
            return True

        log.info("Setting config.%s to '%s'" % ( full_name, value ) )

        # Backup the original value (only when we didn't already backup it)
        if not self.original.has_key(full_name) and \
               self.config_globals.has_key(full_name):
            self.original[full_name] = self.config_globals[full_name]

        self.config_globals[full_name] = value

        if self.variables[full_name]['node']:
            self.__removeChildren( self.variables[full_name]['node'] )
            self.rtxp.varToNode( self.variables[full_name]['node'], \
              self.variables[full_name]['template'], value )
        elif node:
            self.variables[full_name]['node'] = node;
            self.__removeChildren( self.variables[full_name]['node'] )
            self.rtxp.varToNode( self.variables[full_name]['node'], \
              self.variables[full_name]['template'], value )
        else:
            parent = self.__make_branch(path)

            # Create the new element, including the text
            elem = self.doc.createElement('var')
            elem.setAttribute('name',name)
            self.rtxp.varToNode( elem, \
              self.variables[full_name]['template'], value )

            # Append the new node to the document
            parent.appendChild(elem)

            # Save the element in our map
            self.variables[full_name]['node'] = elem

        # Call all the handlers, if available
        if self.variables.has_key(full_name):
            for handler in self.variables[full_name]['handlers']:
                handler(full_name)

        # Save the changes to the disk
        if not write_delay:
            self.save()

        return True


    def set_handler(self, path, name, handler):
        """
        Set a change handler for a specific property.
        The handler is called when the specified config value is set.
        """
        full_name = '_'.join(path).upper() + '_' + \
                    name.replace(' ','_').upper()

        if self.variables.has_key(full_name):
            self.variables[full_name]['handlers'].append(handler)
        else:
            self.variables[full_name]['handlers'] = [ handler ]


    def make_conf_name(self, path, name):
        """
        Use the path and name to create a Freevo configuration name
        (for example: config.FREEVO_CONF_DIRECTIVE)
        """
        return '_'.join(path).upper() + '_' + name.replace(' ','_').upper()


    def remove_handler(self, path, name, handler):
        """
        Remove a change handler for a specific property.
        """
        full_name = self.make_conf_name(path, name)

        if self.variables.has_key(full_name):
            for existing_handler in self.variables[full_name]['handlers']:
                if existing_handler == handler:
                    self.variables[full_name]['handlers'].remove(handler)
                    return True

        return False


    def load_template(self, filename):
        """
        Open and parse the configuration template and create a map of
        the available configuration items.
        """
        try:
            self.tpl_doc = minidom.parse(filename)
        except:
            log.error('Error while parsing runtime configuration template %s'%\
                      self.xmlfile)
            impl = getDOMImplementation()
            self.tpl_doc = impl.createDocument(None, "freevo", None)
            return False

        # Every variable is contained in a <var/> tag
        varlist = self.tpl_doc.getElementsByTagName('var')

        for node in varlist:
            path = self._getParents(node)
            name = node.getAttribute('name')
            full_name = self.make_conf_name(path, name)
            log.info('Found %s in runtime configuration template' % full_name)
            self.variables[full_name] = \
              { 'template' : node, 'node' : None, 'handlers' : [] }

        return True


    def load(self):
        """
        Open and parse the configuration file and set the available
        configuration items to their values
        """

        try:
            self.doc = minidom.parse(self.xmlfile)
        except:
            log.error('Error while parsing runtime configuration file %s' % \
                      self.xmlfile)
            return self.__init_doc()

        self.loaded = True
        self.last_time = os.stat(self.xmlfile)[stat.ST_MTIME]

        # Every variable is contained in a <var> tag
        varlist = self.doc.getElementsByTagName('var')

        for node in varlist:
            if node.hasChildNodes:
                path = self._getParents(node)
                name = node.getAttribute('name')
                value = self.rtxp.parseNode(node)
                self.set_value(path, name, value, node, True)

        return True


    def save(self):
        """
        Save the complete and modified tree to disk.
        """
        if self.doc:
            log.info('Saving runtime configuration to %s' % self.xmlfile)
            f = open(self.xmlfile, 'w')
            PrettyPrint(self.doc, stream=f)
            f.close()

        # Change our modification time
        self.last_time = os.stat(self.xmlfile)[stat.ST_MTIME]


    def __find_leaf(self, path):
        """
        This function returns the node at the specified path.
        If the node already exist, it returns the instance.
        Otherwise, it creates a new node.
        """
        level = self.tpl_doc.documentElement

        for val in path:
            children = level.childNodes

            found = False
            for child in children:
                if child.nodeType != child.TEXT_NODE and child.tagName == val:
                    level = child
                    found = True
                    children = []

            if not found:
                return False

        return level


    def __init_doc(self):
        """
        Initializes the document element
        """
        impl = getDOMImplementation()
        self.doc = impl.createDocument(None, "freevo", None)
        return False


    def init_item_options(self, child):
        options = {}

        if child.getAttribute('type') == 'integer':
            if child.getAttribute('increment'):
                options['increment'] = int(child.getAttribute('increment'))
            else:
                options['increment'] = 1
            if child.getAttribute('increment'):
                options['min_int'] = int(child.getAttribute('minInt'))
            else:
                options['min_int'] = -1
            if child.getAttribute('maxInt'):
                options['max_int'] = int(child.getAttribute('maxInt'))
            else:
                options['max_int'] = -1

        return options


    def get_items(self, path):
        """
        This function returns a list of labels and config names
        from the XML template. For use in the GUI interface.
        """
        leaf = self.__find_leaf(path)

        items = []

        if leaf.hasChildNodes():
            for child in leaf.childNodes:
                if child.nodeType != child.TEXT_NODE and \
                       child.getAttribute('label'):
                    options = self.init_item_options(child)
                    items.append( ( child.getAttribute('label'), child.tagName,
                                    child.getAttribute('name'),
                                    self.make_conf_name( path, child.tagName ),
                                    child.getAttribute('type'), options ) )
        return items


    def __init__(self, conf_globs):
        """
        Find the runtime configuration file and load it.
        """
        self.doc = None
        self.loaded = False
        self.original = {}
        self.variables = {}

        self.rtxp = RuntimeXMLParser(self)

        tpl_file = os.path.join(conf_globs['SHARE_DIR'], 'fxd/runtime_config.tpl.fxd')
        if os.path.isfile(tpl_file):
            if not self.load_template(tpl_file):
                return
        else:
            log.error('Cannot find runtime configuration template %s' % \
                      tpl_file )
            log.error('Runtime configuration disabled')
            return

        cfgfilepath = [ '.', os.path.expanduser('~/.freevo') ]

        mcomm.register_event('config.runtimexml.rescan', self.__rescan)

        # Make a copy of our configuration variables
        self.config_globals = conf_globs

        # Load the XML with runtime configuration settings
        for dirname in cfgfilepath:
            xmlfile = dirname + '/runtime_config.xml'
            if os.path.isfile(xmlfile):
                self.xmlfile = xmlfile
                self.load()
                return

        # Make sure we always have a valid document element
        self.__init_doc()

        # We need a default runtime path, use the homedir
        self.xmlfile = os.path.expanduser('~/.freevo') + '/runtime_config.xml'
