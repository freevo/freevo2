#!/bin/sh
#
# Stupid script to grab images from the net, and convert them
# into png cover logos on-the-fly. Accepts a URL as an option
# and writes a "cover.png" in the current directory.
#
# Requires imagemagick.

curl $1 | convert - cover.png
