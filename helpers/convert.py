#!/usr/bin/python
#
import os
import urllib2
import cStringIO
import Image
import sys
import urlparse

# Overfeatured :) but it's a good replacement for installing ImageMagick just for
# the conversion feature, which is about the only thing from ImageMagick I even
# used. 
#
# Technically, it does more than imagemagick, since it supports HTTP urls as well
# as actual files

FILETYPES=('ARG', 'BMP', 'CUR', 'DCX', 'EPS', 'FLI', 'FPX', 'GBR', 'GIF', 'ICO',
			'IM', 'IMT', 'IPTC', 'JPEG', 'MCIDAS', 'MIC', 'MPEG', 'MSP', 'PCD', 
			'PCX', 'PDF', 'PIXAR', 'PNG', 'PPM', 'PSD', 'SGI', 'SUN', 'TGA', 
			'TIFF', 'WMF', 'XVTHUMB', 'XBM', 'XPM')

if len(sys.argv) > 1:	
	imgsrc = sys.argv[1]
	output_file = sys.argv[2]
	if (urlparse.urlparse(imgsrc)[0] == 'http'):
		# use the get method
		# Get the file into a fp
		print "Grabbing image via HTTP:"
		fp = urllib2.urlopen(str(imgsrc))	
		# Make a seekable file object
		img = cStringIO.StringIO(fp.read())
		# Convert the image
	else:
		img = imgsrc
	try: 
		print "Converting %s to %s" % (sys.argv[1], sys.argv[2])
		Image.open(img).save(output_file)
	except IOError:
		sys.exit('Cannot identify input file; image header corrupt or missing')
else:
	print "Usage: %s <input_file> <output file>" % sys.argv[0]
	print "Take an input file and convert it to any PIL supported"
	print "format. This currently includes:"
	print
	for file in FILETYPES: print "%s" % file
