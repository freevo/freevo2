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
	# Convert the image into a PNG and save to logos directory
	output_file = 'cover.png'
	Image.open(img).save(output_file)
