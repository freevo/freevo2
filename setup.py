#!/usr/bin/env python

"""Setup script for the freevo distribution."""


# This is the first version of a real python setup script to install
# Freevo directly into the system. This script can't be used with
# the runtime, because the runtime contains it's own python.
#
# TODO:
# o add more needed libs to 'libs'
# o fix fbcon stuff in freevo_config.py. It looks for contrib/fbcon but
#   installed the scripts are somewhere else
# o test it on more platforms than mine


__revision__ = "$Id$"

from distutils.core import setup, Extension
import distutils.command.install
import os
import sys

libs = ( ('mmpython', 'http://www.sf.net/projects/mmpython' ),
         ('pygame', 'http://www.pygame.org') )

def package_finder(result, dirname, names):
    for name in names:
        if os.path.splitext(name)[1] == '.py':
            import_name = dirname.replace('/','.').replace('..src', 'freevo')
            result[import_name] = dirname
            return result
    return result

def data_finder(result, dirname, names):
    files = []
    for name in names:
        if os.path.isfile(os.path.join(dirname, name)):
            files.append(os.path.join(dirname, name))
    if files and dirname.find('/CVS') == -1:
        result.append((dirname.replace('./share', 'share/freevo').
                       replace('./contrib', 'share/freevo/contrib').\
                       replace('./helpers', 'share/freevo/helpers'), files))
    return result


package_dir = {}
os.path.walk('./src', package_finder, package_dir)
packages = []
for p in package_dir:
    packages.append(p)

data_files = []
os.path.walk('./share', data_finder, data_files)
os.path.walk('./contrib', data_finder, data_files)
os.path.walk('./helpers', data_finder, data_files)

# copy freevo_config.py to share/freevo. It's the best place to put it
# for now, but the location should be changed
data_files.append(('share/freevo', [ 'freevo_config.py' ]))

scripts = ['freevo']


# ok, this can't be done by setup it seems, so we have to do it
# manually
if len(sys.argv) > 1 and sys.argv[1].lower() == 'install':
    # check for needed libs
    for module, url in libs:
        print 'checking for %-13s' % (module+'...'),
        try:
            exec('import %s' % module)
            print 'found'
        except:
            print 'not found'
            print 'please download it from %s and install it' % url
            sys.exit(1)
            
#     # compile runapp
#     if os.environ.has_key('LOGDIR') and os.environ['LOGDIR']:
#         logdir='"%s"' % os.environ['LOGDIR']
#     else:
#         logdir='"/var/log/freevo"'
#     print 'building runapp'
#     os.system('gcc -O2 -Wall -static -o runapp runapp.c '
#               '-DRUNAPP_LOGDIR=\\"%s\\" -DDEBUG' % logdir)
#     # bad hack, this is no script, but it is compiled and
#     # ready to install now
#     scripts.append('runapp')


# now start the python magic
setup (name = "freevo",
       version = "1.3.4cvs",
       description = "Freevo",
       author = "Krister Lagerstrom, et al.",
       author_email = "",
       url = "http://freevo.sf.net",

       scripts=scripts,
       package_dir = package_dir,
       packages = packages,
       data_files = data_files
       )
