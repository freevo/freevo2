import fxditem
from videoitem import VideoItem


class MovieParser(fxditem.FXDItem):
    """
    Class to parse a movie informations from a fxd file
    """
    def __init__(self, parser, filename, parent, duplicate_check):
        self.items    = []
        self.parent   = parent
        self.dirname  = vfs.dirname(vfs.normalize(filename))
        self.filename = filename
        self.duplicate_check = duplicate_check
        parser.set_handler('movie', self.parse)
        parser.set_handler('disc-set', self.parse)


    def parse(self, fxd, node):
        """
        Callback from the fxd parser. Create a VideoItem (since it should handle
        the information and use it's callback function to jump back into this
        class to fill the structure in __init__. So we jump:
        fxd -> MovieParser.parse -> VideoItem.__init__ -> MovieParser.XXX
        """
        v = None
        
        if node.name == 'movie':
            v = VideoItem((fxd, node, self.parse_movie), self.parent, parse=False)
        elif node.name == 'disc-set':
            v = VideoItem((fxd, node, self.parse_disc_set), self.parent, parse=False)
        if v:
            v.xml_file = self.filename
            self.items.append(v)


    def parse_video_child(self, fxd, node):
        """
        parse a subitem from <video>
        """
        filename = fxd.gettext(node)
        filename = vfs.join(self.dirname, filename)
        mode     = node.name
        id       = fxd.getattr(node, 'id')
        media_id = fxd.getattr(node, 'media_id')
        options  = fxd.getattr(node, 'mplayer_options')

        if mode == 'file':
            # mark the files we include in the fxd in _fxd_covered_
            if not hasattr(self.item, '_fxd_covered_'):
                self.item._fxd_covered_ = []
            if filename and not filename in self.item._fxd_covered_:
                self.item._fxd_covered_.append(filename)
            # remove them from the filelist (if given)
            if filename in self.duplicate_check:
                self.duplicate_check.remove(filename)
            
        return id, filename, mode, media_id, options

    
    def parse_movie(self, fxd, node, item):
        """
        Callback from VideoItem for <movie>

        <movie title>
          <cover-img>file</cover-img>
          <video>
            <dvd|vcd|file id name media_id mplayer_options>file</>+
          <variants>
            <variant>
              <part ref mplayer_options/>
              <subtitle media_id>file</subtitle>
              <audio media_id>file</audio>
            </variant>
          </variants>  
          <info>
        </movie>
        """
        self.item  = item
        item.name  = fxd.getattr(node, 'title')
        item.image = fxd.childcontent(node, 'cover-img')
        if item.image:
            item.image = vfs.join(self.dirname, item.image)
            
        fxd.parse_info(fxd.get_children(node, 'info', 1), item, {'runtime': 'length'})

        video = fxd.get_children(node, 'video')
        if video:
            mplayer_options = fxd.getattr(video[0], 'mplayer_options')
            video = fxd.get_children(video[0], 'file') + \
                    fxd.get_children(video[0], 'vcd') + \
                    fxd.get_children(video[0], 'dvd')

        variants = fxd.get_children(node, 'variants')
        if variants:
            variants = fxd.get_children(variants[0], 'variant')

        if variants:
            # a list of variants
            id = {}
            for v in video:
                info = self.parse_video_child(fxd, v)
                id[info[0]] = info

            for variant in variants:
                audio    = fxd.get_children(variant, 'audio')
                subtitle = fxd.get_children(variant, 'subtitle')

                if audio:
                    audio = { 'media_id': fxd.getattr(audio[0], 'media_id'),
                              'file'    : fxd.gettext(audio[0]) }
                else:
                    audio = {}
                    
                if subtitle:
                    subtitle = { 'media_id': fxd.getattr(subtitle[0], 'media_id'),
                                 'file'    : fxd.gettext(subtitle[0]) }
                else:
                    subtitle = {}
                    
                parts = fxd.get_children(variant, 'part')
                if len(parts) == 1:
                    # a variant with one file
                    ref = fxd.getattr(parts[0] ,'ref')
                    v = VideoItem(id[ref][1], parent=item, parse=False)
                    v.mode, v.media_id, v.mplayer_options = id[ref][2:]

                    v.subtitle_file = subtitle
                    v.audio_file    = audio

                    # global <video> mplayer_options
                    if mplayer_options:
                        v.mplayer_options += mplayer_options
                else:
                    # a variant with a list of files
                    v = VideoItem('', parent=item, parse=False)
                    v.subtitle_file = subtitle
                    v.audio_file    = audio
                    for p in parts:
                        ref = fxd.getattr(p ,'ref')
                        sub = VideoItem(id[ref][1], parent=v, parse=False)
                        sub.mode, sub.media_id, sub.mplayer_options = id[ref][2:]
                        # global <video> mplayer_options
                        if mplayer_options:
                            sub.mplayer_options += mplayer_options
                        v.subitems.append(sub)
                        
                v.name = fxd.getattr(variant, 'name')
                item.variants.append(v)
                
        elif len(video) == 1:
            # only one file, this is directly for the item
            id, item.filename, item.mode, item.media_id, \
                item.mplayer_options = self.parse_video_child(fxd, video[0])
            # global <video> mplayer_options
            if mplayer_options:
                item.mplayer_options += mplayer_options

        else:
            # a list of files
            for s in video:
                info = self.parse_video_child(fxd, s)
                v = VideoItem(info[1], parent=item, parse=False)
                v.mode, v.media_id, v.mplayer_options = info[2:]
                # global <video> mplayer_options
                if mplayer_options:
                    v.mplayer_options += mplayer_options
                item.subitems.append(v)
        


    def parse_disc_set(self, fxd, node, item):
        """
        Callback from VideoItem for <disc-set>
        """
        item.name  = fxd.getattr(node, 'title')
        item.image = fxd.childcontent(node, 'cover-img')
        if item.image:
            item.image = vfs.join(self.dirname, item.image)

        fxd.parse_info(fxd.get_children(node, 'info', 1), item, {'runtime': 'length'})
        item.rom_label = []
        item.rom_id    = []
        
        for disc in fxd.get_children(node, 'disc'):
            id = fxd.getattr(disc, 'media-id')
            if id:
                item.rom_id.append(id)
                
            label = fxd.getattr(disc, 'label-regexp')
            if label:
                item.rom_label.append(label)

            # what to do with the mplayer_options? We can't use them for
            # one disc, or can we? And file_ops? Also only on a per disc base.
            # So I ignore that we are in a disc right now and use the 'item'
            item.mplayer_options = fxd.getattr(disc, 'mplayer_options')
            for f in fxd.get_children(disc, 'file-opts'):
                opt = { 'file-d': f.getattr(f, 'media-id'),
                        'mplayer_options': f.getattr(f, 'mplayer_options') }
                item.files_options.append(opt)




# register this callback
fxditem.register(['video'], MovieParser)
