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
import string, popen2, fcntl, select, struct
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
    
def makeNonBlocking(fd):

    # XXX Ugly hack to work around Python <2.2 which doesn't
    # XXX have these constants, but I don't want to require
    # XXX people to upgrade Python in addition to everything
    # XXX else
    f_setfl = 4
    f_getfl = 3
    fndelay = 04000
    #fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fl = fcntl.fcntl(fd, f_getfl)
    try:
	#fcntl.fcntl(fd, fcntl.F_SETFL, fl | 04000)
	fcntl.fcntl(fd, f_setfl, fl | 04000)
    except AttributeError:
	#fcntl.fcntl(fd, fcntl.F_SETFL, fl | FCNTL.FNDELAY)
	fcntl.fcntl(fd, f_setfl, fl | fndelay)


# Why were we doing this?
#try:
#	fp = open('log.txt', 'a', 0)
#except IOError:
#	fp = open('/dev/null','a')

write_lock = threading.Lock()

def log(str):
    global write_lock, fp
    write_lock.acquire()
    fp.write(str + '\n')
    write_lock.release()

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

def resize(file,x0=25,y0=25):
	import Image
	# Since the filenames are not unique we need
	# to cache them by content, not name.
	# Cache the thumbnails
	# thumbnail file is checksum.png
	mythumb = config.FREEVO_CACHEDIR + os.path.basename(md5file(file)) + '.png'
	if os.path.isfile(mythumb):
		return mythumb
	else:
		im = Image.open(file)
		im_res = im.resize((x0,y0))
		im_res.save(mythumb,'PNG')
		return mythumb
