#!/usr/bin/env python

"""Setup script for the pyepg distribution."""

__revision__ = "$Id$"

from distutils.core import setup, Extension

setup (# Distribution meta-data
       name = "pyepg",
       version = 0.1,
       description = "",
       author = "",
       author_email = "freevo-devel@lists.sourceforge.net",
       url = "http://freevo.sf.net",

       package_dir = {'pyepg': ''},

       packages = [ 'pyepg' ],
      )

