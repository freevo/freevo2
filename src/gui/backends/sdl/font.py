import pygame
import os

import config


font_warning = []

class Font:
    def __init__(self, name, ptsize):
        self.font   = self.__getfont__(name, ptsize)
        self.height = max(self.font.size('A')[1], self.font.size('j')[1])
        self.chars  = {}
        self.name   = name
        self.ptsize = ptsize


    def fade_out(self, surface, pixels=30):
        """
        Helper for drawing a transparency gradient end for strings
        which don't fit it's content area.
        """
        try:
            opaque_mod = float(1)
            opaque_stp = opaque_mod/float(pixels)
            w, h       = surface.get_size()
            alpha      = pygame.surfarray.pixels_alpha(surface)

            # transform all the alpha values in x,y range
            # any speedup could help alot
            for x in range(max(w-pixels, 1), w):
                for y in range(1, h):
                    if alpha[x,y][0] != 0:
                        alpha[x,y] = int(alpha[x,y][0]*opaque_mod)
                opaque_mod -= opaque_stp
        except Exception, e:
            print e


    def render(self, txt, fgcolor, bgcolor=None, border_color=None,
               border_radius=0, dim=0):
        if bgcolor:
            # draw a box around the text if we have a bgcolor
            print 'FIXME: draw box around text'

        render = self.font.render(txt, 1, self.__sdlcol__(fgcolor))

        if not border_color == None:
            border = self.font.render(txt, 1, self.__sdlcol__(border_color))
            # draw on a tmp surface
            tmp = pygame.Surface((render.get_size()[0] + 2 * border_radius,
                                  render.get_size()[1] + 2 * border_radius)).convert_alpha()
            tmp.fill((0, 0, 0, 0))
                            
            for ox in (0, border_radius, border_radius*2):
                for oy in (0, border_radius, border_radius*2):
                    if ox or oy:
                        tmp.blit(border, (ox, oy))
            tmp.blit(render, (border_radius, border_radius))
            render = tmp

        if dim:
            self.fade_out(render, dim)
            
        return render

        
    def charsize(self, c):
        try:
            return self.chars[c]
        except:
            w = self.font.size(c)[0]
            self.chars[c] = w
            return w

    def stringsize(self, s):
        if not s:
            return 0
        w = 0
        for c in s:
            w += self.charsize(c)
        return w


    # Convert a 32-bit TRGB color to a 4 element tuple for SDL
    def __sdlcol__(self, col):
        if col==None:
            return (0,0,0,255)
        a = 255 - ((col >> 24) & 0xff)
        r = (col >> 16) & 0xff
        g = (col >> 8) & 0xff
        b = (col >> 0) & 0xff
        c = (r, g, b, a)
        return c

    def __loadfont__(self, filename, ptsize):
        if os.path.isfile(filename):
            try:
                return pygame.font.Font(filename, ptsize)
            except (RuntimeError, IOError):
                return None
        return None
    
        
    def __getfont__(self, filename, ptsize):
        ptsize = int(ptsize / 0.7)  # XXX pygame multiplies by 0.7 for some reason

        _debug_('Loading font "%s"' % filename, 2)
        font   = self.__loadfont__(filename, ptsize)
        if not font:
            
            # search OSD_EXTRA_FONT_PATH for this font
            fontname = os.path.basename(filename)
            for path in config.OSD_EXTRA_FONT_PATH:
                fname = os.path.join(path, fontname)
                font  = self.__loadfont__(fname, ptsize)
                if font:
                    break
                # deactivated: arialbd seems to be have a wrong height
                # font  = self.__loadfont__(fname.replace('_bold', 'bd'), ptsize)
                # if font:
                #     break
                
        if not font:
            _debug_('Couldnt load font "%s"' % os.path.basename(filename).lower())

            # Ok, see if there is an alternate font to use
            if fontname.lower() in config.OSD_FONT_ALIASES:
                alt_fname = os.path.join(config.FONT_DIR,
                                         config.OSD_FONT_ALIASES[fontname.lower()])
                _debug_('trying alternate: %s' % os.path.basename(alt_fname).lower())
                font = self.__loadfont__(alt_fname, ptsize)

        if not font:
            # not good
            global font_warning
            if not fontname in font_warning:
                print 'WARNING: No alternate found in the alias list!'
                print 'Falling back to default font, this may look very ugly'
                font_warning.append(fontname)
            font = self.__loadfont__(config.OSD_DEFAULT_FONTNAME, ptsize)

        if not font:
            print 'Couldnt load font "%s"' % config.OSD_DEFAULT_FONTNAME
            raise

        return font

