-*- python -*-

"""
This file explains the interface needed to write a backend for
Freevo. Since the gui code is Work In Progress, there may be more
requirements than in this doc. 

Please look at the sdl backend for example if this doc isn't enough.
To test your backend, remove the idlebar plugin for now, activate it
in gui/__init__.py and test iton the menu only.

A backend should provide four main classes in it's __init__.py:
Renderer, Screen, Layer and Keyboard (will be optional soon).

Renderer:
"""

class Renderer:
    """
    The basic render engine
    """
    # Some default colors (deprecated)
    COL_BLACK  = 0x000000
    COL_WHITE  = 0xffffff
    COL_ORANGE = 0xFF9028


    def shutdown(self):
        """
        Shutdown the renderer. This function will be called when Freevo
        shuts down.
        """
	pass


    def stopdisplay(self):
        """
        Stop the display to give other apps the right to use it. Some output
        devices need the screen and Freevo needs to stop the display. If your
        output driver doesn't support this, just do nothing here.
        """
        pass


    def restartdisplay(self):
        """
        Restores a stopped display (see stopdisplay)
        """
        pass
    
        
    def toggle_fullscreen(self):
        """
        Toggle between window and fullscreen mode. Only needed in the
        tvtime plugin for now, you can just create this an empty function.
        """
        pass


    def get_fullscreen(self):
        """
        Return 1 is fullscreen is running. Only needed in the
        tvtime plugin for now, you can just create this an empty function.
        """
        pass
    

    def clearscreen(self, color=None):
        """
        Clean the complete screen. Some parts of Freevo call this function,
        but they shouldn't. Implement this function as a dummy for now. 
        """
        pass
    
    
    def loadbitmap(self, url, cache=False, width=None, height=None, vfs_save=False):
        """
        Load a bitmap and return the image object.
        o if cache is given, use the cache object to store the result and check
          in it to make Freevo faster. If cache is True (== no object), use an
          internal cache.
        o If width and height are given, the image is scaled to that. Setting
          only width or height will keep aspect ratio.
        o If vfs_save is true, the so scaled bitmap will be stored in the vfs for
          future use.
        The returned object must provide the interface of Image defined after
        Renderer.   
        """
        pass
    

    def resizebitmap(self, image, width=None, height=None):
        """
        Resize the given image to width and height. If height or width is None,
        keep aspect ratio in the result. Return a new image, don't mess with the
        given one.
        The returned object must provide the interface of Image defined after
        Renderer.   
        """
        pass
        

    def zoombitmap(self, image, scaling=None, bbx=0, bby=0, bbw=0, bbh=0, rotation = 0):
        """
        Scale the given image, rotate it and only use the bounding box defined
        with the bb pararmeter. Return a new image, don't change the old one.
        The returned object must provide the interface of Image defined after
        Renderer.   
        """
        pass

        
    def getfont(self, font, ptsize):
        """
        Return a font object for the given font and size. Fall back to a default
        font if you can't load the given font. The returned object must provide
        the interface below.
        """
        pass

    
    def drawstringframed(self, string, x, y, width, height, font, fgcolor=None,
                         bgcolor=None, align_h='left', align_v='top', mode='hard',
                         layer=None, ellipses='...', dim=True):
        """
        Draw a string. This function is deprecated, but many parts of Freevo still
        use it. See drawstringframed in sdl/renderer.py for a nice fallback.
        """
        pass

    
    def drawstring(self, string, x, y, fgcolor=None, bgcolor=None,
                   font=None, ptsize=0, align='left', layer=None):
        """
        Deprecated. Define this function for now, but you don't have to do anything.
        """
        pass
    

    def update(self, rect=None, blend_surface=None, blend_speed=0,
               blend_steps=0, blend_time=None, stop_busyicon=True):
        """
        Update the output object. This function is also deprecated, but many parts
        of Freevo still use it. Just do nothing.
        """
        pass
    



class Surface:
    """
    Everytime the renderer returns an image or is given a surface or layer, this
    object needs to have the following interface. You won't find this in the sdl
    renderer because it is the pygame surface.
    """
    def get_size(self):
        """
        Return width, height of the object
        """
        pass
    

    def blit(self, image, src, dest=None):
        """
        I don't know if this function is needed somewere, so create at least a
        dummy for it. It merges the content of the given image to it's own at the
        position src (x,y). If dest ist given (x,y,w,h), only merge the given
        rectange from the image.
        """
        pass
    

class Font:
    """
    The font object returned by getfont must provide the folllowing functions:
    """

    def __init__(self, *args):
        """
        Attributes:
        self.height is the height in pixel of one line with this font/size
        """
        self.height

        
    def render(self, txt, fgcolor, bgcolor=None, border_color=None,
               border_radius=0, dim=0):
        """
        Render the string 'txt' with the given attributes like fgcolor.
        This functions returns a Surface object.
        """
        pass
    

    def charsize(self, c):
        """
        Return the width in pixel of the character c
        """
        pass

    
    def stringsize(self, s):
        """
        Return the width in pixel of the string s
        """
        pass
    


class Layer:
    """
    A layer is something objects from gui.base are added or removed. It belongs
    the a Screen (the below). You can add more functions you need when you update
    a layer from your screen implementation.
    """
    def __init__(self, *args):
        """
        Attributes: width and height of the layer. This should be identical
        with the Screen values.
        """
        self.width
        self.height
        

    def blit(self, image, src, dest=None):
        """
        Blit the given image (it is a Surface from above) to the layer. The objects
        from gui.base call this function to draw themself.
        src is the position on the layer (x,y), if dest is given, only blit this
        rectangle (x,y,w,h).
        """
        pass


    def drawbox(self, x0, y0, x1, y1, color=None, border_size=0,
                border_color=None, radius=0):
        """
        Draw a round box (needed for the Rectangle in gui.base).
        """
        pass


    def add(self, object):
        """
        Add an object to this layer
        """
        pass
    

    def remove(self, object):
        """
        Add an object from this layer
        """
        pass



class Screen:
    """
    This is the screen. It should have 3 Layers: bg, alpha and content. Freevo
    will add objects to it and draw it.
    """
    def clear(self):
        """
        Clear the complete screen. Provide this function, but I hope we will
        never use it.
        """
        pass
    

    def add(self, layer, object):
        """
        Add object to a specific layer. Right now, this screen has
        only three layers: bg, alpha and content. The layer is provided
        as a string.
        """
        pass
    
            
    def remove(self, layer, object):
        """
        Remove an object from the screen
        """
        pass


    def update(self):
        """
        Update the screen. This means drawing on all objects on all layers and
        call some function to show this on the real screen.
        """
        pass
    


class Keyboard:
    """
    This is for keyboard control. In SDL it is still a bad mix between keyboard
    and screen updates. THIS INTERFACE MAY CHANGE IN THE FUTURE. If you don't
    need this, provide a class with only the poll function for now.
    """
    def poll(self, map=True):
        """
        Poll for keyboard events. If map is true, map the key to an event
        using config.KEYMAP and return it. Else return the key as unicode
        character. Return None if no key is pressed.
        """
        pass
    
