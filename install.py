import sys
import os

REQUIREDVERSION="2.1"

print "Checking Python Version:"
if sys.version_info[0] < 2:
	print "Your system is running python %s.%s.%s, %s or later is required." % (sys.version_info[0],sys.version_info[1],sys.version_info[2],REQUIREDVERSION)


print "Checking for Python XML:"
try:
	import xml
except ImportError:
	print "Python XML module is missing."

print "Checking for Python Imaging Library:"
try:
	import Image
except ImportError:
	print "Python Imaging library is missing."

print "Checking for Python fChecksum Library:"
try:
	import fchksum
except ImportError:
	print "Python Checksum module is missing."

# Build everything

if len(sys.argv) > 1:
	if sys.argv[1] == 'x11':
		buildops = 'x11'
	else:
		buildops = ''
else:
	buildops = ''

print "Building Freevo Binaries..."
os.system('make %s > /dev/null' % buildops)
print "Done. Now you can type make install to put the binaries"
print "into /usr/local/freevo or run them from here\n"

