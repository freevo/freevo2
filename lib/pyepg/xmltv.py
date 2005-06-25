#
#  xmltv.py - Python interface to XMLTV format, based on XMLTV.pm
#
#  Copyright (C) 2001 James Oakley
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2.1 of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

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

# Changes for Freevo:
# o change data_format to '%Y%m%d%H%M%S %Z'
# o delete all encode, return Unicode
# o add except AttributeError: for unhandled elements (line 250ff)


from xml.utils import qp_xml
from xml.sax import saxutils
import string, types, re

# The Python-XMLTV version
VERSION = "0.5.15"

# The date format used in XMLTV
date_format = '%Y%m%d%H%M%S %Z'
# Note: Upstream xmltv.py uses %z so remember to change that when syncing
date_format_notz = '%Y%m%d%H%M%S'

# These characters are illegal in XML
XML_BADCHARS = re.compile(u'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD\u10000-\u10FFFF]')


#
# Options. They may be overridden after this module is imported
#

# The extraction process could be simpler, building a tree recursively
# without caring about the element names, but it's done this way to allow
# special handling for certain elements. If 'desc' changed one day then
# ProgrammeHandler.desc() can be modified to reflect it

class _ProgrammeHandler(object):
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
        data = {}
        data['units'] = _getxmlattr(node, u'units')
        try:
            length = int(node.textof())
        except ValueError:
            pass
        data['length'] = length
        return data

    def icon(self, node):
        data = {}
        for attr in (u'src', u'width', u'height'):
            if node.attrs.has_key(('', attr)):
                data[attr] = _getxmlattr(node, attr)
        return data

    def url(self, node):
        return node.textof()

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
            result[child.name] = self._call(child)
        return result

    def audio(self, node):
        result = {}
        for child in node.children:
            result[child.name] = self._call(child)
        return result

    def previously_shown(self, node):
        data = {}
        for attr in (u'start', u'channel'):
            if node.attrs.has_key(('', attr)):
                data[attr] = node.attrs[('', attr)]
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
                data['language'] = _readwithlang(child)
        return data

    def rating(self, node):
        data = {}
        data['icon'] = []
        if node.attrs.has_key(('', u'system')):
            data['system'] = node.attrs[('', u'system')]
        for child in node.children:
            if child.name == u'value':
                data['value'] = child.textof()
            elif child.name == u'icon':
                data['icon'].append(self.icon(child))
        if len(data['icon']) == 0:
            del data['icon']
        return data

    def star_rating(self, node):
        data = {}
        data['icon'] = []
        for child in node.children:
            if child.name == u'value':
                data['value'] = child.textof()
            elif child.name == u'icon':
                data['icon'].append(self.icon(child))
        if len(data['icon']) == 0:
            del data['icon']
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
        except AttributeError:
            return '**Unhandled Element**'

class _ChannelHandler(object):
    """
    Handles XMLTV channel elements
    """
    def display_name(self, node):
        return _readwithlang(node)

    def icon(self, node):
        data = {}
        for attr in (u'src', u'width', u'height'):
            if node.attrs.has_key(('', attr)):
                data[attr] = _getxmlattr(node, attr)
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


#
# Some convenience functions, treat them as private
#

def _extractNodes(node, handler):
    """
    Builds a dictionary from the sub-elements of node.
    'handler' should be an instance of a handler class
    """
    result = {}
    for child in node.children:
        if not result.has_key(child.name):
            result[child.name] = []
        result[child.name].append(handler._call(child))
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
    Returns a tuple containing the text of a 'node' and the text of the 'lang'
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
    Create a programme dictionary from a qp_xml 'node'
    """
    handler = _ProgrammeHandler()
    programme = _extractNodes(node, handler)

    for attr in (u'start', u'channel'):
        programme[attr] = node.attrs[(u'', attr)]
    if (u'', u'stop') in node.attrs:
        programme[u'stop'] = node.attrs[(u'', u'stop')]
    #else:
        # Sigh. Make show zero-length. This will allow the show to appear in
        # searches, but it won't be seen in a grid, if the grid is drawn to
        # scale
        #programme[u'stop'] = node.attrs[(u'', u'start')]
    return programme

def _node_to_channel(node):
    """
    Create a channel dictionary from a qp_xml 'node'
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
        attrs[key[1]] = doc.attrs[key]

    return attrs


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



class Writer(object):
    """
    A class for generating XMLTV data

    **All strings passed to this class must be Unicode, except for dictionary
    keys**
    """
    def __init__(self, fp, encoding="iso-8859-1", date=None,
                 source_info_url=None, source_info_name=None,
                 generator_info_url=None, generator_info_name=None):
        """
        Arguments:

          'fp' -- A File object to write XMLTV data to

          'encoding' -- The text encoding that will be used.
                        *Defaults to 'iso-8859-1'*

          'date' -- The date this data was generated. *Optional*

          'source_info_url' -- A URL for information about the source of the
                               data. *Optional*

          'source_info_name' -- A human readable description of
                                'source_info_url'. *Optional*

          'generator_info_url' -- A URL for information about the program
                                  that is generating the XMLTV document.
                                  *Optional*

          'generator_info_name' -- A human readable description of
                                   'generator_info_url'. *Optional*

        """
        self.fp = fp
        self.encoding = encoding
        self.date = date
        self.source_info_url = source_info_url
        self.source_info_name = source_info_name
        self.generator_info_url = generator_info_url
        self.generator_info_name = generator_info_name

        s = """<?xml version="1.0" encoding="%s"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
""" % self.encoding

        # tv start tag
        s += "<tv"
        for attr in ('date', 'source_info_url', 'source_info_name',
                     'generator_info_url', 'generator_info_name'):
            if attr:
                s += ' %s="%s"' % (attr, self.__dict__[attr])
        s += ">\n"
        self.fp.write(s)


    def _validateStructure(self, d):
        """
        Raises 'TypeError' if any strings are not Unicode

        Argumets:

          's' -- A dictionary
        """
        if type(d) == types.StringType:
            raise TypeError ('All strings, except keys, must be in Unicode. Bad string: %s' % d)
        elif type(d) == types.DictType:
            for key in d.keys():
                self._validateStructure(d[key])
        elif type(d) == types.TupleType or type(d) == types.ListType:
            for i in d:
                self._validateStructure(i)


    def _formatCDATA(self, cdata):
        """
        Returns fixed and encoded CDATA

        Arguments:

          'cdata' -- CDATA you wish to encode
        """
        # Let's do what 4Suite does, and replace bad characters with '?'
        cdata = XML_BADCHARS.sub(u'?', cdata)
        return saxutils.escape(cdata).encode(self.encoding)


    def _formatTag(self, tagname, attrs=None, pcdata=None, indent=4):
        """
        Return a simple tag

        Arguments:

          'tagname' -- Name of tag

          'attrs' -- dictionary of attributes

          'pcdata' -- Content

          'indent' -- Number of spaces to indent
        """
        s = indent*' '
        s += '<%s' % tagname
        if attrs:
            for key in attrs.keys():
                s += ' %s="%s"' % (key, self._formatCDATA(attrs[key]))
        if pcdata:
            s += '>%s</%s>\n' % (self._formatCDATA(pcdata), tagname)
        else:
            s += '/>\n'
        return s


    def end(self):
        """
        Write the end of an XMLTV document
        """
        self.fp.write("</tv>\n")


    def write_programme(self, programme):
        """
        Write a single XMLTV 'programme'

        Arguments:

          'programme' -- A dict representing XMLTV data
        """
        self._validateStructure(programme)
        s = '  <programme'

        # programme attributes
        for attr in ('start', 'channel'):
            if programme.has_key(attr):
                s += ' %s="%s"' % (attr, self._formatCDATA(programme[attr]))
            else:
                raise ValueError("'programme' must contain '%s' attribute" % attr)

        for attr in ('stop', 'pdc-start', 'vps-start', 'showview', 'videoplus', 'clumpidx'):
            if programme.has_key(attr):
                s += ' %s="%s"' % (attr, self._formatCDATA(programme[attr]))

        s += '>\n'

        # Required children
        err = 0
        if programme.has_key('title'):
            if len(programme['title']) > 0:
                for title in programme['title']:
                    if title[1] != u'':
                        attrs = {'lang': title[1]}
                    else:
                        attrs=None
                    s += self._formatTag('title', attrs, title[0])
            else:
                err = 1
        else:
            err = 1

        if err:
            raise ValueError("'programme' must contain at least one 'title' element")

        # Zero or more children with PCDATA and 'lang' attribute
        for element in ('sub-title', 'desc', 'category', 'country'):
            if programme.has_key(element):
                for item in programme[element]:
                    if item[1] != u'':
                        attrs = {'lang': item[1]}
                    else:
                        attrs=None
                    s += self._formatTag(element, attrs, item[0])

        # Zero or one children with PCDATA and 'lang' attribute
        for element in ('language', 'orig-language', 'premiere', 'last-chance'):
            if programme.has_key(element):
                if len(programme[element]) != 1:
                    raise ValueError("Only one '%s' element allowed" % element)
                if programme[element][0][1] != u'':
                    attrs = {'lang': programme[element][0][1]}
                else:
                    attrs=None
                s += self._formatTag(element, attrs, programme[element][0][0])

        # Credits
        if programme.has_key('credits'):
            s += '    <credits>\n'
            for credit in ('director', 'actor', 'writer', 'adapter',
                           'producer', 'presenter', 'commentator', 'guest'):
                if programme['credits'][0].has_key(credit):
                    for name in programme['credits'][0][credit]:
                        s += self._formatTag(credit, pcdata=name, indent=6)
            s += '    </credits>\n'

        # Date
        if programme.has_key('date'):
            if len(programme['date']) != 1:
                raise ValueError("Only one 'date' element allowed")
            s += self._formatTag('date', pcdata=programme['date'][0])

        # Length
        if programme.has_key('length'):
            if len(programme['length']) != 1:
                raise ValueError("Only one 'length' element allowed")
            s += self._formatTag('length', {'units': programme['length'][0]['units']}, str(programme['length'][0]['length']).decode(self.encoding))

        # Icon
        if programme.has_key('icon'):
            for icon in programme['icon']:
                if icon.has_key('src'):
                    s += self._formatTag('icon', icon)
                else:
                    raise ValueError("'icon' element requires 'src' attribute")

        # URL
        if programme.has_key('url'):
            for url in programme['url']:
                s += self._formatTag('url', pcdata=url)

        # Episode-num
        if programme.has_key('episode-num'):
            if len(programme['episode-num']) != 1:
                raise ValueError("Only one 'episode-num' element allowed")
            s += self._formatTag('episode-num', {'system': programme['episode-num'][0][1]},
                                programme['episode-num'][0][0])

        # Video and audio details
        for element in ('video', 'audio'):
            if programme.has_key(element):
                s += '    <%s>\n' % element
                for key in programme[element][0]:
                    s += self._formatTag(key, pcdata=str(programme[element][0][key]).decode(self.encoding), indent=6)
                s += '    </%s>\n' % element

        # Previously shown
        if programme.has_key('previously-shown'):
            s += self._formatTag('previously-shown', programme['previously-shown'][0])

        # New
        if programme.has_key('new'):
            s += self._formatTag('new')

        # Subtitles
        if programme.has_key('subtitles'):
            s += '    <subtitles'
            if programme['subtitles'][0].has_key('type'):
                s += ' type="%s"' % self._formatCDATA(programme['subtitles'][0]['type'])
            s += '>\n'
            if programme['subtitles'][0].has_key('language'):
                if programme['subtitles'][0]['language'][1] != u'':
                    attrs = {'lang': programme['subtitles'][0]['language'][1]}
                else:
                    attrs = None
                s += self._formatTag('language', None, programme['subtitles'][0]['language'][0], indent=6)
            s += '    </subtitles>\n'

        # Rating and star rating
        for element in ('rating', 'star-rating'):
            if programme.has_key(element):
                s += '    <%s' % element
                if element == 'rating':
                    if programme[element][0].has_key('system'):
                        s += ' system="%s"' % self._formatCDATA(programme[element][0]['system'])
                s += '>\n'
                if programme[element][0].has_key('value'):
                    s += self._formatTag('value', pcdata=programme[element][0]['value'], indent=6)
                if programme[element][0].has_key('icon'):
                    for icon in programme[element][0]['icon']:
                        s += self._formatTag('icon', icon, indent=6)
                s += '    </%s>\n' % element

        # End tag
        s += '  </programme>\n'

        self.fp.write(s)


    def write_channel(self, channel):
        """
        Write a single XMLTV 'channel'

        Arguments:

          'channel' -- A dict representing XMLTV data
        """
        self._validateStructure(channel)
        s = '  <channel id="%s">\n' % channel['id']

        # Write display-name(s)
        err = 0
        if channel.has_key('display-name'):
            if len(channel['display-name']) > 0:
                for name in channel['display-name']:
                    if name[1] != u'':
                        attrs = {'lang': name[1]}
                    else:
                        attrs = None
                    s += self._formatTag('display-name', attrs, name[0])
            else:
                err = 1
        else:
            err = 1

        if err:
            raise ValueError("'channel' must contain at least one 'display-name' element")

        # Icon
        if channel.has_key('icon'):
            for icon in channel['icon']:
                if icon.has_key('src'):
                    s += self._formatTag('icon', icon)
                else:
                    raise ValueError("'icon' element requires 'src' attribute")

        # URL
        if channel.has_key('url'):
            for url in channel['url']:
                s += self._formatTag('url', pcdata=url)

        s += '  </channel>\n'

        self.fp.write(s)


if __name__ == '__main__':
    # Tests
    from pprint import pprint
    from StringIO import StringIO
    import sys

    # An example file
    xmldata = StringIO("""<?xml version="1.0" encoding="iso-8859-1"?>
<!DOCTYPE tv SYSTEM "xmltv.dtd">
<tv date="20030811003608 -0300" source-info-url="http://www.funktronics.ca/python-xmltv" source-info-name="Funktronics" generator-info-name="python-xmltv" generator-info-url="http://www.funktronics.ca/python-xmltv">
  <channel id="C10eltv.zap2it.com">
    <display-name>Channel 10 ELTV</display-name>
    <url>http://www.eastlink.ca/</url>
  </channel>
  <channel id="C11cbht.zap2it.com">
    <display-name lang="en">Channel 11 CBHT</display-name>
    <icon src="http://tvlistings2.zap2it.com/tms_network_logos/cbc.gif"/>
  </channel>
  <programme start="20030702000000 ADT" channel="C23robtv.zap2it.com" stop="20030702003000 ADT">
    <title>This Week in Business</title>
    <category>Biz</category>
    <category>Fin</category>
    <date>2003</date>
    <audio>
      <stereo>stereo</stereo>
    </audio>
  </programme>
  <programme start="20030702000000 ADT" channel="C36wuhf.zap2it.com" stop="20030702003000 ADT">
    <title>Seinfeld</title>
    <sub-title>The Engagement</sub-title>
    <desc>In an effort to grow up, George proposes marriage to former girlfriend Susan.</desc>
    <category>Comedy</category>
    <country>USA</country>
    <language>English</language>
    <orig-language>English</orig-language>
    <premiere lang="en">Not really. Just testing</premiere>
    <last-chance>Hah!</last-chance>
    <credits>
      <actor>Jerry Seinfeld</actor>
      <producer>Larry David</producer>
    </credits>
    <date>1995</date>
    <length units="minutes">22</length>
    <episode-num system="xmltv_ns">7 . 1 . 1/1</episode-num>
    <video>
      <colour>1</colour>
      <present>1</present>
      <aspect>4:3</aspect>
    </video>
    <audio>
      <stereo>stereo</stereo>
    </audio>
    <previously-shown start="19950921103000 ADT" channel="C12whdh.zap2it.com"/>
    <new/>
    <subtitles type="teletext">
      <language>English</language>
    </subtitles>
    <rating system="VCHIP">
      <value>PG</value>
      <icon src="http://some.ratings/PGicon.png" width="64" height="64"/>
    </rating>
    <star-rating>
      <value>4/5</value>
      <icon src="http://some.star/icon.png" width="32" height="32"/>
    </star-rating>
  </programme>
</tv>
""")
    pprint(read_data(xmldata))
    xmldata.seek(0)
    pprint(read_channels(xmldata))
    xmldata.seek(0)
    pprint(read_programmes(xmldata))

    # Test the writer
    programmes = [{'audio': [{'stereo': u'stereo'}],
                   'category': [(u'Biz', u''), (u'Fin', u'')],
                   'channel': u'C23robtv.zap2it.com',
                   'date': [u'2003'],
                   'start': u'20030702000000 ADT',
                   'stop': u'20030702003000 ADT',
                   'title': [(u'This Week in Business', u'')]},
                  {'audio': [{'stereo': u'stereo'}],
                   'category': [(u'Comedy', u'')],
                   'channel': u'C36wuhf.zap2it.com',
                   'country': [(u'USA', u'')],
                   'credits': [{'producer': [u'Larry David'], 'actor': [u'Jerry Seinfeld']}],
                   'date': [u'1995'],
                   'desc': [(u'In an effort to grow up, George proposes marriage to former girlfriend Susan.',
                             u'')],
                   'episode-num': [(u'7 . 1 . 1/1', u'xmltv_ns')],
                   'language': [(u'English', u'')],
                   'last-chance': [(u'Hah!', u'')],
                   'length': [{'units': u'minutes', 'length': 22}],
                   'new': [1],
                   'orig-language': [(u'English', u'')],
                   'premiere': [(u'Not really. Just testing', u'en')],
                   'previously-shown': [{'channel': u'C12whdh.zap2it.com',
                                         'start': u'19950921103000 ADT'}],
                   'rating': [{'icon': [{'height': u'64',
                                         'src': u'http://some.ratings/PGicon.png',
                                         'width': u'64'}],
                               'system': u'VCHIP',
                               'value': u'PG'}],
                   'star-rating': [{'icon': [{'height': u'32',
                                              'src': u'http://some.star/icon.png',
                                              'width': u'32'}],
                                    'value': u'4/5'}],
                   'start': u'20030702000000 ADT',
                   'stop': u'20030702003000 ADT',
                   'sub-title': [(u'The Engagement', u'')],
                   'subtitles': [{'type': u'teletext', 'language': (u'English', u'')}],
                   'title': [(u'Seinfeld', u'')],
                   'video': [{'colour': 1, 'aspect': u'4:3', 'present': 1}]}]

    channels = [{'display-name': [(u'Channel 10 ELTV', u'')],
                 'id': u'C10eltv.zap2it.com',
                 'url': [u'http://www.eastlink.ca/']},
                {'display-name': [(u'Channel 11 CBHT', u'en')],
                 'icon': [{'src': u'http://tvlistings2.zap2it.com/tms_network_logos/cbc.gif'}],
                 'id': u'C11cbht.zap2it.com'}]


    w = Writer(sys.stdout, encoding="iso-8859-1",
               date="20030811003608 -0300",
               source_info_url="http://www.funktronics.ca/python-xmltv",
               source_info_name="Funktronics",
               generator_info_name="python-xmltv",
               generator_info_url="http://www.funktronics.ca/python-xmltv")
    for c in channels:
        w.write_channel(c)
    for p in programmes:
        w.write_programme(p)
    w.end()
