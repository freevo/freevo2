import mevas
from mevas.displays.bmovlcanvas import BmovlCanvas

import config

class Display(BmovlCanvas):
    def __init__(self, size, default=False):
        self.start_video = default
        if default:
            print
            print 'Activating skin bmovl output'
            print 'THIS IS A TEST, DO NOT USE ANYTHING EXCEPT MENUS'
            print
            self.mplayer_args = "-subfont-text-scale 15 -sws 2 -vf scale=%s:-2,"\
                                "expand=%s:%s,bmovl=1:0:/tmp/bmovl "\
                                "-loop 0 -font /usr/share/mplayer/fonts/"\
                                "font-arial-28-iso-8859-2/font.desc" % \
                                ( config.CONF.width, config.CONF.width,
                                  config.CONF.height )
            self.child = None
            self.restart()
        BmovlCanvas.__init__(self, size)

    def restart(self):
        if self.start_video and not self.child:
            import childapp
            arg = [config.MPLAYER_CMD] + self.mplayer_args.split(' ') + \
                  [config.BMOVL_OSD_VIDEO]
            self.child = childapp.ChildApp2(arg)
            
    def stop(self):
        if self.start_video and self.child:
            self.child.stop('quit')
            self.child = None
            
    def hide(self):
        self.stop()


    def show(self):
        self.restart()


