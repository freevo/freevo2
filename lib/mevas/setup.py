from distutils.core import setup, Extension
import os, sys, re

include_dirs = []
library_dirs = []
libraries    = []
ext_modules  = []

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


if check_config('imlib2', '1.1.1'):
    try:
        import pygame
        inc = re.sub("/(lib|lib64)/", "/include/", pygame.__path__[0]).replace("site-packages/", "")
        if not os.path.isdir(inc):
            raise ImportError
        if not check_config('sdl', '1.2.5'):
            raise ImportError
        include_dirs.append(inc)

        ext_modules.append(
            Extension("mevas.displays.mevas_pygame",
                ["mevas/displays/mevas_pygame.c"],
                library_dirs=library_dirs,
                include_dirs=include_dirs,
                libraries=libraries)
        )

    except ImportError:
        pass



setup(name="mevas", version="0.0.3",
	packages = ["mevas", "mevas.imagelib", "mevas.displays"],
    ext_modules = ext_modules
)
                                                                                
# vim: ts=4
