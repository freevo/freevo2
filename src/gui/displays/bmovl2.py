import time

import mevas
from mevas.displays.mplayercanvas import MPlayerCanvas
from mevas.bmovl2 import MPlayerOverlay

import config

class Display(MPlayerCanvas):
    def __init__(self, size, default=False):
        self.start_video = default
        MPlayerCanvas.__init__(self, size)
        if default:
            print
            print 'Activating bmovl2 output'
            print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
            print
            self.mplayer_overlay = MPlayerOverlay()
            self.mplayer_args = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                                "expand=%s:%s,bmovl2=%s "\
                                "-loop 0 -font /usr/share/mplayer/fonts/"\
                                "font-arial-28-iso-8859-2/font.desc" % \
                                ( config.CONF.width, config.CONF.width,
                                  config.CONF.height, self.mplayer_overlay.fifo_fname )
            self.child = None
            self.show()

    def restart(self):
        _debug_('restart bmovl2')
        if self.start_video and not self.child:
            import childapp
            arg = ['/local/install/mplayer-cvs/mplayer'] + self.mplayer_args.split(' ') + \
            #arg = ['/home/tack/src/main/mplayer'] + self.mplayer_args.split(' ') + \
                  [config.BMOVL_OSD_VIDEO]
            self.child = childapp.ChildApp2(arg)
            time.sleep(2)
            self.mplayer_overlay.set_can_write(True)
            while 1:
                if self.mplayer_overlay.can_write():
                    break
            self.set_overlay(self.mplayer_overlay)
            self.rebuild()
            
    def stop(self):
        _debug_('stop bmovl2')
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None
            
    def hide(self):
        _debug_('hide bmovl2')
        self.stop()


    def show(self):
        _debug_('show bmovl2')
        self.restart()

