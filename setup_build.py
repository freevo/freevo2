#
# config.py - python standalone configure script.
#
# This is an application that is executed by the "./configure" script
# after checking for python.
#
# $Id$
#

# XXX This file should probably be cleaned up to use functions instead.

import sys, os


#PYTHON_REQUIREDVERSION = '2.1'

#print 'checking for Python version >= %s...' % PYTHON_REQUIREDVERSION,
#if ((sys.version_info[0] < 2) or
#    ((sys.version_info[0] == 2) and (sys.version_info[1] < 1))):
#    args = (sys.version_info[0], sys.version_info[1], sys.version_info[2],
#            PYTHON_REQUIREDVERSION)
#    print '%s.%s.%s found, %s or later is required!' % args
#    sys.exit()
#else:
#    print 'found'
        

print 'checking for Python XML...',
try:
    import xml
except ImportError:
    print 'not found, required!'
    sys.exit()
else:
    print ' found'


print 'checking for qp_xml...',
try:
    from xml.utils import qp_xml
except ImportError:
    print 'not found, required!'
    sys.exit()
else:
    print 'found'
    

print 'checking for Python Imaging Library...',
try:
    import Image
except ImportError:
    print 'not found, required!'
    sys.exit()
else:
    print 'found'


# Build everything
# XXX add more config flags, creating config files for python and C, etc.
# XXX use getopt for interpreting the command line args
# XXX add --help
if len(sys.argv) > 1:
    if sys.argv[1] == '--osd=x11':
        buildops = 'x11'
    elif sys.argv[1] == '--osd=sdl':
        buildops = 'sdl'
    elif sys.argv[1] == '--osd=fb':
        buildops = ''
    else:
        print
        print 'Usage: ./configure [--osd=fb | --osd=x11 | --osd=sdl]'
        sys.exit()
else:
    print
    print 'Defaulting build to "--osd=fb"'
    buildops = ''
    

# First clean up from the last build, if any
print
print 'Cleaning up from previous build...',
os.system('make -f Makefile.in clean > /dev/null')
print 'done'

print 'Creating Makefile (buildops="%s")...' % buildops,

# Create a new Makefile
os.system('echo "all:\n\tmake -f Makefile.in %s" > Makefile' % buildops)

print 'done'

print
print 'Now you can type "make" to build and "make install" as root\n',
print 'to put the binaries into /usr/local/freevo or run them from here'
print
