# game item
# Daniel Casimiro

import logging
import event
from player import gamesplayer

from menu import MediaItem, Action

log = logging.getLogger('games')
log.setLevel(logging.DEBUG)

class GameItem(MediaItem):
    def __init__(self, url, parent):
        MediaItem.__init__(self, parent, type='games')

        self.player = None
        log.debug('Initialized GameItem. URL is %s' % (url))
        self.set_url(url)

    def actions(self):
        items = [Action(_('Play'), self.play)]
        return items

    def play(self):
        gamesplayer().play(self)

    def stop(self):
        gamesplayer().stop()

    def eventhandler(self, ev):
        print "Game Item event handler:", ev
        if ev == event.MENU:
            self.player.stop()
            return True

        return MediaItem.eventhandler(self, ev)
