#
# util.py
#
# This file contains utility functions for Freevo
#
import sys
import socket
import random
import termios, tty, time, os
import string, popen2, fcntl, select, struct
import time
import threading
import fcntl

# Configuration file. Determines where to look for AVI/MP3 files, etc
import config


def strip_suffix(str):
    pos = str.rfind('.')
    if pos == -1:
        return str
    else:
        return str[0:pos]
    
    
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



fp = open('log.txt', 'a', 0)

write_lock = threading.Lock()

def log(str):
    global write_lock, fp
    write_lock.acquire()
    fp.write(str + '\n')
    write_lock.release()
