from distutils.core import setup, Extension
import os
import sys

files = ["epeg.c"]

include_dirs = []
library_dirs = []
libraries    = []

def check_config(name, minver):
    """
    Check dependencies add add the flags to include_dirs, library_dirs and
    libraries. The basic logic is taken from pygame.
    """
    command = name + '-config --version --cflags --libs 2>/dev/null'
    try:
        config = os.popen(command).readlines()
        if len(config) == 0:
            raise ValueError, 'command not found'
        flags  = (' '.join(config[1:]) + ' ').split()
        ver = config[0].strip()
        if minver and ver < minver:
            err= 'requires %s version %s (%s found)' % \
                 (name, minver, ver)
            raise ValueError, err
        for f in flags:
            if f[:2] == '-I':
                include_dirs.append(f[2:])
            if f[:2] == '-L':
                library_dirs.append(f[2:])
            if f[:2] == '-l':
                libraries.append(f[2:])
        return True
    except Exception, e:
        print 'WARNING: "%s-config" failed: %s' % (name, e)
        return False


if not check_config('epeg', '0.0.0'):
    sys.exit(1)

setup(name="epeg", version="0.0.1", 
      ext_modules=[Extension("epeg", 
                             files,
                             library_dirs=library_dirs,
                             include_dirs=include_dirs,
                             libraries=libraries)
                   ]
      )

# vim: ts=4
