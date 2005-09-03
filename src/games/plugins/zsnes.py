# ZSNES plugin
# Daniel Casimiro <dan.casimiro@gmail.com>

import plugin
import config
from event import *

from application import ChildApp

class PluginInterface(plugin.Plugin):
    """
    zsnes plugin for gaming.  This plugin allows you to use the zsnes
    super nintendo emulator from within freevo.
    """
    def __init__(self):
        plugin.Plugin.__init__(self)
        plugin.register(Zsnes(), plugin.GAMES, True)
        print 'zsnes activated!'

class Zsnes(ChildApp):
    """
    Use this interface to control zsnes.
    """
    def __init__(self):
        ChildApp.__init__(self, 'zsnes', 'games', True, False, True)
    

    def play(self, item, player):
        self.player = player
        cmd = 'zsnes'
        self.child_start([cmd, item.filename], stop_cmd='quit\n')

    def eventhandler(self, event):
        print 'zsnes eventhandler:', event

        if event == PLAY_END:
            self.stop()
            self.player.eventhandler(event)
            return True

        return False
