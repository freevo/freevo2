#!/usr/bin/python
#
import os
import urllib2
import cStringIO
import Image
import sys

if len(sys.argv) > 1:	
	imgsrc = sys.argv[1]
	# Get the file into a fp
	fp = urllib2.urlopen(str(imgsrc))
	# Make a seekable file object
	img = cStringIO.StringIO(fp.read())
	# Convert the image
	if len(sys.argv) < 3:
		output_file = 'cover.png'
	else:
		output_file = sys.argv[2]
	Image.open(img).save(output_file)
else:
	print "Usage: %s [URL] <output file>" % sys.argv[0]
	print "Grab a cover image via HTTP, optionally convert it to JPG/PNG format"
	print "if no <output_file> is specified, convert and write to 'cover.png'"
	# Technically, we can convert to a lot more formats, but Freevo doesn't use them

