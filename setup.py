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
import util.distutils

util.distutils.check_libs((('mmpython', 'http://www.sf.net/projects/mmpython' ),
                           ('pygame', 'http://www.pygame.org'),
                           ('Image', 'http://www.pythonware.com/products/pil/'),
                           ('twisted', 'http://www.twistedmatrix.com/')))


# check if everything is in place
if not os.path.isdir('./Docs/howto'):
    print 'Docs/howto not found. Looks like you are using the CVS version'
    print 'of Freevo. Please run ./autogen.sh first'
    sys.exit(0)

data_files = util.distutils.data_files

for f in ('BUGS', 'COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__, ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__, ['Docs/CREDITS' ]))

# copy freevo_config.py to share/freevo. It's the best place to put it
# for now, but the location should be changed
data_files.append(('share/freevo', [ 'freevo_config.py' ]))

scripts = ['freevo']

# now start the python magic
setup (name         = "freevo",
       version      = version.__version__,
       description  = "Freevo",
       author       = "Krister Lagerstrom, et al.",
       author_email = "freevo-devel@lists.sourceforge.net",
       url          = "http://www.freevo.org",
       license      = "GPL",

       scripts=scripts,
       package_dir = util.distutils.package_dir,
       packages = util.distutils.packages,
       data_files = data_files
       )

