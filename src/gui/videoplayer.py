# python imports
import logging

# gui imports
from application import Application

# get logging object
log = logging.getLogger('video')

class VideoPlayer(Application):
    """
    Widget for the video player. This is the kaa.candy part of the application
    """
    candyxml_style = 'videoplayer'

    def set_player(self, player):
        self.player = player
        from . import signals
        self.player.signals['key-pressed'].connect(signals['key-press'].emit)

    def show(self):
        pass

    def destroy(self):
        from . import signals
        self.player.signals['key-pressed'].disconnect(signals['key-press'].emit)

