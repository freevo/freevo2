import os
import util
import config
import menu
import copy
import rc
import string

from video import xml_parser

from item import Item
from video.videoitem import VideoItem
from audio.audioitem import AudioItem
from image.imageitem import ImageItem

from playlist import Playlist

TRUE  = 1
FALSE = 0

# Create the remote control object
rc = rc.get_singleton()

class MediaMenu(Item):
    def __init__(self):
        Item.__init__(self)
        self.main_menu_selected = -1

    def main_menu_generate(self):
        items = []
        dirs  = []
        
        if self.display_type == 'video':
            dirs += config.DIR_MOVIES
        if self.display_type == 'audio':
            dirs += config.DIR_AUDIO
        if self.display_type == 'image':
            dirs += config.DIR_IMAGES

        for d in dirs:
            try:
                (title, dir) = d
                d = DirItem(dir, self, name = title, display_type = self.display_type)
                items += [ d ]
            except:
                # XXX catch other stuff like playlists and files here later
                pass
            
        for media in config.REMOVABLE_MEDIA:
            if media.info:
                media.info.parent = self
                items += [ media.info ]
            else:
                m = Item()
                m.name = 'Drive %s (no disc)' % media.drivename
                m.parent = self
                m.media = media
                items += [ m ]

        return items


    def main_menu(self, arg=None, menuw=None):
        self.display_type = arg
        if self.display_type == 'video':
            title = 'MOVIE'
        elif self.display_type == 'image':
            title = 'IMAGE'
        else:
            title = 'MEDIA'
        moviemenu = menu.Menu('%s MAIN MENU' % title, self.main_menu_generate(),
                              umount_all=1)
        menuw.pushmenu(moviemenu)


    def eventhandler(self, event = None, menuw=None):
        if event == rc.IDENTIFY_MEDIA:
            if not menuw:               # this shouldn't happen
                menuw = menu.get_singleton() 

            if menuw.menustack[1] == menuw.menustack[-1]:
                self.main_menu_selected = menuw.all_items.index(menuw.menustack[1].selected)

            menuw.menustack[1].choices = self.main_menu_generate()

            menuw.menustack[1].selected = menuw.menustack[1].choices[self.main_menu_selected]

            if menuw.menustack[1] == menuw.menustack[-1]:
                menuw.init_page()
                menuw.refresh()
            return TRUE

        # give the event to the next eventhandler in the list
        return Item.eventhandler(self, event, menuw)



    
class DirItem(Playlist):
    def __init__(self, dir, parent, name = '', display_type = None):
        Item.__init__(self)
        self.type = 'dir'
        self.dir = dir
        self.display_type = display_type
        self.parent = parent
        self.media = None
        
        if name:
            self.name = name
        else:
            self.name = '[' + os.path.basename(dir) + ']'
        
        if os.path.isfile(dir+'/cover.png'): 
            self.image = dir+'/cover.png'
        if os.path.isfile(dir+'/cover.jpg'): 
            self.image = dir+'/cover.jpg'

        # playlist stuff
        self.current_item = 0
        self.playlist = []


    def actions(self):
        return [ ( self.cwd, 'browse directory' ) ]
        
            
    def cwd(self, menuw=None):
        items = []
        play_items = []
        
        for media in config.REMOVABLE_MEDIA:
            if string.find(self.dir, media.mountdir) == 0:
                util.mount(self.dir)
                self.media = media

        for dir in util.getdirnames(self.dir):
            items += [ DirItem(dir, self, display_type = self.display_type) ]



        if self.display_type == 'video':
            video_files = util.match_files(self.dir, config.SUFFIX_MPLAYER_FILES)

            for file in util.match_files(self.dir, config.SUFFIX_FREEVO_FILES):
                x = xml_parser.parseMovieFile(file, self, video_files)
                if x:
                    play_items += x

            for file in video_files:
                play_items += [ VideoItem(file, self) ]



        if self.display_type == 'audio':
            audio_files = util.match_files(self.dir, config.SUFFIX_AUDIO_FILES)

            for file in audio_files:
                play_items += [ AudioItem(file, self) ]
            self.playlist = play_items



        if self.display_type == 'image':
            for file in util.match_files(self.dir, config.SUFFIX_IMAGE_FILES):
                play_items += [ ImageItem(file, self) ]
            self.playlist = play_items
            
            for file in util.match_files(self.dir, config.SUFFIX_IMAGE_SSHOW):
                pl = Playlist(file, self)
                pl.autoplay = TRUE
                items += [ pl ]

        
        items += play_items

        title = self.name
        if title[0] == '[' and title[-1] == ']':
            title = self.name[1:-1]

        # autoplay
        if len(items) == 1 and items[0].actions():
            items[0].actions()[0][0](menuw=menuw)
        else:
            moviemenu = menu.Menu(title, items)
            menuw.pushmenu(moviemenu)


