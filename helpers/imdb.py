#!/usr/bin/env python

# usage:   imdb.py imdb-number out-filename moviefiles
# example: imdb.py 0120915 swep1 star.wars.episode1.avi


import re
import httplib, urllib
import sys
import string

try:
    imdb_number = sys.argv[1]
    filename = sys.argv[2]
except IndexError:
    print "Usage: imdb.py [IMDB-NUMBER] [OUTPUT_FILE] [MOVIEFILE(S)]"
    print "       imdb.py -s [SEARCH_STRING]"
    print "       imdb.py -id [DRIVE] [XML_FILE]"
    print
    print "Generate XML data that stores extra IMDB information for use"
    print "in the movie browser."
    print
    print "IMDB_NUMBER:"
    print "  IMDB title number for this movie"
    print
    print "OUTPUT_FILE:"
    print "  The script will generate OUTPUT_FILE.xml fot the IMDB data"
    print "  and OUTPUT_FILE.jpg for the image (if possible)"
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
    print "-id [DRIVE] [XML_FILE]"
    print "  Stores the DVD/VCD/CD id to the XML file"
    sys.exit(1)


# add ID tag
if imdb_number == '-id':
    img = open(filename)
    img.seek(0x0000832d)
    id = img.read(16)
    img.seek(32808, 0)
    label = img.read(32)
    m = re.compile("^(.*[^ ]) *$").match(label)
    if m:
        label = m.group(1)
    img.close()
    print 'adding id=id%s' % id
    print label

    x = open(sys.argv[3])
    content = x.read()
    x.close()

    content = string.replace(content, "</title>", "</title>\n    <id>%s</id>" % id)
    x = open(sys.argv[3], 'w')
    x.write(content)
    x.close()
    sys.exit(0)
    
# connect to imdb 
conn = httplib.HTTPConnection("us.imdb.com")

# let's lie about the user agent, without user-agent the return is 403
headers = { 'User-Agent': 'Netscape 3.0' }

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


conn.request("GET", "/Title?"+imdb_number, "", headers)
r = conn.getresponse()
if r.status != 200:
    print r.status
    print r.reason
    sys.exit(1)
    
title = year = genre = tagline = plot = rating = image = ""

regexp_title   = re.compile('.*STRONG CLASS="title">(.*?)<')
regexp_year    = re.compile('.*<A HREF="/Sections/Years/.*?([0-9]*)<')
regexp_genre   = re.compile('.*<B CLASS="ch">Genre.*?</B>(.*)<BR>')
regexp_tagline = re.compile('.*<B CLASS="ch">Tagline.*?</B>(.*?)<')
regexp_plot    = re.compile('.*<B CLASS="ch">Plot Outline.*?</B>(.*?)<')
regexp_rating  = re.compile('.*<B>([0-9\.]*)</B>/10 (.[0-9]* votes.)')
regexp_image   = re.compile('.*(http.*?)" ALT="cover"')



for line in r.read().split("\n"):

    m = regexp_title.match(line)
    if m: title = m.group(1)

    m = regexp_year.match(line)
    if m: year = m.group(1)

    m = regexp_genre.match(line)
    if m:
        for g in re.compile(' *</A>.*?> *').split('</A>'+m.group(1)):
            if genre == "": genre = g
            elif g != "" and g != "(more)": genre += " / "+ g

    m = regexp_tagline.match(line)
    if m: tagline = re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:]
        
    m = regexp_plot.match(line)
    if m: plot = re.compile('[\t ]+').sub(" ", ' ' + m.group(1))[1:]
        
    m = regexp_rating.match(line)
    if m: rating = m.group(1) + '/10 ' + m.group(2)
        
    m = regexp_image.match(line)
    if m:
        # hack for amazon images
        url = re.compile('MZZZZZ').sub('LZZZZZ', m.group(1))

        # split host and file
        url = re.compile('http://(.*?)/(.*)$').match(url)

        # get the image
        conn = httplib.HTTPConnection(url.group(1))
        conn.request("GET", "/"+url.group(2), "", headers)
        r = conn.getresponse()
        if r.status == 200:
            i = open(filename + ".jpg", 'w')
            i.write(r.read())
            i.close()
            image = re.compile('^.*/').sub("", filename) + '.jpg'
            
        else:
            print "image download failed"
            print r.status
            print r.reason
        conn.close()


i = open(filename + ".xml", 'w')
i.write( "\
<?xml version=\"1.0\" ?>\n\
<freevo>\n\
  <movie>\n\
    <title>"+title+"</title>\n\
    <cover>"+image+"</cover>\n\
    <video>\n")

index = 3

try:
    if sys.argv[3] == "-vcd":
        i.write("      <vcd/>\n")
        index = 0
    if sys.argv[3] == "-dvd":
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
            i.write( "        <filename>"+sys.argv[index]+"</filename>\n")
            index += 1
    except IndexError:
        pass

    i.write("      </files>\n")

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
