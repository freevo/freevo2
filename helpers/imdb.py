#!/usr/bin/env python
#if 0 /*
# -----------------------------------------------------------------------
# imdbp.py - IMDB helper script to generate fxd files
# -----------------------------------------------------------------------
# $Id$
#
# Notes:
#
# Todo:        
#
# -----------------------------------------------------------------------
# $Log$
# Revision 1.23  2003/06/24 18:12:45  dischi
# fixed string translation with urllib (not urllib2)
#
# Revision 1.22  2003/06/24 16:15:07  dischi
# o updated by den_RDC - changed code to urllib2 - exceptions are handled by
#   urllib2, including 302 redirection -- proxy servers ,including transparant
#   proxies now work
# o added support for better image finder. Right now there we can also get
#   posters from www.impawards.com
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

import re
import urllib, urllib2, urlparse
import sys
import string
import codecs
import os

freevo_version = '1.3.2'

imdb_title_list = '/tmp/imdb-movies.list'
imdb_title_list_url = 'ftp://ftp.funet.fi/pub/mirrors/ftp.imdb.com/pub/movies.list.gz'
imdb_titles = None

# headers for urllib2
txdata = None
txheaders = {   
    'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform),
    'Accept-Language': 'en-us',
}

def getCDID(drive):
    """
    return a unique identifier for the disc
    """

    try:
        img = open(drive)
        img.seek(0x0000832d)
        id = img.read(16)
        img.seek(32808, 0)
        label = img.read(32)
        
        LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match
        m = LABEL_REGEXP(label)
    except IOError:
        print 'no disc in drive %s' % drive
        sys.exit(2)
        
    if m:
        label = m.group(1)
    img.close()
    return id+label
    

def str2XML(line):
    """
    make the string XML valid
    """

    try:
        # s = unicode(string.replace(line, "&", "&amp;"), 'latin-1')
        s = unicode(line, 'latin-1')
        while s[-1] == ' ':
            s = s[:-1]
        if s[:4] == '&#34':
            s = s[5:]
        if s[-4:] == '#34;':
            s = s[:-5]
        return s
    except:
        return line
    

def search(name):
    """
    search imdb title database for the given name
    """

    results = []

    url = 'http://us.imdb.com/Tsearch?title=%s&restrict=Movies+and+TV' % urllib.quote(name)
    req = urllib2.Request(url, txdata, txheaders)

    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        print error 
        return results
        
    regexp_title = re.compile('.*<LI><A HREF="/Title\?([0-9]*)">(.*) '+
                               '\(([12][0-9][0-9][0-9].*)\)</A>')

    regexp_type  = re.compile('<H2><A NAME=.*>(.*)</A></H2>')
    
    type = ''

    for line in response.read().split("\n"):
        m = regexp_type.match(line)
        if m:
            type = m.group(1)
            if type == 'Movies':
                type = 'Movie'
            elif type == 'TV-Movies':
                type = 'TV-Movie'

        m = regexp_title.match(line)

        if m and not type == 'Video Games':
            id   = m.group(1)
            name = m.group(2)
            year = m.group(3)

            if name[0] == '"' and name [-1] == '"':
                name=name[1:-1]
            if year.find(')') > 0:
                year = year[:year.find(')')]

            for i in range(len(results)):
                if results[i][0] == id:
                    results[i] = ( id , name, year, type )
                    break
            else:
                results += [ ( id , name, year, type ) ]
    return results


imdb_info_tags = ('year', 'genre', 'tagline', 'plot', 'rating', 'runtime');
image_url_handler = {}

def get_data(id):
    """
    get imdb data about the movie with the given id
    """

    title = ''
    info = {}

    for t in imdb_info_tags:
        info[t] = ""

    image_urls = []
    dvd = 0
    
    regexp_title   = re.compile('.*STRONG CLASS="title">(.*?)<', re.I)
    regexp_year    = re.compile('.*<A HREF="/Sections/Years/.*?([0-9]*)<', re.I)
    regexp_genre   = re.compile('.*href="/Sections/Genres(.*)$', re.I)
    regexp_tagline = re.compile('.*<B CLASS="ch">Tagline.*?</B>(.*?)<', re.I)
    regexp_plot1   = re.compile('.*<B CLASS="ch">Plot Outline.*?</B>(.*?)<', re.I)
    regexp_plot2   = re.compile('.*<B CLASS="ch">Plot Summary.*?</B>(.*?)<', re.I)
    regexp_rating  = re.compile('.*<B>([0-9\.]*)/10</B> (.[0-9,]* votes.?)', re.I)
    regexp_image   = re.compile('.*ALT="cover".*src="(http://.*?)"', re.I)
    regexp_runtime = re.compile('.*<b class="ch">Runtime', re.I)
    regexp_dvd     = re.compile('.*<a href="/DVD\?', re.I)

    regexp_dvd_image = re.compile('.*(http://images.amazon.com.*?ZZZZZ.*?)"')
    regexp_url   = re.compile('.*href="(http.*?)"', re.I)

    url = 'http://us.imdb.com/Title?%s' % id
    req = urllib2.Request(url, txdata, txheaders)
    
    try:
        r = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        print error
        return None

    next_line_is = None

    for line in r.read().split("\n"):
        if next_line_is == 'runtime':
            next_line_is = None
            info['runtime'] = str2XML(line)

        if regexp_runtime.match(line):
            next_line_is = 'runtime'
            continue

        m = regexp_title.match(line)
        if m: title = str2XML(m.group(1))

        m = regexp_year.match(line)
        if m: info['year'] = m.group(1)

        m = regexp_genre.match(line)
        if m:
            for g in re.compile(' *</A>.*?> *', re.I).split(' </a>'+line+' > '):
                if info['genre'] == "": info['genre'] = g
                elif g != "" and g != "(more)": info['genre'] += " / "+ g


        m = regexp_tagline.match('%s<' % line)
        if m:
            info['tagline'] = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])

        m = regexp_plot1.match('%s<' % line)
        if m: info['plot'] = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])

        m = regexp_plot2.match('%s<' % line)
        if m: info['plot'] = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])

        m = regexp_rating.match(line)
        if m: info['rating'] = m.group(1) + '/10 ' + m.group(2)

        m = regexp_dvd.match(line)
        if m: dvd = 1

        m = regexp_image.match(line)
        if m: image_urls += [ m.group(1) ]

    if dvd:

        url = 'http://us.imdb.com/DVD?%s' % id
        req = urllib2.Request(url, txdata, txheaders)
        
        try:
            r = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print error
            return None

        for line in r.read().split("\n"):

            m = regexp_dvd_image.match(line)
            if m: image_urls += [ m.group(1) ]

    global image_url_handler
    if not image_url_handler:
        return (title, info, image_urls)

    url = 'http://us.imdb.com/Posters?%s' % id
    req = urllib2.Request(url, txdata, txheaders)
        
    try:
        r = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        print error
        return (title, info, image_urls)

    for line in r.read().split("\n"):
        m = regexp_url.match(line)
        if m:
            url = urlparse.urlsplit(m.group(1))
            if url[0] == 'http' and image_url_handler.has_key(url[1]):
                image_urls += image_url_handler[url[1]](url[1], url[2])

    return (title, info, image_urls)



def download_image(url, filename):
    """
    download a cover image
    """

    # hack for amazon images
    url = re.compile('MZZZZZ').sub('LZZZZZ', url)

    # split host and file
    url = re.compile('http://(.*?)/(.*)$').match(url)

    # get the image
    url = (url.group(1), url.group(2))

    req = urllib2.Request('http://' + url[0] + '/' + url[1], txdata, txheaders)
    try:
        r = urllib2.urlopen(req)
    except urllib2.HTTPError, error:
        print "Image download failed"
        print error
        return None
        
    i = open(filename, 'w')
    i.write(r.read())
    i.close()

    # try to crop the image to avoid borders by imdb and unidented tot return
    try:
        import Image
        image = Image.open(filename)
        width, height = image.size
        image.crop((2,2,width-4, height-4)).save(filename)
    except:
        pass
    return url[0]
  

def print_video(file, part):
    if file[:3]== 'dvd':
        return "        <dvd  id=\"p%s\" media-id=\"%s\">%s</dvd>\n" % \
               (part, getCDID(drive), file[3:])
    elif file[:3] == 'vcd':
        return "        <vcd  id=\"p%s\" media-id=\"%s\">%s</vcd>\n" % \
               (part, getCDID(drive), file[3:])


    # FIXME: ismount doesn't mean it's a rom drive !!!!
    #
    # elif os.path.ismount(os.path.dirname(file)):
    #     return "        <file id=\"p%s\" media-id=\"%s\">%s</file>\n" % \
    #            (part, getCDID(drive), str2XML(os.path.basename(file)))

    else:
        return "        <file id=\"p%s\">%s</file>\n" % \
               (part, str2XML(file))

def print_image(filename, image_url):
    image = '%s.jpg' % filename
    if os.path.exists(image):
        image = re.compile('^.*/').sub("", str(filename)) + '.jpg'
        if image_url:
            return "    <cover-img source=\"%s\">%s</cover-img>\n" % \
                   (str2XML(image_url), str2XML(image))
        else:
            return "    <cover-img>%s</cover-img>\n" % str2XML(image)
    return ''

def print_info(info):
    ret = ''
    if info:
        ret = '    <info>\n'
        for k in info.keys():
            ret += '      <%s>%s</%s>\n' % (k,info[k],k)
        ret += '    </info>\n'
    return ret


def write_fxd(imdb_number, filename, drive, image_url, type, files, cdid, imdb_data):
    """
    write the infos to the xml file
    """

    title, info, None = imdb_data
    
    i = codecs.open('%s.fxd' % filename, 'w', encoding='utf-8')
    i.write("<?xml version=\"1.0\" ?>\n<freevo>\n")
    i.write("  <copyright>\n" +
            "    The information in this file are from the Internet " +
            "Movie Database (IMDb).\n" +
            "    Please visit http://www.imdb.com for more informations.\n")
    i.write("    <source url=\"http://www.imdb.com/Title?%s\"/>\n"  % imdb_number +
            "  </copyright>\n")

    if cdid:
        i.write("  <disc-set title=\"%s\">\n" % str2XML(title))
        i.write(print_image(filename, image_url))
        i.write(print_info(info))
        i.write("    <disc media-id=\"%s\"/>\n" % getCDID(drive))
        i.write("  </disc-set>\n")
            
    if files:
        i.write("  <movie title=\"%s\">\n" % str2XML(title))
        i.write(print_image(filename, image_url))

        part = 1
        i.write("    <video>\n")
        for file in files:
            i.write(print_video(file, part))
            part += 1
        i.write("    </video>\n")

        i.write(print_info(info))
        i.write("  </movie>\n")

    i.write("</freevo>\n")

    os.system('touch /tmp/freevo-rebuild-database')



def get_data_and_write_fxd(imdb_number, filename, drive, type, files, cdid):
    """
    get imdb data and store it into the xml database
    """

    imdb_data = get_data(imdb_number)
    if not imdb_data:
        print 'getting info for id=%s failt' % imdb_number
        return 0

    (title, info, image_url_list) = imdb_data

    image_file = '%s.jpg' % filename
    image_url = None
    
    if not os.path.exists(image_file):
        for url in image_url_list:
            tmp = download_image(url, image_file)
            if tmp:
                image_url = tmp
                try:
                    import Image
                    if Image.open(image_file).size[0] > 180:
                        break
                    print 'image seems to small, try to get a better one'
                except:
                    break
                
    if image_url:
        print "Downloaded cover image from %s" % image_url
        print "Freevo knows nothing about the copyright of this image, please"
        print "go to %s to check for more informations about private." % image_url
        print "use of this image"

    # Now write the output file
    write_fxd(imdb_number, filename, drive, image_url, type, files, cdid, imdb_data)
    return 1



def parse_file_args(input):
    files = []
    cdid  = []
    for i in input:
        if i == 'dvd' or i == 'vcd' or i == 'cd':
            cdid += [ i ]
        else:
            files += [ i ]
    return files, cdid


    
def add(fxd_file, files):
    """
    open the fxd file and add the disc id of the disc in drive 'drive'
    to the database.
    """

    files, sets = parse_file_args(files)
    
    x = open(fxd_file+'.fxd')
    content = x.read()
    x.close()

    regexp_file = re.compile(' *.file.*id.*/file', re.I)
    regexp_dvd  = re.compile(' *.dvd.*id.*/dvd', re.I)
    regexp_vcd  = re.compile(' *.vcd.*id.*/vcd', re.I)

    regexp_video_end  = re.compile(' *</video>', re.I)
    regexp_set_end    = re.compile(' *./disc-set', re.I)

    x = open(fxd_file+'.fxd', 'w')

    part = 1
    for line in content.split('\n'):
        if regexp_file.match(line) or regexp_dvd.match(line) or regexp_vcd.match(line):
            part += 1

        if regexp_video_end.match(line):
            for file in files:
                x.write(print_video(file, part))
                part += 1

        if regexp_set_end.match(line):
            for i in sets:
                x.write("    <disc media-id=\"%s\"/>\n" % getCDID(drive))
                
        x.write(line+'\n')

    x.close()
    os.system('touch /tmp/freevo-rebuild-database')



def point_maker(matching):
    return '%s.%s' % (matching.groups()[0], matching.groups()[1])


def load_imdb_titles():
    movie_data = re.compile('^.*[12][0-9][0-9][0-9]$', re.I)
    data = []
    try:
        for line in open(imdb_title_list).readlines():
            if movie_data.match(line):
                data.append(' %s ' % line[:-1])
    except IOError:
        return None
    return data

    
def local_search(name):
    global imdb_titles

    name  = os.path.basename(os.path.splitext(name)[0])
    name  = re.sub('([a-z])([A-Z])', point_maker, name)
    name  = re.sub('([a-zA-Z])([0-9])', point_maker, name)
    name  = re.sub('([0-9])([a-zA-Z])', point_maker, name.lower())
    parts = re.split('[\._ -]', name)

    if imdb_titles == None:
        imdb_titles = load_imdb_titles()

    matches = imdb_titles

    if matches == None:
        return None
    
    title = ''
    
    for p in parts:
        if p and p != 'and':
            new_match = []
            if p[0] == '(' and p[-1] == ')':
                r = re.compile('^.*%s' % p[1:-1], re.I)
            else:
                r = re.compile('^.*[ :",-]%s[ :",-].*[12][0-9][0-9][0-9]' % p +
                               '.*[12][0-9][0-9][0-9]', re.I)

            for line in matches:
                if r.match(line):
                    new_match.append(line)

            if new_match:
                title = '%s %s' % (title, p)
                matches = new_match

    return title


def find_best_match(title, matches):
    best  = ''
    count = 10000
    for line in matches:
        val = 0
        for part in re.split(' ', title):
            if part and part[0] == '(' and part[-1] == ')':
                part = part[1:-1]
                
            if not re.search(part, line, re.I):
                val += 2
                
        val += len(re.split(' ', re.split('\(', line)[0]))

        if re.search('\(.*Movie.*\)', line):
            val -= 2
            
        if  val < count:
            count = val
            best = line

    return best

def guess(filename):
    print "searching " + filename
    keys = local_search(filename)
    if keys == None:
        print 'Local database not found. Please download movies.list.gz'
        print 'from the imdb interface website, unpack it and move it to'
        print '%s.' % imdb_title_list
        print 'To get the file go to http://www.imdb.com/interfaces'
        sys.exit(1)

    print 'keywords: %s' % keys
    data = []
    for result in search(keys):
        data.append('%s   %s (%s)' % (result[0], result[1], result[2]))
    match = find_best_match(filename, data)
    print 'best match: %s' % match
    imdb_number = match[:7]
    files = [ filename ]
    filename = os.path.splitext(filename)[0]
    get_data_and_write_fxd(imdb_number, filename, drive, type, files, '')


def usage():
    print 'imdb.py -s string:   search imdb for string'
    print
    print 'imdb.py [--rom-drive=/path/to/rom/drive] nr output files'
    print '  Generate output.fxd for the movie.'
    print '  Files is a list of files that belongs to this movie.'
    print '  Use [dvd|vcd] to add the whole disc or use [dvd|vcd][title]'
    print '  to add a special DVD or VCD title to the list of files'
    print
    print 'imdb.py [--rom-drive=/path/to/rom/drive] -a fxd-file files'
    print '  add files to fxd-file.fxd'
    print
    sys.exit(1)



def impawards(host, path):
    """
    parser for posters from www.impawards.com. TODO: check for licences
    of each poster and add all posters
    """
    path = '%s/posters/%s.jpg' % (path[:path.rfind('/')], \
                                  path[path.rfind('/')+1:path.rfind('.')])
    return [ 'http://%s%s' % (host, path) ]




image_url_handler['www.impawards.com'] = impawards






#
# Main function
#
if __name__ == "__main__":
    import getopt

    drive = '/dev/cdrom'

    task = ''
    search_arg = ''
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'ag:s:', ('rom-drive=','list-guess='))
    except getopt.GetoptError:
        usage()
        pass
    
    for o, a in opts:
        if o == '-a':
            if task:
                usage()
            task = 'add'

        if o == '-s':
            if task:
                usage()
            task = 'search'
            search_arg = a

        if o == '-g':
            if task:
                usage()
            task = 'guess'
            search_arg = a

        if o == '--list-guess':
            if task:
                usage()
            task = 'list-guess'
            search_arg = a

        if o == '--rom-drive':
            drive=a

    if task == 'add':
        if len(args) < 2:
            usage()
        add(args[0], args[1:])
        sys.exit(0)

    if task == 'search':
        if len(args) != 0:
            usage()

        filename = search_arg
        print "searching " + filename
        for result in search(filename):
            if result[3]:
                print '%s   %s (%s, %s)' % result
            else:
                print '%s   %s (%s)' % (result[0], result[1], result[2])
        sys.exit(0)

    if task == 'list-guess':
        import fileinput
        for filename in fileinput.input(search_arg):
            try:
                # check for already existing .fxd file and skip if exists
                open(os.path.splitext(filename)[0] + '.fxd', 'r')
                print 'skipping %s. info already exists' % filename
                continue
            except IOError:
                pass

            guess(filename)

        sys.exit(0)

    if task == 'guess':
        if len(args) != 0:
            usage()

        guess(search_arg)
        sys.exit(0)
        
    # normal usage
    if len(args) < 2:
        usage()

    imdb_number = args[0]
    filename = args[1]


    files, cdid = parse_file_args(args[2:])

    if not (files or cdid):
        usage()
        
    get_data_and_write_fxd(imdb_number, filename, drive, type, files, cdid)
