import config
from base import Application
from event import *

import logging
log = logging.getLogger()

class MenuApplication(Application):
    """
    An application inside the menu
    """
    def __init__(self, name, event_context, fullscreen):
        Application.__init__(self, name, event_context, fullscreen)
        self.menuw  = None
        self.engine = None # draw engine based on area
        self.inside_menu = False
        

    def eventhandler(self, event):
        """
        Eventhandler for basic menu functions
        """
        if not self.menuw:
            return False
        if event == MENU_GOTO_MAINMENU:
            self.stop()
            self.menuw.goto_main_menu()
            return True
        if event == MENU_BACK_ONE_MENU:
            self.stop()
            self.menuw.back_one_menu()
            return True
        return False


    def show(self):
        """
        show the menu on the screen
        """
        if self.visible:
            return
        Application.show(self)
        if self.engine and self.inside_menu:
            self.inside_menu = False
            self.engine.show(0)
        elif self.engine:
            self.engine.show(config.OSD_FADE_STEPS)
    

    def hide(self):
        """
        hide the menu on the screen
        """
        if not self.visible:
            return
        Application.hide(self)
        if self.engine and self.inside_menu:
            self.inside_menu = False
            self.engine.hide(0)
        elif self.engine:
            self.engine.hide(config.OSD_FADE_STEPS)

    

    def refresh(self):
        """
        refresh display
        """
        pass


    def __del__(self):
        log.info('delete menu application %s' % self)
