import time
import pygame
from pygame.locals import *

import config


class Keyboard:
    def __init__(self):
        self.mousehidetime = time.time()

        
    def poll(self, map=True):
        """
        callback for SDL event (not Freevo events)
        """
        if not pygame.display.get_init():
            return None

        # Check if mouse should be visible or hidden
        mouserel = pygame.mouse.get_rel()
        mousedist = (mouserel[0]**2 + mouserel[1]**2) ** 0.5

        if mousedist > 4.0:
            pygame.mouse.set_visible(1)
            self.mousehidetime = time.time() + 1.0  # Hide the mouse in 2s
        else:
            if time.time() > self.mousehidetime:
                pygame.mouse.set_visible(0)

        # Return the next key event, or None if the queue is empty.
        # Everything else (mouse etc) is discarded.
        while 1:
            event = pygame.event.poll()

            if event.type == NOEVENT:
                return
            
            if event.type == KEYDOWN:
                if not map and event.key > 30:
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        pass
                    
                if event.key in config.KEYMAP.keys():
                    # Turn off the helpscreen if it was on
                    return config.KEYMAP[event.key]

                elif event.key == K_h:
                    print 'FIXME: add help'

                elif event.key == K_z:
                    print 'FIXME: toogle fullscreen'

                elif event.key == K_F10:
                    # Take a screenshot
                    print 'FIXME: take screenshot'

                else:
                    # don't know what this is, return it as it is
                    try:
                        if event.unicode != u'':
                            return event.unicode
                    except:
                        return None
