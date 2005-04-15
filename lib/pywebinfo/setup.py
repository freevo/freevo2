#!/usr/bin/env python

"""Setup script for the pywebinfo distribution."""

__revision__ = "$Id$"

from distutils.core import setup, Extension

setup (# Distribution meta-data
       name = "pywebinfo",
       version = 0.1,
       description = "",
       author = "",
       author_email = "freevo-devel@lists.sourceforge.net",
       url = "http://freevo.sf.net",

       package_dir = {'pywebinfo': 'src'},
       packages    = ['pywebinfo',
                      'pywebinfo.movie', 
                      'pywebinfo.audio',
                      'pywebinfo.lib',
                      'pywebinfo.rss',
                      'pywebinfo.weather',
                      'pywebinfo.images',
                      ],
      )
