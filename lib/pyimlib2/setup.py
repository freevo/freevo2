from distutils.core import setup, Extension
import os

files = ["imlib2.c", "image.c", "font.c", "rawformats.c", "display.c"]
includes = []
libs = ["Imlib2", "rt", "X11"]

config_h = open('config.h', 'w')

try:
    import pygame
    if not os.path.isdir('/usr/include/python2.3/pygame/'):
        raise ImportError
    print 'building pygame extention'
    includes += ['/usr/include/SDL', '/usr/include/python2.3/pygame/', '/usr/local/include/SDL']
    config_h.write('#define USE_PYGAME\n')
except ImportError:
    pass

config_h.close()

setup(name="_Imlib2", version="0.0.7", 
	ext_modules=[ 
		Extension("_Imlib2module", 
			files,
			library_dirs=["/usr/X11R6/lib"],
                        include_dirs=includes,
			libraries=libs)
	],
	py_modules=["Imlib2"]
)

# vim: ts=4
