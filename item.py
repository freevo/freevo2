from menu import MenuItem

import rc
import menu

rc         = rc.get_singleton()

TRUE  = 1
FALSE = 0


#
# Item class. Inherits from MenuItem and is a template for other info items
# like VideoItem, AudioItem and ImageItem
#
class Item(MenuItem):
    def __init__(self):
        self.name = None                # name in menu
        self.image = None               # imagefile
        
        self.type   = None              # type: e.g. video, audio, dir, playlist
        self.handle_type = None         # handle item in skin as video, audio, image
                                        # e.g. a directory has all video info like
                                        # directories of a cdrom
        self.icon   = None
        self.parent = None              # parent item to pass unmapped event


        # possible variables for an item.
        # some or only needed for video or image or audio
        # these variables are copied by the copy function
        
        self.mplayer_options = ''

        self.url     = ''
        self.genre   = ''
        self.tagline = ''
        self.plot    = ''
        self.runtime = ''
        self.year    = ''
        self.rating  = ''

        self.rom_id    = []
        self.rom_label = []
        self.media = None

        # interactive stuff for video, parsed my mplayer
        self.current_playtime = 0
        self.available_audio_tracks = []
        self.available_subtitles = []
        self.available_chapters = 0


    def copy(self, obj):
        if not self.image:
            self.image = obj.image
        if not self.name:
            self.name = obj.name
            
        self.mplayer_options = obj.mplayer_options

        self.url     = obj.url
        self.genre   = obj.genre
        self.tagline = obj.tagline
        self.plot    = obj.plot
        self.runtime = obj.runtime
        self.year    = obj.year
        self.rating  = obj.rating

        self.rom_id    = obj.rom_id
        self.rom_label = obj.rom_label
        self.media     = obj.media

        self.current_playtime = obj.current_playtime
        self.available_audio_tracks = obj.available_audio_tracks
        self.available_subtitles = obj.available_subtitles
        self.available_chapters = obj.available_chapters
        

    # returns a list of possible actions on this item. The first
    # one is autoselected by pressing SELECT
    def actions(self):
        return None

    # eventhandler for this item
    def eventhandler(self, event, menuw=None):
        if event == rc.EJECT and self.media and menuw and \
           menuw.menustack[1] == menuw.menustack[-1]:
            self.media.move_tray(dir='toggle')
            return TRUE

        if event == rc.PLAY_END:
            menuwidget = menu.get_singleton()
            menuwidget.refresh()
            return TRUE

        # give the event to the next eventhandler in the list
        if self.parent:
            return self.parent.eventhandler(event, menuw)

        print 'no eventhandler for event %s menuw %s' % (event, menuw)
        return FALSE

        
