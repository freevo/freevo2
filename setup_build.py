#
# config.py - python standalone configure script.
#
# This is an application that is executed by the "./configure" script
# after checking for python.
#
# $Id$
#

import sys, os


def check_deps():
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


makefile = """
all:
\tmake -f Makefile.in %s

install:
\tmake -f Makefile.in install

clean:
\tmake -f Makefile.in clean
"""

def create_makefile(buildops):

    # First clean up from the last build, if any
    print
    print 'Cleaning up from previous build...',
    os.system('make -f Makefile.in clean > /dev/null')
    print 'done'

    print 'Creating Makefile (buildops="%s")...' % buildops,

    # Create a new Makefile

    os.system('echo "%s" > Makefile' % (makefile % buildops))

    print 'done'

    
def print_usage():
    print 'Usage: ./configure [--osd=fb | --osd=x11 | --osd=sdl | --osd=dxr3]'

    
if __name__ == '__main__':

    if len(sys.argv) >= 2 and sys.argv[1] == '--help':
        print_usage()
        sys.exit()

    check_deps()
    
    # Build everything
    # XXX add more config flags, creating config files for python and C, etc.
    # XXX use getopt for interpreting the command line args
    # XXX add --help
    if len(sys.argv) > 1:
        if sys.argv[1] == '--osd=x11':
            buildops = 'x11'
        elif sys.argv[1] == '--osd=sdl':
            buildops = 'sdl'
        elif sys.argv[1] == '--osd=dxr3':
            buildops = 'dxr3'
        elif sys.argv[1] == '--osd=fb':
            buildops = ''
        else:
            print_usage()
            sys.exit()
    else:
        print
        print 'Defaulting build to "--osd=fb"'
        buildops = ''

    create_makefile(buildops)
    
    print
    print 'Now you can type "make" to build and "make install" as root'
    print 'to put the binaries into /usr/local/freevo or run them from here'
    print
