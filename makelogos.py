#!/usr/bin/python
#
import xmltv
import config
import os
import urllib2
import cStringIO
import Image

# Check if the logos directory exists, if not, make it before
# proceeding

if not os.path.isdir(config.TV_LOGOS):
        print "Logo directory does not exist\n"
        print "Creating: %s\n" % (config.TV_LOGOS)
        os.mkdir(config.TV_LOGOS)

x = xmltv.read_channels(open(config.XMLTV_FILE))

for i in x:
        try:
                imgsrc = i['icon'][0]['src']
        except KeyError:
                imgsrc = None
        channel = i['id']
        #print '%s - %s' % (imgsrc,channel)
        if imgsrc != None:
                # Get the file into a fp
                fp = urllib2.urlopen(str(imgsrc))
                # Make a seekable file object
                img = cStringIO.StringIO(fp.read())
                # Convert the image into a PNG and save to logos directory
                output_file = config.TV_LOGOS + '/' + channel + '.png'
                Image.open(img).save(output_file)

