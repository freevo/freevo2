import plugin
import config
import rc

import menu

TRUE  = 1
FALSE = 0

class PluginInterface(plugin.MainMenuPlugin):
    """
    plugin to detach the audio player to e.g. view pictures while listening
    to music
    """
    def __init__(self):
        plugin.MainMenuPlugin.__init__(self)
        config.RC_MPLAYER_AUDIO_CMDS['DISPLAY'] = ( self.detach, 'detach player' )
        self.player = None
        self.show_item = menu.MenuItem('Show player', action=self.show)
        
    def detach(self, player):
        gui   = player.playerGUI

        # hide the player and show the menu
        gui.hide()
        gui.menuw.show()

        # set all menuw's to None to prevent the next title to be
        # visible again
        gui.menuw = None
        gui.item.menuw = None
        if gui.item.parent:
            gui.item.parent.menuw = None
        self.player = gui.player
        

    def items(self, parent):
        if self.player and self.player.is_playing():
            self.show_item.parent = parent
            return [ self.show_item ]
        return ()


    def show(self, arg=None, menuw=None):
        gui = self.player.playerGUI

        # restore the menuw's
        gui.menuw = menuw
        gui.item.menuw = menuw
        if gui.item.parent:
            gui.item.parent.menuw = menuw

        # hide the menu and show the player
        menuw.hide()
        gui.show()


    def eventhandler(self, event, menuw=None):
        if event == 'AUDIO_PLAY_END':
            self.player.eventhandler(event=event)
            return TRUE
        return FALSE
