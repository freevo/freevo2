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


check_libs((('mmpython', 'http://www.sf.net/projects/mmpython' ),
            ('pygame', 'http://www.pygame.org'),
            ('Image', 'http://www.pythonware.com/products/pil/'),
            ('mbus', 'http://www.mbus.org/')))


print 'WARNING, CVS is unstable right now, press C-c to quit'
print 'If you really want to install freevo, make sure you also install'
print 'the libs in the lib dir'
print
print 'Waiting 5 seconds'
time.sleep(5)

class Runtime(core.Command):

    description     = "download and install runtime"
    user_options    = []
    boolean_options = []
    help_options    = []
    negative_opt    = {}

    def initialize_options (self):
        pass
    
    def finalize_options (self):
        pass

    def download(self, package):
        """
        download a package from sourceforge
        """
        url  = 'http://osdn.dl.sourceforge.net/sourceforge/' + package
        file = package[package.rfind('/')+1:]
        ddir = os.path.join(os.environ['HOME'], '.freevo/dist')
	if not os.path.isdir(ddir):
	    os.system('mkdir -p %s' % ddir)
        full = os.path.join(ddir, file)
        if not os.path.isfile(full):
            print 'Downloading %s' % file
            os.system('wget %s -O %s' % (url, full))
        if not os.path.isfile(full):
            print
            print 'Failed to download %s' % file
            print
            print 'Please download %s from http://www.sf.net/projects/%s' % \
                  (file, package[:package.find('/')])
            print 'and store it as %s' % full
            print
            sys.exit(0)
        return full


    def mmpython_install(self, result, dirname, names):
        """
        install mmpython into the runtime
        """
        for n in names:
            source = os.path.join(dirname, n)
            if dirname.find('/') > 0:
                destdir = dirname[dirname.find('/')+1:]
            else:
                destdir = ''
            dest   = os.path.join('runtime/lib/python2.3/site-packages',
                                  'mmpython', destdir, n)
            if os.path.isdir(source) and not os.path.isdir(dest):
                os.mkdir(dest)
            if n.endswith('.py') or n == 'mminfo':
                if n == 'dvdinfo.py':
                    # runtime contains a bad hack version of dvdinfo
                    # the normal one doesn't work
                    continue
                os.system('mv "%s" "%s"' % (source, dest))
        
    def run (self):
        """
        download and install the runtime + current mmpython
        """
        mmpython = self.download('mmpython/mmpython-%s.tar.gz' % version.mmpython)
        runtime  = self.download('freevo/freevo-runtime-%s.tar.gz' % version.runtime)
        print 'Removing runtime directory'
        os.system('rm -rf runtime')
        print 'Unpacking runtime'
        os.system('tar -zxf %s' % runtime)
        print 'Unpacking mmpython'
        os.system('tar -zxf %s' % mmpython)
        print 'Installing mmpython into runtime'
        os.path.walk('mmpython-%s' % version.mmpython, self.mmpython_install, None)
        os.system('rm -rf mmpython-%s' % version.mmpython)

    
# check if everything is in place
if (not os.path.isdir('./Docs/installation/html')) and \
   (len(sys.argv) < 2 or sys.argv[1].lower() not in ('i18n', '--help', '--help-commands')):
    print 'Docs/howto not found. Looks like you are using the CVS version'
    print 'of Freevo. Please run ./autogen.sh first'
    sys.exit(0)

# only add files not in share and src

data_files = []
# add some files to Docs
for f in ('BUGS', 'COPYING', 'ChangeLog', 'INSTALL', 'README'):
    data_files.append(('share/doc/freevo-%s' % version.__version__, ['%s' % f ]))
data_files.append(('share/doc/freevo-%s' % version.__version__, ['Docs/CREDITS' ]))
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
       cmdclass     = { 'runtime': Runtime }
       )
