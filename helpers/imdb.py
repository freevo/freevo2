#!/usr/bin/env python


import re
import httplib, urllib
import sys
import string
import codecs
import os

freevo_version = '1.3.0'


def getCDID(drive):
    """
    return a unique identifier for the disc
    """
    
    img = open(drive)
    img.seek(0x0000832d)
    id = img.read(16)
    img.seek(32808, 0)
    label = img.read(32)
    
    LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match
    m = LABEL_REGEXP(label)

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
        return s
    except:
        return line
    

def add_id(drive, xml_file):
    """
    open the xml file and add the disc id of the disc in drive 'drive'
    to the database.
    """
    
    id = getCDID(drive)

    x = open(xml_file)
    content = x.read()
    x.close()

    content = string.replace(content, "</title>", "</title>\n    <id>%s</id>" % id)
    x = open(sys.argv[3], 'w')
    x.write(content)
    x.close()
    os.system('touch /tmp/freevo-rebuild-database')
    sys.exit(0)


def search(name):
    """
    search imdb title database for the given name
    """

    conn = httplib.HTTPConnection("www.imdb.com")
    headers = { 'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform) }

    results = []
    params = urllib.urlencode({'title': name, 'restrict': 'Movies and TV'})

    conn.request("GET", '/Tsearch?%s' % params, params, headers)
    response = conn.getresponse()

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
    

def get_data(id):
    """
    get imdb data about the movie with the given id
    """
    
    title = year = genre = tagline = plot = rating = runtime = ""
    image_urls = []
    dvd = 0
    
    regexp_title   = re.compile('.*STRONG CLASS="title">(.*?)<', re.I)
    regexp_year    = re.compile('.*<A HREF="/Sections/Years/.*?([0-9]*)<', re.I)
    regexp_genre   = re.compile('.*href="/Sections/Genres(.*)$', re.I)
    regexp_tagline = re.compile('.*<B CLASS="ch">Tagline.*?</B>(.*?)<', re.I)
    regexp_plot    = re.compile('.*<B CLASS="ch">Plot Outline.*?</B>(.*?)<', re.I)
    regexp_rating  = re.compile('.*<B>([0-9\.]*)/10</B> (.[0-9,]* votes.?)', re.I)
    regexp_image   = re.compile('.*ALT="cover".*src="(http://.*?)"', re.I)
    regexp_runtime = re.compile('.*<b class="ch">Runtime', re.I)
    regexp_dvd     = re.compile('.*<a href="/DVD\?', re.I)

    regexp_dvd_image = re.compile('.*(http://images.amazon.com.*?ZZZZZ.*?)"')

    # connect to IMDb 
    conn = httplib.HTTPConnection("www.imdb.com")

    # set user agent
    headers = { 'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform) }


    #
    # Get and parse the information from the site
    #
    
    conn.request("GET", "/Title?"+id, "", headers)
    r = conn.getresponse()
    if r.status != 200:
        print r.status
        print r.reason
        return None

    next_line_is = None

    for line in r.read().split("\n"):
        if next_line_is == 'runtime':
            next_line_is = None
            runtime = str2XML(line)

        if regexp_runtime.match(line):
            next_line_is = 'runtime'
            continue

        m = regexp_title.match(line)
        if m: title = str2XML(m.group(1))

        m = regexp_year.match(line)
        if m: year = m.group(1)

        m = regexp_genre.match(line)
        if m:
            for g in re.compile(' *</A>.*?> *', re.I).split(' </a>'+line+' > '):
                if genre == "": genre = g
                elif g != "" and g != "(more)": genre += " / "+ g


        m = regexp_tagline.match(line)
        if m:
            tagline = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])

        m = regexp_plot.match(line)
        if m: plot = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])

        m = regexp_rating.match(line)
        if m: rating = m.group(1) + '/10 ' + m.group(2)

        m = regexp_dvd.match(line)
        if m: dvd = 1

        m = regexp_image.match(line)
        if m: image_urls += [ m.group(1) ]

    if dvd:
        conn.request("GET", "/DVD?"+id, "", headers)
        r = conn.getresponse()
        if r.status != 200:
            print r.status
            print r.reason
            return None

        for line in r.read().split("\n"):

            m = regexp_dvd_image.match(line)
            if m: image_urls += [ m.group(1) ]
            
    return (title, year, genre, tagline, plot, rating, image_urls, runtime)



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

    conn = httplib.HTTPConnection(url[0])
    headers = { 'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform) }
    conn.request("GET", "/"+url[1], "", headers)
    r = conn.getresponse()
    if r.status == 200:
        i = open(filename, 'w')
        i.write(r.read())
        i.close()
        conn.close()
        return url[0]

    else:
        print "image download failed"
        print r.status
        print r.reason
        conn.close()
        return None
    

def write_xml(filename, id, image_url, type, files, imdb_data):
    """
    write the infos to the xml file
    """

    title, year, genre, tagline, plot, rating, None, runtime = imdb_data
    
    i = codecs.open(filename + ".xml", 'w', encoding='utf-8')
    i.write("<?xml version=\"1.0\" ?>\n<freevo>\n")
    i.write("  <copyright>\n" +
            "    The information in this file are from the Internet Movie Database (IMDb).\n" +
            "    Please visit http://www.imdb.com for more informations.\n" +
            "  </copyright>\n")

    i.write("  <movie>\n    <title>"+title+"</title>\n")

    if id:
        i.write("    <id type=\"timestamp\">%s</id>\n" % id)

    image = filename + ".jpg"
    if os.path.exists(image):
        image = re.compile('^.*/').sub("", filename) + '.jpg'

    if image_url:
        i.write("    <cover source=\"%s\">%s</cover>\n" % (str2XML(image_url),
                                                           str2XML(image)))
    else:
        i.write("    <cover>%s</cover>\n" % str2XML(image))


    # insert filenames and video type

    i.write("    <video>\n\
      <mplayer_options></mplayer_options>\n")

    if type:
        i.write("      <%s/>\n" % type)

    if not type or type == 'cd':
        i.write  ("      <files>\n")
        for file in files:
            i.write( "        <filename>"+str2XML(file)+"</filename>\n")
        i.write("      </files>\n")


    # insert more IMDb info

    i.write("    </video>\n    <info>\n      <url>http://us.imdb.com/Title?"+
            imdb_number+"</url>\n")

    if genre:
        i.write("      <genre>"+genre+"</genre>\n")
    if year:
        i.write("      <year>"+year+"</year>\n")
    if runtime:
        i.write("      <runtime>"+runtime+"</runtime>\n")
    if tagline:
        i.write("      <tagline>"+tagline+"</tagline>\n")
    if plot:
        i.write("      <plot>"+plot+"</plot>\n")
    if rating:
        i.write("      <rating>"+rating+"</rating>\n")

    i.write("    </info>\n  </movie>\n</freevo>\n")
    i.close()

    os.system('touch /tmp/freevo-rebuild-database')



def get_data_and_write_xml(imdb_number, filename, id, files):
    """
    get imdb data and store it into the xml database
    """

    imdb_data = get_data(imdb_number)
    if not imdb_data:
        print 'getting info for id=%s failt' % imdb_number
        return 0

    (title, year, genre, tagline, plot, rating, image_url_list, runtime) = imdb_data

    image_file = filename + ".jpg"
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
    write_xml(filename, id, image_url, type, files, imdb_data)
    return 1



def usage():
    print "Usage: imdb.py [IMDB-NUMBER] [OUTPUT_FILE] [-id DRIVE] [MOVIEFILE(S)]"
    print "       imdb.py -s [SEARCH_STRING]"
    print "       imdb.py --add-id [DRIVE] [XML_FILE]"
    print
    print "Generate XML data that stores extra IMDB information for use"
    print "in the movie browser."
    print
    print "IMDB_NUMBER:"
    print "  IMDB title number for this movie"
    print
    print "OUTPUT_FILE:"
    print "  The script will generate OUTPUT_FILE.xml for the IMDB data"
    print "  and OUTPUT_FILE.jpg for the image (if possible)"
    print
    print "-id [DRIVE]"
    print "  Stores the DVD/VCD/CD id to the XML file"
    print
    print "MOVIE_FILE(S):"
    print "  One or more files belonging to this movie"
    print "  -dvd or -vcd to generate data for a DVD or VCD."
    print "  -cd MOVIEFILES(S) if the files are stored on a cd. Please"
    print "   give a relative path to the files from the cd mount point"
    print
    print "-s [SEARCH_STRING]"
    print "  Search IMDB to get the IMDB_NUMBER"
    print
    print "--add-id [DRIVE] [XML_FILE]"
    print "  Adds the DVD/VCD/CD id to the XML file"
    sys.exit(1)







#
# Main function
#
if __name__ == "__main__":

    try:
        # add ID tag to exiting XML file
        if sys.argv[1] == '--add-id':
            add_id(sys.argv[2], sys.argv[3])

        # Search IMDb for a title
        if sys.argv[1] == '-s':
            filename = sys.argv[2]
            print "searching " + filename
            for result in search(filename):
                print '%s   %s (%s, %s)' % result
            sys.exit(0)

        # normal usage
        imdb_number = sys.argv[1]
        filename = sys.argv[2]

    except IndexError:
        usage()

    index = 3

    try:
        id = ''
        if sys.argv[3] == "-id":
            id = getCDID(sys.argv[4])
            index += 2
    except IndexError:
        pass


    try:
        type = ''
        if sys.argv[index] == "-vcd":
            type = 'vcd'
            index = 0
        if sys.argv[index] == "-dvd":
            type = 'dvd'
            index = 0
        if sys.argv[3] == "-cd":
            type = 'cd'
            index += 1
    except IndexError:
        pass


    files = []
    if index > 0:
        try:
            while 1:
                files += [ sys.argv[index] ]
                index += 1
        except IndexError:
            pass

    get_data_and_write_xml(imdb_number, filename, id, files)
