#!/usr/bin/env python

"""Setup script for the freevo distribution."""


__revision__ = "$Id$"

# Python distutils stuff
import os
import sys
import time

# Freevo distutils stuff
sys.path.append('./src')
import version
from util.distribution import setup, Extension, check_libs, docbook_finder
from distutils import core


check_libs((('pygame', 'http://www.pygame.org'),
            ('Image', 'http://www.pythonware.com/products/pil/'),
            ('mbus', 'http://www.mbus.org/')))



data_files = []
# add some files to Docs
for f in ('COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__,
                       ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__,
                   ['Docs/CREDITS' ]))
data_files.append(('share/fxd', ['share/fxd/webradio.fxd']))

# copy freevo_config.py to share/freevo. It's the best place to put it
# for now, but the location should be changed
data_files.append(('share/freevo', [ 'freevo_config.py' ]))

# add docbook style howtos
os.path.walk('./Docs/installation', docbook_finder, data_files)
os.path.walk('./Docs/plugin_writing', docbook_finder, data_files)

# start script
scripts = ['freevo']

# now start the python magic
setup (name         = "freevo",
       version      = version.__version__,
       description  = "Freevo",
       author       = "Krister Lagerstrom, et al.",
       author_email = "freevo-devel@lists.sourceforge.net",
       url          = "http://www.freevo.org",
       license      = "GPL",

       i18n         = 'freevo',
       scripts      = scripts,
       data_files   = data_files,
       )
