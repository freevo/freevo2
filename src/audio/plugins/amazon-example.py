#!/usr/bin/python
#
# Pass a artist/album
#
import amazon

# Use keyword, rather than searchbyartist, because any artist with multiple albums
# doesn't appear to work

# Get a key from http://www.amazon.com/webservices
amazon.setLicense('...') # must get your own key!
cover = amazon.searchByKeyword('Brand New Your Favorite Weapon', product_line="music")
print cover[0].ImageUrlLarge
