from distutils.core import setup, Extension
import os
import sys

files = ["imlib2.c", "image.c", "font.c", "rawformats.c"]

include_dirs = []
library_dirs = []
libraries    = ['rt']

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


if not check_config('imlib2', '1.1.1'):
    sys.exit(1)


config_h = open('config.h', 'w')

try:
    import pygame
    inc = pygame.__path__[0]
    inc = inc[:inc.rfind('site-packages')] + 'pygame'
    inc = inc[:inc.rfind('/lib/')] + '/include' + inc[inc.rfind('/lib/')+4:]
    if not os.path.isdir(inc):
        raise ImportError
    if not check_config('sdl', '1.2.5'):
        raise ImportError
    print 'pygame extention enabled'
    include_dirs.append(inc)
    config_h.write('#define USE_PYGAME\n')
except ImportError:
    print 'pygame extention disabled'

if 'X11' in libraries:
    files.append('display.c')
    config_h.write('#define USE_IMLIB2_DISPLAY\n')
else:
    print 'Imlib2 compiled without X11, deactivation imlib2 display'
    
config_h.close()

setup(name="_Imlib2", version="0.0.7", 
	ext_modules=[ 
		Extension("_Imlib2module", 
			files,
			library_dirs=library_dirs,
                        include_dirs=include_dirs,
			libraries=libraries)
	],
	py_modules=["Imlib2"]
)

# vim: ts=4
