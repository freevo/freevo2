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
import string, popen2, fcntl, select, struct, fnmatch,re
import time
import threading
import fcntl
import md5

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config

# XML support
import movie_xml

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
                   os.path.basename(md5file(file)) + '-%s-%s.png' % (x0, y0))
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



########################################################################
# identify media stuff

PROC_MOUNT_REGEXP = re.compile("^([^ ]*) ([^ ]*) .*$").match

def proc_mount(dir):
    f = open('/proc/mounts')
    l = f.readline()
    while(l):
        m = PROC_MOUNT_REGEXP(l)
        if m:
            if m.group(2) == dir and m.group(1).encode() != 'none':
                f.close()
                return m.group(1).encode()
        l = f.readline()
    f.close()
    return None


LABEL_REGEXP = re.compile("^(.*[^ ]) *$").match

# returns (type, label, image, play_options)
def identifymedia(dir):

    # check if we need to update the database
    if os.path.exists("/tmp/freevo-rebuild-database"):
        movie_xml.hash_xml_database()
        
    mediatypes = [('VCD','/mpegav/', 'vcd'), ('SVCD','/SVCD/', 'vcd'), \
                  ('DVD','/video_ts/', 'dvd') ]

    image = title = None

    device = proc_mount(dir)
    if device:
        img = open(device)
        img.seek(0x0000832d)
        id = img.read(16)
        img.seek(32808, 0)
        label = img.read(32)
        m = LABEL_REGEXP(label)
        if m:
            label = m.group(1)
        img.close()
    else:
        return None, None, None, None

    if id in config.MOVIE_INFORMATIONS:
        title, image, xml_filename = config.MOVIE_INFORMATIONS[id]
            
    for media in mediatypes:
        if os.path.exists(dir + media[1]):
            if title:
                return media[0], title, image, (media[2], 1, [])
            return media[0], '%s [%s]' % (media[0], label), image, (media[2], 1, [])
        
    mplayer_files = match_files(dir, config.SUFFIX_MPLAYER_FILES)
    mp3_files = match_files(dir, config.SUFFIX_AUDIO_FILES)
    image_files = match_files(dir, config.SUFFIX_AUDIO_FILES)
    
    if mplayer_files and not mp3_files:

        # return the title and action is play
        if title and len(mplayer_files) == 1:
            # XXX add mplayer_options, too
            return 'DIVX', title, image, ('video', mplayer_files[0], [])

        # return the title
        if title:
            return 'DIVX', title, image, None

        # only one movie on DVD/CD, title is movie name and action is play
        if len(mplayer_files) == 1:
            title = string.capitalize(os.path.splitext(os.path.basename(mplayer_files[0]))[0])
            return 'DIVX', title, image, ('video', mplayer_files[0], [])

        # try to find out if it is a series cd
        show_name = ""
        the_same  = 1
        volumes   = ''
        for movie in mplayer_files:
            if config.TV_SHOW_REGEXP_MATCH(movie):
                show = config.TV_SHOW_REGEXP_SPLIT(os.path.basename(movie))

                if show_name and show_name != show[0]: the_same = 0
                if not show_name: show_name = show[0]
                if volumes: volumes += ', '
                volumes += show[1] + "x" + show[2]

        if show_name and the_same:
            if os.path.isfile((config.TV_SHOW_IMAGES + show_name + ".png").lower()):
                image = (config.TV_SHOW_IMAGES + show_name + ".png").lower()
            elif os.path.isfile((config.TV_SHOW_IMAGES + show_name + ".jpg").lower()):
                image = (config.TV_SHOW_IMAGES + show_name + ".jpg").lower()
            return "DIVX", show_name + ' ('+ volumes + ')', image, None

        # nothing found, return the label
        return "DIVX", 'CD [%s]' % label, None, None

    if not mplayer_files and mp3_files:
        return "MP3" , 'CD [%s]' % label, None, None

    if not mplayer_files and not mp3_files and image_files:
        return "IMAGE", 'CD [%s]' % label, None, None
    
    if mplayer_files or image_files or mp3_files:
        if title:
            return 'DATA', title, image, None
        return "DATA", 'CD [%s]' % label, None, None

    return "AUDIO", 'CD [%s]' % label, None, None


