#
# util.py
#
# This file contains utility functions for Freevo
#
# $Id$

import sys
import socket, glob
import random
import termios, tty, time, os
import string, popen2, fcntl, select, struct, fnmatch
import time
import threading
import fcntl
import md5

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config


#
# Get all subdirectories in the given directory
#
#
def getdirnames(dir):
    files = glob.glob(dir + '/*')
    dirnames = filter(lambda d: os.path.isdir(d), files)
    dirnames.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return dirnames


#
# Find all files in a directory that matches a list of glob.glob() rules.
# It returns a list that is case insensitive sorted.
#
def match_files(dir, suffix_list):
    files = []
    for suffix in suffix_list:
        files += glob.glob(dir + suffix)
    files.sort(lambda l, o: cmp(l.upper(), o.upper()))
    return files
    

# Helper function for the md5 routine; we don't want to
# write filenames that aren't in lower ascii so we uhm,
# hexify them.
def hexify(str):
	hexStr = string.hexdigits
	r = ''
	for ch in str:
		i = ord(ch)
		r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
	return r


# Python's bundled MD5 class only acts on strings, so
# we have to calculate it in this loop
def md5file(file):
	m = md5.new()
	f = open(file, 'r')
	for line in f.readlines():
		m.update(line)
	f.close()
	return hexify(m.digest())
    

# Simple Python Imaging routine to return image size
# and return a default if the Imaging library is not
# installed.
def pngsize(file):
    if not os.path.isfile(file):
        return 200,200
    import Image
    image = Image.open(file)
    width, height = image.size
    return width,height


def resize(file, x0=25, y0=25):
	import Image
	# Since the filenames are not unique we need
	# to cache them by content, not name.
	mythumb = (config.FREEVO_CACHEDIR + '/' +
                   os.path.basename(md5file(file)) + '.png')
	if os.path.isfile(mythumb):
		return mythumb
	else:
		im = Image.open(file)
		im_res = im.resize((x0,y0))
		im_res.save(mythumb,'PNG')
		return mythumb

def getExifThumbnail(file, x0=0, y0=0):
    import Image

    # EXIF parser
    import exif

    f=open(file, 'rb')
    tags=exif.process_file(f)
    
    if tags.has_key('JPEGThumbnail'):
        thumb_name='%s/image-viewer-thumb.jpg' % config.FREEVO_CACHEDIR
        open(thumb_name, 'wb').write(tags['JPEGThumbnail'])
        if x0 >0 :
            return resize(thumb_name, x0, y0)
        return thumb_name
        
    if tags.has_key('TIFFThumbnail'):
        print "TIFF thumbnail not supported yet"

    
def recursefolders(root, recurse=0, pattern='*', return_folders=0):
	# Before anyone asks why I didn't use os.path.walk; it's simple, 
	# os.path.walk is difficult, clunky and doesn't work right in my
	# mind. 
	#
	# Here's how you use this function:
	#
	# songs = recursefolders('/media/Music/Guttermouth',1,'*.mp3',1):
	# for song in songs:
	#	print song	
	#
	# Should be easy to add to the mp3.py app.

	# initialize
	result = []

	# must have at least root folder
	try:
		names = os.listdir(root)
	except os.error:
		return result

	# expand pattern
	pattern = pattern or '*'
	pat_list = string.splitfields( pattern , ';' )
	
	# check each file
	for name in names:
		fullname = os.path.normpath(os.path.join(root, name))

		# grab if it matches our pattern and entry type
		for pat in pat_list:
			if fnmatch.fnmatch(name, pat):
				if os.path.isfile(fullname) or (return_folders and os.path.isdir(fullname)):
					result.append(fullname)
				continue
				
		# recursively scan other folders, appending results
		if recurse:
			if os.path.isdir(fullname) and not os.path.islink(fullname):
				result = result + recursefolders( fullname, recurse, pattern, return_folders )
			
	return result
