#!/usr/bin/env python

import os
import sys
from fcntl import ioctl

if len(sys.argv)>1 and sys.argv[1] == '--help':
    print 'release the vt in case freevo crashed and still locks'
    print 'the framebuffer.'
    print
    print 'this script has no options'
    print
    sys.exit(0)

# set ioctl (tty, KDSETMODE, KD_TEXT)
try:
    fd = os.open('/dev/tty0', os.O_RDONLY | os.O_NONBLOCK)
    try:
        ioctl(fd, 0x4B3A, 0)
    except:
        pass
    os.close(fd)
except:
    pass
