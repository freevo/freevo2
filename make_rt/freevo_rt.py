import sys
import os
import imp

# Dependencies that we want the Installer to include in the
# package
import pygame
from pygame.locals import *
import Image
import imghdr
from xml.utils import qp_xml

# Automatically generated list of all system modules
import sysmodules

import iu
iu.ImportManager().install()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: %s <filename.py>' % sys.argv[0]
        sys.exit(0)

    print 'Running from %s' % sys.executable
    pildir = os.path.dirname(sys.executable) + '/PIL'
    maindir = os.path.dirname(sys.argv[1]) + './'
    
    sys.path = ['.', pildir, maindir] + sys.path
    
    print 'Will try to run "%s"' % sys.argv
    fd = open(sys.argv[1], 'r')
    mod = imp.load_source('__main__', sys.argv[1], fd)
    print 'Done in %s' % sys.argv[1]
