import mevas
import config


font_warning = []

class Font:
    def __init__(self, name, ptsize):
        self.font   = self.__getfont__(name, ptsize)
        self.height = self.font.get_text_size('')[3]
        self.chars  = {}
        self.name   = name
        self.ptsize = ptsize


    def charsize(self, c):
        try:
            return self.chars[c]
        except:
            w = self.font.get_text_size(c)[0]
            self.chars[c] = w
            return w

    def stringsize(self, s):
        s = self.font.get_text_size(s)
        return max(s[0], s[2])
        

    def __getfont__(self, name, ptsize):
        _debug_('Loading font "%s:%s"' % (name, ptsize), 2)
        try:
            return mevas.imagelib.load_font(name, ptsize)
        except IOError:
            _debug_('Couldn\'t load font "%s"' % name, 2)

            # Ok, see if there is an alternate font to use
            if name in config.OSD_FONT_ALIASES:
                alt_fname = config.OSD_FONT_ALIASES[name]
                _debug_('trying alternate: %s' % alt_fname, 2)
                try:
                    return mevas.imagelib.load_font(alt_fname, ptsize)
                except IOError:
                    # not good
                    global font_warning
                    if not name in font_warning:
                        print 'WARNING: No alternate found in the alias list!'
                        print 'Falling back to default font, this may look very ugly'
                        font_warning.append(name)
                    return mevas.imagelib.load_font(config.OSD_DEFAULT_FONTNAME, ptsize)

        


# init
mevas.imagelib.add_font_path(config.FONT_DIR)
font_info_cache = {}

def get(font, ptsize):
    """
    return cached font
    """
    key = (font, ptsize)
    try:
        return font_info_cache[key]
    except:
        fi = Font(font, ptsize)
        font_info_cache[key] = fi
        return fi
