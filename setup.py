#!/usr/bin/env python

"""Setup script for the freevo distribution."""


# This is the first version of a real python setup script to install
# Freevo directly into the system. This script can't be used with
# the runtime, because the runtime contains it's own python.


__revision__ = "$Id$"

from distutils.core import setup, Extension
import distutils.command.install
import os
import sys

sys.path.append('./src')
import version

libs = ( ('mmpython', 'http://www.sf.net/projects/mmpython' ),
         ('pygame', 'http://www.pygame.org'),
         ('Image', 'http://www.pythonware.com/products/pil/'),
         ('twisted', 'http://www.twistedmatrix.com/') )


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
            if name != 'freevo.pot':
                files.append(os.path.join(dirname, name))
            
    if files and dirname.find('/CVS') == -1:
        result.append((dirname.replace('./share', 'share/freevo').
                       replace('./src/www', 'share/freevo').\
                       replace('./i18n', 'share/locale').\
                       replace('./contrib', 'share/freevo/contrib').\
                       replace('./Docs', 'share/doc/freevo-%s' % version.__version__).\
                       replace('./helpers', 'share/freevo/helpers'), files))
    return result

# check if everything is in place
if not os.path.isdir('./Docs/howto'):
    print 'Docs/howto not found. Looks like you are using the CVS version'
    print 'of Freevo. Please run ./autogen.sh first'
    sys.exit(0)

# create list of source files
package_dir = {}
os.path.walk('./src', package_finder, package_dir)
packages = []
for p in package_dir:
    packages.append(p)

# create list of data files (share)
data_files = []
os.path.walk('./share', data_finder, data_files)
os.path.walk('./contrib/fbcon', data_finder, data_files)
os.path.walk('./contrib/xmltv', data_finder, data_files)
os.path.walk('./src/www/htdocs', data_finder, data_files)
os.path.walk('./i18n', data_finder, data_files)
os.path.walk('./Docs/howto', data_finder, data_files)

for f in ('BUGS', 'COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__, ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__, ['Docs/CREDITS' ]))

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
            

# now start the python magic
setup (name = "freevo",
       version = version.__version__,
       description = "Freevo",
       author = "Krister Lagerstrom, et al.",
       author_email = "",
       url = "http://freevo.sf.net",

       scripts=scripts,
       package_dir = package_dir,
       packages = packages,
       data_files = data_files
       )

