#!/usr/bin/env python

"""Setup script for the freevo distribution."""


__revision__ = "$Id$"

# Python distutils stuff
from distutils.core import setup, Extension
import os
import sys

# Freevo distutils stuff
sys.path.append('./src')
import version
from util.distutils import *

check_libs((('mmpython', 'http://www.sf.net/projects/mmpython' ),
            ('pygame', 'http://www.pygame.org'),
            ('Image', 'http://www.pythonware.com/products/pil/'),
            ('twisted', 'http://www.twistedmatrix.com/')))


# check if everything is in place
if (not os.path.isdir('./Docs/installation/html')) and \
   (len(sys.argv) < 2 or sys.argv[1].lower() not in ('i18n', '--help', '--help-commands')):
    print 'Docs/howto not found. Looks like you are using the CVS version'
    print 'of Freevo. Please run ./autogen.sh first'
    sys.exit(0)

# add some files to Docs
for f in ('BUGS', 'COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__, ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__, ['Docs/CREDITS' ]))

# copy freevo_config.py to share/freevo. It's the best place to put it
# for now, but the location should be changed
data_files.append(('share/freevo', [ 'freevo_config.py' ]))

# add docbook style howtos
os.path.walk('./Docs/installation', docbook_finder, data_files)
os.path.walk('./Docs/plugin_writing', docbook_finder, data_files)

# i18n support
i18n('freevo')

scripts = ['freevo']

# now start the python magic
setup (name         = "freevo",
       version      = version.__version__,
       description  = "Freevo",
       author       = "Krister Lagerstrom, et al.",
       author_email = "freevo-devel@lists.sourceforge.net",
       url          = "http://www.freevo.org",
       license      = "GPL",

       scripts      =scripts,
       package_dir  = package_dir,
       packages     = packages,
       data_files   = data_files
       )

finalize()
