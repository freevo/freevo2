import os
import util
import config
import menu

from video import xmlinfo

from menu import Info
from video.videoinfo import VideoInfo
from image.imageinfo import ImageInfo

TRUE  = 1
FALSE = 0

class MediaMenu(Info):
    def __init__(self):
        Info.__init__(self)


    def main_menu_generate(self):
        items = []
        dirs  = []
        
        if self.display_type == 'video' or not self.display_type:
            dirs += config.DIR_MOVIES
        if self.display_type == 'image' or not self.display_type:
            dirs += config.DIR_IMAGES
            
        for (title, dir) in dirs:
            d = DirInfo(dir, self, name = title, display_type = self.display_type)
            items += [ d ]

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




    
class DirInfo(Info):
    def __init__(self, dir, calling_info, name = None, display_type = None):
        Info.__init__(self)
        self.type = 'dir'
        self.dir = dir
        self.display_type = display_type
        self.calling_info = calling_info

        if name:
            self.name = name
        else:
            self.name = '[' + os.path.basename(dir) + ']'
        
        if os.path.isfile(dir+'/cover.png'): 
            self.image = dir+'/cover.png'
        if os.path.isfile(dir+'/cover.jpg'): 
            self.image = dir+'/cover.jpg'

        self.action = self.cwd
        
            
    def cwd(self, arg=None, menuw=None):
        items = []

        for dir in util.getdirnames(self.dir):
            items += [ DirInfo(dir, self, display_type = self.display_type) ]

        if self.display_type == 'video' or not self.display_type:
            video_files = util.match_files(self.dir, config.SUFFIX_MPLAYER_FILES)

            for file in util.match_files(self.dir, config.SUFFIX_FREEVO_FILES):
                x = xmlinfo.parseMovieFile(file, self, video_files)
                if x:
                    items += x

            for file in video_files:
                items += [ VideoInfo(file, self) ]


        if self.display_type == 'image' or not self.display_type:
            for file in util.match_files(self.dir, config.SUFFIX_IMAGE_FILES):
                items += [ ImageInfo(file, self) ]

        title = self.name
        if title[0] == '[' and title[-1] == ']':
            title = self.name[1:-1]
        moviemenu = menu.Menu(title, items)
        menuw.pushmenu(moviemenu)
