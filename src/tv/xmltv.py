#
#  xmltv.py - Python interface to XMLTV format, based on XMLTV.pm
#
#  Copyright (C) 2001 James Oakley
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#
#  Notes:
#  - Uses qp_xml instead of DOM. It's way faster
#  - Read and write functions use file objects instead of filenames
#  - Unicode is removed on dictionary keys because the xmlrpclib marshaller
#    chokes on it. It'll always be Latin-1 anyway... (famous last words)
#
#  Yes, A lot of this is quite different than the Perl module, mainly to keep
#  it Pythonic
#
#  If you have any trouble: jfunk@funktronics.ca
#

from xml.utils import qp_xml
import string


# The date formats used in XMLTV
date_format_tz = '%Y%m%d%H%M%S %Z'
date_format_notz = '%Y%m%d%H%M'

# The locale for dictionary keys. Leaving them in Unicode screws up the
# XMLRPC marshaller
locale = 'Latin-1'

# The extraction process could be simpler, building a tree recursively
# without caring about the element names, but it's done this way to allow
# special handling for certain elements. If 'desc' changed one day then
# ProgrammeHandler.desc() can be modified to reflect it

class _ProgrammeHandler:
    """
    Handles XMLTV programme elements
    """

    #
    # <tv> sub-tags
    #

    def title(self, node):
        return _readwithlang(node)

    def sub_title(self, node):
        return _readwithlang(node)

    def desc(self, node):
        return _readwithlang(node)

    def credits(self, node):
        return _extractNodes(node, self)

    def date(self, node):
        return node.textof()

    def category(self, node):
        return _readwithlang(node)

    def language(self, node):
        return _readwithlang(node)

    def orig_language(self, node):
        return _readwithlang(node)

    def length(self, node):
        units = _getxmlattr(node, u'units')
        seconds = int(node.textof())
        if units == 'seconds':
            return seconds
        elif units == 'minutes':
            return seconds * 60
        elif units == 'hours':
            return seconds * 3600
        else:
            return None

    def icon(self, node):
        return _ChannelHandler.icon(self, node)

    def url(self, node):
        return _ChannelHandler.url(self, node)

    def country(self, node):
        return _readwithlang(node)

    def episode_num(self, node):
        system = _getxmlattr(node, u'system')
        if system == '':
            system = 'onscreen'
        return (node.textof(), system)

    def video(self, node):
        result = {}
        for child in node.children:
            result[child.name.encode(locale)] = self._call(child)
        return result

    def audio(self, node):
        return _extractNodes(node, self)

    def previously_shown(self, node):
        data = {}
        for attr in (u'start', u'channel'):
            if node.attrs.has_key(('', attr)):
                data[attr.encode(locale)] = node.attrs[('', attr)]
        return data

    def premiere(self, node):
        return _readwithlang(node)

    def last_chance(self, node):
        return _readwithlang(node)

    def new(self, node):
        return 1

    def subtitles(self, node):
        data = {}
        if node.attrs.has_key(('', u'type')):
            data['type'] = _getxmlattr(node, u'type')
        for child in node.children:
            if child.name == u'language':
                data['language'] = child.textof()
        return data

    def rating(self, node):
        data = {}
        if node.attrs.has_key(('', u'system')):
            data['system'] = node.attrs[('', u'system')]
        for child in node.children:
            if child.name == u'value':
                data['value'] = child.textof()
        return data

    def star_rating(self, node):
        data = {}
        for child in node.children:
            if child.name == u'value':
                data['value'] = child.textof()
        return data


    #
    # <credits> sub-tags
    #

    def actor(self, node):
        return node.textof()

    def director(self, node):
        return node.textof()

    def writer(self, node):
        return node.textof()

    def adapter(self, node):
        return node.textof()

    def producer(self, node):
        return node.textof()

    def presenter(self, node):
        return node.textof()

    def commentator(self, node):
        return node.textof()

    def guest(self, node):
        return node.textof()


    #
    # <video> and <audio> sub-tags
    #

    def present(self, node):
        return _decodeboolean(node)

    def colour(self, node):
        return _decodeboolean(node)

    def aspect(self, node):
        return node.textof()

    def stereo(self, node):
        return node.textof()


    #
    # Magic
    #

    def _call(self, node):
        try:
            return getattr(self, string.replace(node.name.encode(), '-', '_'))(node)
        except NameError:
            return '**Unhandled Element**'

class _ChannelHandler:
    """
    Handles XMLTV channel elements
    """
    def display_name(self, node):
        return node.textof()

    def icon(self, node):
        data = {}
        data['desc'] = node.textof()
        if node.attrs.has_key(('', u'src')):
            data['src'] = _getxmlattr(node, u'src')
        return data

    def url(self, node):
        return node.textof()


    #
    # More Magic
    #

    def _call(self, node):
        try:
            return getattr(self, string.replace(node.name.encode(), '-', '_'))(node)
        except NameError:
            return '**Unhandled Element**'



# Some convenience functions, treat them as private

def _extractNodes(node, handler):
    """
    Builds a dictionary from the sub-elements of node.
    'handler' should be an instance of a handler class
    """
    result = {}
    for child in node.children:
        if not result.has_key(child.name):
            result[child.name.encode(locale)] = []
        result[child.name.encode(locale)].append(handler._call(child))
    return result

def _getxmlattr(node, attr):
    """
    If 'attr' is present in 'node', return the value, else return an empty
    string

    Yeah, yeah, namespaces are ignored and all that stuff
    """
    if node.attrs.has_key((u'', attr)):
        return node.attrs[(u'', attr)]
    else:
        return u''

def _readwithlang(node):
    """
    Returns a tuple containing the text of a node and the text of the 'lang'
    attribute
    """
    return (node.textof(), _getxmlattr(node, u'lang'))

def _decodeboolean(node):
    text = node.textof().lower()
    if text == 'yes':
        return 1
    elif text == 'no':
        return 0
    else:
        return None

def _node_to_programme(node):
    """
    Create a programme dictionary from a qp_xml node
    """
    handler = _ProgrammeHandler()
    programme = _extractNodes(node, handler)

    for attr in (u'start', u'stop', u'channel'):
        programme[attr.encode(locale)] = node.attrs[(u'', attr)]
    return programme

def _node_to_channel(node):
    """
    Create a channel dictionary from a qp_xml node
    """
    handler = _ChannelHandler()
    channel = _extractNodes(node, handler)

    channel['id'] = node.attrs[('', 'id')]
    return channel


def read_programmes(fp):
    """
    Read an XMLTV file and get out the relevant information for each
    programme.

    Parameter: file object to read from
    Returns: list of hashes with start, titles, etc.
    """
    parser = qp_xml.Parser()
    doc = parser.parse(fp.read())

    programmes = []

    for node in doc.children:
        if node.name == u'programme':
            programmes.append(_node_to_programme(node))

    return programmes


def read_data(fp):
    """
    Get the source and other info from an XMLTV file.

    Parameter: filename to read from
    Returns: dictionary of <tv> attributes
    """
    parser = qp_xml.Parser()
    doc = parser.parse(fp.read())

    attrs = {}

    for key in doc.attrs.keys():
        attrs[key[1].encode(locale)] = doc.attrs[key]

    return attrs


def write_programmes(fp, programmes):
    """
    Write several programmes as a complete XMLTV file to the file object fp

    **this is not implemented yet**

    Parameter: fp - file object to write to
               programmes - list of programme hashrefs
    """
    pass

def write_programme(fp, programme):
    """
    Write details for a single programme as XML.

    **This is not implemented yet**

    Parameters:
      reference to hash of programme details (a 'programme')
    """
    pass

def read_channels(fp):
    """
    Read the channels.xml file and return a list of channel
    information.
    """
    parser = qp_xml.Parser()
    doc = parser.parse(fp.read())

    channels = []

    for node in doc.children:
        if node.name == u'channel':
            channels.append(_node_to_channel(node))

    return channels

def write_channels(fp, channels):
    """
    Write channels data as channels.dtd XML to file 'channels.xml'.

    **This is not implemented yet**

    Parameter: channels data hashref
    """
    pass

if __name__ == '__main__':
    # Tests
    from pprint import pprint
    import sys

    if len(sys.argv) == 1:
        print "No file specified"
        sys.exit(1)
    # This tends to generate a lot of output
    pprint(read_programmes(open(sys.argv[1])))
    pprint(read_data(open(sys.argv[1])))
    pprint(read_channels(open(sys.argv[1])))
