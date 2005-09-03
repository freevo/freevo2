import plugin
from gameitem import GameItem

class PluginInterface(plugin.MimetypePlugin):
    """
    Plugin to handle all kinds of game items
    """
    def __init__(self):
        plugin.MimetypePlugin.__init__(self)
        self.display_type = [ 'games' ]

        # activate the mediamenu for video
        plugin.activate('mediamenu', level=plugin.is_active('games')[2],
                        args='games')

    def suffix(self):
        return ['smc']

    def get(self, parent, listing):
        items = []

        all_files = listing.match_suffix('smc')
        all_files.sort(lambda l, o: cmp(l.basename.upper(),
                                         o.basename.upper()))

        for file in all_files:
            # TODO: Build snapshots of roms.
            items.append(GameItem(file, parent))
            
        return items
