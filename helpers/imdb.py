#!/usr/bin/env python

# usage:   imdb.py imdb-number out-filename moviefiles
# example: imdb.py 0120915 swep1 star.wars.episode1.avi


import re
import httplib, urllib
import sys
import string
import codecs
import os

freevo_version = '1.2.5'


#
# Return the CD ID for cd in the drive
#

LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match

def getCDID(drive):
    img = open(drive)
    img.seek(0x0000832d)
    id = img.read(16)
    img.seek(32808, 0)
    label = img.read(32)
    m = LABEL_REGEXP(label)
    if m:
        label = m.group(1)
    img.close()
    return id+label
    
#
# make the string XML valid
#

def str2XML(line):
    return unicode(string.replace(line, "&", "&amp;"), 'latin-1')
    

try:
    imdb_number = sys.argv[1]
    filename = sys.argv[2]
except IndexError:
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
# add ID tag to exiting XML file
#

if imdb_number == '--add-id':
    id = getCDID(filename)

    x = open(sys.argv[3])
    content = x.read()
    x.close()

    content = string.replace(content, "</title>", "</title>\n    <id>%s</id>" % id)
    x = open(sys.argv[3], 'w')
    x.write(content)
    x.close()
    os.system('touch /tmp/freevo-rebuild-database')
    sys.exit(0)



#
# Some init stuff
#
    
title = year = genre = tagline = plot = rating = image = ""

regexp_title   = re.compile('.*STRONG CLASS="title">(.*?)<')
regexp_year    = re.compile('.*<A HREF="/Sections/Years/.*?([0-9]*)<')
regexp_genre   = re.compile('.*<B CLASS="ch">Genre.*?</B>(.*)<BR>')
regexp_tagline = re.compile('.*<B CLASS="ch">Tagline.*?</B>(.*?)<')
regexp_plot    = re.compile('.*<B CLASS="ch">Plot Outline.*?</B>(.*?)<')
regexp_rating  = re.compile('.*<B>([0-9\.]*)</B>/10 (.[0-9]* votes.)')
regexp_image   = re.compile('.*(http.*?)" ALT="cover"')


# connect to IMDb 
conn = httplib.HTTPConnection("www.imdb.com")

# set user agent
headers = { 'User-Agent': 'freevo %s (%s)' % (freevo_version, sys.platform) }



#
# Search IMDb for a title
#

if imdb_number == '-s':
    print "searching " + filename

    params = urllib.urlencode({'select': "All", 'for': filename})
    conn.request("POST", "/Find", params, headers)
    response = conn.getresponse()

    regexp_title   = re.compile('.*<LI><A HREF="/Title\?([0-9]*)">(.*)</A></LI>')
    for line in response.read().split("\n"):
        m = regexp_title.match(line)
        if m:
            print m.group(1) + " " + m.group(2)
    sys.exit(0)


    # the /Sherlock? way, but it doesn't work
    conn.request("GET", "/Sherlock?"+filename, "", headers)
    r = conn.getresponse()
    if r.status != 200:
        print r.status
        print r.reason
        sys.exit(1)

    # this doesn't work, why????
    print r.read()



#
# Get and parse the information from the site
#

conn.request("GET", "/Title?"+imdb_number, "", headers)
r = conn.getresponse()
if r.status != 200:
    print r.status
    print r.reason
    sys.exit(1)
    
for line in r.read().split("\n"):

    m = regexp_title.match(line)
    if m: title = str2XML(m.group(1))

    m = regexp_year.match(line)
    if m: year = m.group(1)

    m = regexp_genre.match(line)
    if m:
        for g in re.compile(' *</A>.*?> *').split('</A>'+m.group(1)):
            if genre == "": genre = g
            elif g != "" and g != "(more)": genre += " / "+ g

    m = regexp_tagline.match(line)
    if m:
        tagline = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])
        
    m = regexp_plot.match(line)
    if m: plot = str2XML(re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:])
        
    m = regexp_rating.match(line)
    if m: rating = m.group(1) + '/10 ' + m.group(2)
        
    m = regexp_image.match(line)
    if m and not os.path.exists(filename + ".jpg"):
        # hack for amazon images
        url = re.compile('MZZZZZ').sub('LZZZZZ', m.group(1))

        # split host and file
        url = re.compile('http://(.*?)/(.*)$').match(url)

        # get the image
        conn = httplib.HTTPConnection(url.group(1))
        conn.request("GET", "/"+url.group(2), "", headers)
        r = conn.getresponse()
        if r.status == 200:
            print "Downloaded cover image from %s" % url.group(1)
            print "Freevo knows nothing about the copyright of this image, please"
            print "go to %s to check for more informations about private." % url.group(1)
            print "use of this image"
            i = open(filename + ".jpg", 'w')
            i.write(r.read())
            i.close()
            image = re.compile('^.*/').sub("", filename) + '.jpg'
            
        else:
            print "image download failed"
            print r.status
            print r.reason
        conn.close()


#
# Now write the output file
#

i = codecs.open(filename + ".xml", 'w', encoding='utf-8')
i.write( "\
<?xml version=\"1.0\" ?>\n\
<freevo>\n\
  <copyright>\n\
    The information in this file are from the Internet Movie Database (IMDb).\n\
    Please visit http://www.imdb.com for more informations.\n\
  </copyright>\n\
  <movie>\n\
    <title>"+title+"</title>\n")

index = 3

# insert ID?

try:
    if sys.argv[3] == "-id":
        i.write("    <id type=\"timestamp\">%s</id>\n" % getCDID(sys.argv[4]))
        index += 2
except IndexError:
    pass

# insert image?

if image:
    i.write("    <cover source=\"%s\">%s</cover>\n" % (url.group(1), str2XML(image)))



# insert filenames and video type

i.write("    <video>\n")

try:
    if sys.argv[index] == "-vcd":
        i.write("      <vcd/>\n")
        index = 0
    if sys.argv[index] == "-dvd":
        i.write("      <dvd/>\n")
        index = 0
    if sys.argv[3] == "-cd":
        i.write("      <cd/>\n")
        index += 1
except IndexError:
    pass

if index > 0:
    i.write  ("      <files>\n")

    try:
        while 1:
            i.write( "        <filename>"+str2XML(sys.argv[index])+"</filename>\n")
            index += 1
    except IndexError:
        pass

    i.write("      </files>\n")


# insert more IMDb info

i.write("\
    </video>\n\
    <info>\n\
      <url>http://us.imdb.com/Title?"+imdb_number+"</url>\n\
      <genre>"+genre+"</genre>\n\
      <year>"+year+"</year>\n\
      <tagline>"+tagline+"</tagline>\n\
      <plot>"+plot+"</plot>\n\
      <rating>"+rating+"</rating>\n\
    </info>\n\
  </movie>\n\
</freevo>\n")

i.close()

os.system('touch /tmp/freevo-rebuild-database')

