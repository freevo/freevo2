#!/usr/bin/env python
  
"""Setup script for my freevo plugin."""
  
__revision__ = "$Id$"
  
from freevo.util.distribution import setup
  
# now start the python magic
setup (name = "insert-name-here",
       version = '0.1',
       description = "Full name of the plugin",
       author = "your name",
       author_email = "your mail address",
       url = "maybe a homepage"
       )
