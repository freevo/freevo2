# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# main.py - This is the Freevo main application code
# -----------------------------------------------------------------------------
# $Id$
#
# This file is the python start file for Freevo. It handles the init phase like
# checking the python modules, loading the plugins and starting the main menu.
#
# It also contains the splashscreen and the skin chooser.
#
# First edition: Krister Lagerstrom <krister-freevo@kmlager.com>
# Maintainer: Dirk Meyer <dmeyer@tzi.de>
#
# -----------------------------------------------------------------------------
# Freevo - A Home Theater PC framework
# Copyright (C) 2002-2004 Krister Lagerstrom, Dirk Meyer, et al. 
# Please see the file freevo/Docs/CREDITS for a complete list of authors.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

# python imports
import os
import sys, time
import traceback
import signal

try:
    import notifier
except ImportError:
    print 'This version of freevo requires pyNotifier 0.2.0rc1 or newer!'
    print 'You can find the current release at:'
    print 'http://www.crunchy-home.de/download/'
    sys.exit( 1 )
    
# init notifier
notifier.init( notifier.GENERIC )
    
# i18n support

# First load the xml module. It's not needed here but it will mess
# up with the domain we set (set it from freevo 4Suite). By loading it
# first, Freevo will override the 4Suite setting to freevo

try:
    from xml.utils import qp_xml
    from xml.dom import minidom
    
    # now load other modules to check if all requirements are installed
    import Image
    try:
        import twisted
    except ImportError, e:
        print e
    import Numeric
    
    import config
    import system

    try:
        import Imlib2
    except:
        print 'The python Imlib2 bindings could not be loaded!'
        print 'Maybe you did not install Imlib2.'
        print 'You can find Imlib2 at: http://enlightenment.org'
        sys.exit( 1 )

    if config.OSD_DISPLAY == 'SDL':
        import pygame

    if not config.CONF.lsdvd:
        print
        print 'Can\'t find lsdvd. DVD support will be limited and maybe not'
        print 'all discs are detected. Please install lsdvd, you can get it'
        print 'from http://acidrip.thirtythreeandathird.net/lsdvd.html'
        print
        print 'After installing it, you should run \'freevo cache --rebuild\''
    else:
        os.environ['LSDVD'] = config.CONF.lsdvd
        
    import mmpython

    
except ImportError, i:
    print 'Can\'t find all Python dependencies:'
    print i
    if str(i)[-7:] == 'Numeric':
        print 'You need to recompile pygame after installing Numeric!'
    print
    print 'Not all requirements of Freevo are installed on your system.'
    print 'Please check the INSTALL file for more informations.'
    print
    sys.exit(0)


# check if mmpython is up to date to avoid bug reports
# for already fixed bugs
try:
    import mmpython.version
    if mmpython.version.CHANGED < 20040629:
        raise ImportError
except ImportError:
    print 'Error: Installed mmpython version is too old.'
    print 'Please update mmpython to version 0.4.3 or higher'
    print
    sys.exit(0)

# freevo imports
import eventhandler
import gui
import util
import menu

from item import Item
from event import *
from cleanup import shutdown
from gui.areas import Area


class SkinSelectItem(Item):
    """
    Item for the skin selector
    """
    def __init__(self, parent, name, image, skin):
        Item.__init__(self, parent)
        self.name  = name
        self.image = image
        self.skin  = skin

        
    def actions(self):
        """
        Return the select function to load that skin
        """
        return [ ( self.select, '' ) ]


    def select(self, arg=None, menuw=None):
        """
        Load the new skin and rebuild the main menu
        """
        # load new theme
        theme = gui.theme_engine.set_base_fxd(self.skin)
        # set it to the main menu as used theme
        pos = menuw.menustack[0].theme = theme
        # and go back
        menuw.back_one_menu()


class MainMenu(Item):
    """
    This class handles the main menu
    """
    def getcmd(self):
        """
        Setup the main menu and handle events (remote control, etc)
        """
        import plugin
        menuw = menu.MenuWidget()
        items = []
        for p in plugin.get('mainmenu'):
            items += p.items(self)

        for i in items:
            i.is_mainmenu_item = True

        mainmenu = menu.Menu(_('Freevo Main Menu'), items, item_types='main',
                             umount_all = 1)
        mainmenu.item_types = 'main'
        mainmenu.theme = gui.get_theme()
        menuw.pushmenu(mainmenu)
        menuw.show()
        

    def get_skins(self):
        """
        return a list of all possible skins with name, image and filename
        """
        ret = []
        skindir = os.path.join(config.SKIN_DIR, 'main')
        skin_files = util.match_files(skindir, ['fxd'])

        # image is not usable stand alone
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/image.fxd'))
        skin_files.remove(os.path.join(config.SKIN_DIR, 'main/basic.fxd'))
        
        for skin in skin_files:
            name  = os.path.splitext(os.path.basename(skin))[0]
            if os.path.isfile('%s.png' % os.path.splitext(skin)[0]):
                image = '%s.png' % os.path.splitext(skin)[0]
            elif os.path.isfile('%s.jpg' % os.path.splitext(skin)[0]):
                image = '%s.jpg' % os.path.splitext(skin)[0]
            else:
                image = None
            ret += [ ( name, image, skin ) ]
        return ret


    def eventhandler(self, event = None, menuw=None, arg=None):
        """
        Automatically perform actions depending on the event, e.g. play DVD
        """
        # pressing DISPLAY on the main menu will open a skin selector
        # (only for the new skin code)
        if event == MENU_CHANGE_STYLE:
            items = []
            for name, image, skinfile in self.get_skins():
                items += [ SkinSelectItem(self, name, image, skinfile) ]

            menuw.pushmenu(menu.Menu(_('Skin Selector'), items))
            return True

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)
        
    

class Splashscreen(Area):
    """
    A simple splash screen for osd startup
    """
    def __init__(self, text):
        Area.__init__(self, 'content')
        self.pos          = 0
        self.bar_border   = gui.theme_engine.Rectangle(color=(0,0,0), size=2)
        self.bar_position = gui.theme_engine.Rectangle(bgcolor=(0,0,0,95))
        self.text         = text
        self.content      = []
        self.bar          = None
        self.engine       = gui.AreaHandler('splashscreen', ('screen', self))
        self.engine.show()

        
    def clear(self):
        """
        clear all content objects
        """
        for c in self.content:
            c.unparent()
        self.content = []
        if self.bar:
            self.bar.unparent()
            self.bar = None
            
        
    def update(self):
        """
        update the splashscreen
        """
        content   = self.calc_geometry(self.layout.content, copy_object=True)

        x0, x1 = content.x, content.x + content.width
        y = content.y + content.font.font.height + content.spacing

        if not self.content:
            s = self.drawstring(self.text, content.font, content, height=-1,
                                align_h='center')
            b = self.drawbox(x0, y, x1-x0, 20, self.bar_border)
            self.content.append(s)
            self.content.append(b)

        pos = 0
        if self.pos:
            pos = round(float((x1 - x0 - 4)) / (float(100) / self.pos))
        if self.bar:
            self.bar.unparent()
        self.bar = self.drawbox(x0+2, y+2, pos, 16, self.bar_position)
        

    def progress(self, pos):
        """
        set the progress position and refresh the screen
        """
        self.pos = pos
        if self.engine:
            self.engine.draw(None)


    def hide(self):
        """
        fade out
        """
        self.engine.hide(config.OSD_FADE_STEPS)

        
    def destroy(self):
        """
        destroy the object
        """
        del self.engine



def signal_handler(sig, frame):
    """
    the signal handler to shut down freevo
    """
    if sig in (signal.SIGTERM, signal.SIGINT):
        shutdown(exit=True)



def tracefunc(frame, event, arg, _indent=[0]):
    """
    function to trace everything inside freevo for debugging
    """
    if event == 'call':
        filename = frame.f_code.co_filename
        funcname = frame.f_code.co_name
        lineno = frame.f_code.co_firstlineno
        if 'self' in frame.f_locals:
            try:
                classinst = frame.f_locals['self']
                classname = repr(classinst).split()[0].split('(')[0][1:]
                funcname = '%s.%s' % (classname, funcname)
            except:
                pass
        here = '%s:%s:%s()' % (filename, lineno, funcname)
        _indent[0] += 1
        tracefd.write('%4s %s%s\n' % (_indent[0], ' ' * _indent[0], here))
        tracefd.flush()
    elif event == 'return':
        _indent[0] -= 1

    return tracefunc




#
# Freevo main function
#

# parse arguments
if len(sys.argv) >= 2:

    # force fullscreen mode
    # deactivate screen blanking and set osd to fullscreen
    if sys.argv[1] == '-force-fs':
        os.system('xset -dpms s off')
        config.START_FULLSCREEN_X = 1

    # activate a trace function
    if sys.argv[1] == '-trace':
        tracefd = open(os.path.join(config.LOGDIR, 'trace.txt'), 'w')
        sys.settrace(tracefunc)
        config.DEBUG = 2

    # create api doc for Freevo and move it to Docs/api
    if sys.argv[1] == '-doc':
        import pydoc
        import re
        for file in util.match_files_recursively('src/', ['py' ]):
            # doesn't work for everything :-(
            if file not in ( 'src/tv/record_server.py', ) and \
                   file.find('src/www') == -1 and \
                   file.find('src/helpers') == -1:
                file = re.sub('/', '.', file)
                try:
                    pydoc.writedoc(file[4:-3])
                except:
                    pass
        try:
            os.mkdir('Docs/api')
        except:
            pass
        for file in util.match_files('.', ['html', ]):
            print 'moving %s' % file
            os.rename(file, 'Docs/api/%s' % file)
        print
        print 'wrote api doc to \'Docs/api\''
        shutdown(exit=True)



try:
    # signal handler
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    # load the fxditem to make sure it's the first in the
    # mimetypes list
    import fxditem

    # load all plugins
    import plugin
    import gui
    
    # prepare the skin
    gui.get_theme().prepare()

    # Fire up splashscreen and load the plugins
    splash = Splashscreen(_('Starting Freevo, please wait ...'))
    plugin.init(splash.progress)

    # Fire up splashscreen and load the cache
    if config.MEDIAINFO_USE_MEMORY == 2:
        # delete previous splash screen object
        splash.destroy()
        import util.mediainfo

        splash = Splashscreen(_('Reading cache, please wait ...'))

        cachefiles = []
        for type in ('video', 'audio', 'image', 'games'):
            if plugin.is_active(type):
                n = 'config.%s_ITEMS' % type.upper()
                x = eval(n)
                for item in x:
                    if os.path.isdir(item[1]):
                        cachefiles += [ item[1] ] + \
                                      util.get_subdirs_recursively(item[1])


        cachefiles = util.unique(cachefiles)

        for f in cachefiles:
            splash.progress(int((float((cachefiles.index(f)+1)) / \
                                 len(cachefiles)) * 100))
            util.mediainfo.load_cache(f)

    # fade out the splash screen
    splash.hide()
    
    # prepare again, now that all plugins are loaded
    gui.get_theme().prepare()

    # start menu
    MainMenu().getcmd()

    # Wait for the startup animation. This is a bad hack but we won't
    # be able to remove our splashscreen otherwise. Big FIXME!
    gui.animation.render().wait()

    # delete splash screen
    splash.destroy()
    del splash
    
    # Kick off the main menu loop
    _debug_('Main loop starting...',2)

    # FIXME
    import eventhandler
    notifier.addDispatcher( eventhandler.get_singleton().handle )

    import childapp
    notifier.addDispatcher( childapp.watcher.step )

    # start main loop
    notifier.loop()

    
except KeyboardInterrupt:
    print 'Shutdown by keyboard interrupt'
    # Shutdown the application
    shutdown()

except SystemExit:
    pass

except:
    print 'Crash!'
    try:
        tb = sys.exc_info()[2]
        fname, lineno, funcname, text = traceback.extract_tb(tb)[-1]

        if config.FREEVO_EVENTHANDLER_SANDBOX:
            secs = 5
        else:
            secs = 1
        # for i in range(secs, 0, -1):
        #     osd.clearscreen(color=osd.COL_BLACK)
        #     osd.drawstring(_('Freevo crashed!'), 70, 70)
        #     osd.drawstring(_('Filename: %s') % fname, 70, 130)
        #     osd.drawstring(_('Lineno: %s') % lineno, 70, 160)
        #     osd.drawstring(_('Function: %s') % funcname, 70, 190)
        #     osd.drawstring(_('Text: %s') % text, 70, 220)
        #     osd.drawstring(str(sys.exc_info()[1]), 70, 280)
        #     osd.drawstring(_('Please see the logfiles for more info'),
        #                    70, 350)
        #     osd.drawstring(_('Exit in %s seconds') % i, 70, 410)
        #     osd.update()
        #     time.sleep(1)
    except:
        pass
    traceback.print_exc()

    # Shutdown the application, but not the system even if that is
    # enabled
    shutdown()


# -----------------------------------------------------------------------------
# $Log$
# Revision 1.147  2004/10/06 19:24:00  dischi
# switch from rc.py to pyNotifier
#
# Revision 1.146  2004/10/03 16:09:27  dischi
# changes to a new header (proposal)
#
# Revision 1.145  2004/09/28 18:31:06  dischi
# check system auto detect
#
# Revision 1.144  2004/09/07 18:56:12  dischi
# internal colors are now lists, not int
#
# Revision 1.143  2004/09/02 00:12:46  rshortt
# Only import pygame is config.OSD_DISPLAY is 'SDL'.
#
# Revision 1.142  2004/08/24 19:23:36  dischi
# more theme updates and design cleanups
#
# Revision 1.141  2004/08/24 16:42:39  dischi
# Made the fxdsettings in gui the theme engine and made a better
# integration for it. There is also an event now to let the plugins
# know that the theme is changed.
#
# Revision 1.140  2004/08/23 20:37:52  dischi
# fading support in splash screen
#
# Revision 1.139  2004/08/22 20:16:22  dischi
# move splashscreen to new mevas based gui code
#
# Revision 1.138  2004/08/14 15:09:54  dischi
# use new AreaHandler
#
# Revision 1.137  2004/08/05 17:37:55  dischi
# remove a bad skin hack
#
# Revision 1.136  2004/08/01 10:57:59  dischi
# show menu application on startup
#
# Revision 1.135  2004/07/26 18:10:16  dischi
# move global event handling to eventhandler.py
#
# -----------------------------------------------------------------------------
