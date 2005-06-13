# -*- coding: iso-8859-1 -*-
# -----------------------------------------------------------------------------
# Imlib2.py - Imlib2 wrapper for Python
# -----------------------------------------------------------------------------
# $Id$
# -----------------------------------------------------------------------------
# Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
#
# Maintainers: Jason Tackaberry <tack@sault.org>
#              Dirk Meyer <dmeyer@tzi.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MER-
# CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# -----------------------------------------------------------------------------

import types
import math
import os
import glob
import md5

import _Imlib2

# thumbnail image dir
_thumbnail_dir = os.path.join(os.environ['HOME'], '.thumbnails/large/')
if not os.path.isdir(_thumbnail_dir):
    # create the 'large' dir. Set permissions to user only. All files
    # inside should also be user only, but who cares when the dir is save?
    # Yes, I know, it's ugly :)
    os.makedirs(_thumbnail_dir, 0700)

# dir for failed thumbnails
_failed_dir = os.path.join(os.environ['HOME'], '.thumbnails/fail/pyimlib2/')
if not os.path.isdir(_failed_dir):
    # create the 'fail' dir. Set permissions to user only. All files
    # inside should also be user only, but who cares when the dir is save?
    # Yes, I know, it's ugly :)
    os.makedirs(_failed_dir, 0700)
    
def utf8(text):
    """
    Returns a UTF-8 string, converting from latin-1 if necessary.  This does a
    pretty good job Doing the Right Thing, converting only when it's really
    latin-1.  Of course it's not foolproof, but it works reasonably in practice.
    """
    if type(text) == types.UnicodeType:
        return text.encode("utf-8")

    try:
        text.decode("utf-8")
    except:
        try:
            text = text.decode("latin-1").encode("utf-8")
        except:
            pass

    return text


class Image:
    """
    Imlib2 Image class.  The constructor can be called directly, or a new
    Image object may be created via the new() and open() module functions.
    """

    def __init__(self, image_or_filename):
        """
        Create a new Image object.

        Arguments:
          image_or_filename: Instantiate the image from another Image
                             instance, an instance of the backend's image
                             class or type, or a file name from which to load
                             the image.
        """
        if type(image_or_filename) in types.StringTypes:
            self._image = _Imlib2.open(image_or_filename)
        elif isinstance(image_or_filename, Image):
            self._image = image_or_filename.copy()._image
        elif type(image_or_filename) == _Imlib2.Image:
            self._image = image_or_filename
        else:
            raise ValueError, "Unsupported image type %s" % \
		  type(image_or_filename)

        self.font = None


    def __getattr__(self, attr):
        """
        Supports these attributes:

               size: tuple containing the width and height of the image
              width: width of the image
             height: height of the image
             format: format of the image if loaded from file (e.g. PNG, JPEG)
          rowstride: number of bytes per row of pixels
          has_alpha: True if the image has an alpha channel, False otherwise
           filename: filename if loaded from file
        """
        if attr in ("width", "height", "format", "mode", "filename",
                "rowstride"):
            return getattr(self._image, attr)
        elif attr == "size":
            return (self._image.width, self._image.height)
        elif attr == "has_alpha":
            if self._image.has_alpha: return True
            return False

        if attr not in self.__dict__:
            raise AttributeError, attr
        return self.__dict__[attr]


    # Functions for pickling.
    def __getstate__(self):
        return self.size, str(self.get_raw_data())

    def __setstate__(self, state):
        self._image = _Imlib2.create(state[0], state[1])


    def get_raw_data(self, format = "BGRA", write = False):
        """
        Returns raw image data for read only access.

        Arguments:
          format: pixel format of the raw data to be returned.  If 'format' is
                  not a supported format, ValueError is raised.  Format
                  can be any combination of RGB or RGBA.  YV12A is also
                  supported, which returns a planar 4:2:0 plus a 8bpp
                  alpha plane.  (YV12A isn't a fourcc notation; I just
                  made it up.)

        Returns: A buffer object representing the raw pixel data.  The buffer
                 will be a writable buffer if 'write' was True or if the
                 'format' was non-native (i.e. something other than BGRA).  If
                 'format' was BGRA and 'write' was True, you'll need to call
                 put_back_raw_data() when you're done writing to the buffer.
        """
        return self._image.get_raw_data(format, write)


    def put_back_raw_data(self, data):
        """
        Puts back the writable buffer that was obtained with get_raw_data().
        """
        self._image.put_back_raw_data(data)


    def scale(self, (w, h), src_pos = (0, 0), src_size = (-1, -1)):
        """
        Scale the image and return a new image.

        Arguments:
          w, h: the width and height of the new image.  If either argument
                is -1, that dimension is calculated from the other dimension
                while retaining the original aspect ratio.

        Returns: a new Image instance representing the scaled image.
        """
        src_w, src_h = src_size
        x, y = src_pos

        if 0 in src_size:
            raise ValueError, "Invalid scale size specified %s" % \
		  repr(src_size)

        aspect = float(self.width) / float(self.height)
        if w == -1:      w = round(h * aspect)
        elif h == -1:    h = round(w / aspect)
        if src_w == -1:  src_w = self.width
        if src_h == -1:  src_h = self.height
        return Image(self._image.scale(int(x), int(y), int(src_w), int(src_h),
				       int(w), int(h)))


    def crop(self, (x, y), (w, h)):
        """
        Crop the image and return a new image.

        Arguments:
          x, y, w, h: represents the left, top, width, height region in
                      the image.

        Returns: a new Image instance representing the cropped image.
        """
        return self.scale((w, h), (x, y), (w, h) )


    def rotate(self, angle):
        """
        Rotate the image and return a new image.

        Arguments:
          angle: the angle in degrees by which to rotate the image.

        Returns: a new Image instance representing the rotated image.

        FIXME: imlib2's rotate works all wonky.  Doesn't act how I expect.
        """
        return Image(self._image.rotate(angle * math.pi / 180))


    def orientate(self, orientation):
        """
        Performs 90 degree rotations on the image.

        Arguments:
          orientation: 0: no rotation; 1: rotate clockwise 90 degrees,
                       2: rotate clockwise 180 degrees; 3: rotates clockwise
                       270 degrees.

        Returns: None
        """
        self._image.orientate(orientation)


    def flip_horizontal(self):
        """
        Flips the image on its horizontal axis.

        Returns: None.
        """
        self._image.flip(True, False, False)


    def flip_vertical(self):
        """
        Flips the image on its vertical axis.

        Returns: None.
        """
        self._image.flip(False, True, False)


    def flip_diagonal(self):
        """
        Flips the image on along its diagonal.

        Returns: None.
        """
        self._image.flip(False, False, True)


    def scale_preserve_aspect(self, (w, h)):
        """
        Scales the image while retaining the original aspect ratio and return
        a new image.

        Arguments:
          w, h: the maximum size of the new image.  The new image will be as
                large as possible, using w, h as the upper limits, while
                retaining the original aspect ratio.

        Returns: a new Image instance represented the scaled image.
        """
        if 0 in (w, h):
            raise ValueError, "Invalid scale size specified %s" % repr((w,h))
        aspect = float(self.width) / float(self.height)
        if aspect >= 1.0:
            img = self._image.scale(0, 0, self.width, self.height, w,
				    int(h / aspect))
        else:
            img = self._image.scale(0, 0, self.width, self.height,
				    int(w * aspect), h)
        return Image(img)


    def thumbnail(self, (w, h)):
        """
        Generates a thumbnail of the image, REPLACING the current image.
        This simulates the PIL thumbnail function.
        """
        if self.width < w and self.height < h:
            return

        self._image = self.scale_preserve_aspect( (w, h) )._image


    def copy_rect(self, src_pos, size, dst_pos):
        """
        Copies a region within the image.

        Arguments:
          src_pos: a tuple holding the x, y coordinates marking the top left
                   of the region to be moved.
             size: a tuple holding the width and height of the region to move.
                   If either dimension is -1, then that dimension extends to
                   the far edge of the image.
          dst_pos: a tuple holding the x, y coordinates within the image
                   where the region will be moved to.
        Returns: None
        """
        return self._image.copy_rect(src_pos, size, dst_pos)


    def blend(self, src, src_pos = (0, 0), src_size = (-1, -1),
          dst_pos = (0, 0), dst_size = (-1, -1),
          alpha = 255, merge_alpha = True):
        """
        Blends one image onto another.

        Arguments:
                  src: the image being blended onto 'self'
              dst_pos: a tuple holding the x, y coordinates where the source
                       image will be blended onto the destination image.
              src_pos: a tuple holding the x, y coordinates within the source
                       image where blending will start.
             src_size: a tuple holding the width and height of the source
                       image to be blended.  A value of -1 for either one
                       indicates the full dimension of the source image.
                alpha: the "layer" alpha that is applied to all pixels of the
                       image.  If an individual pixel has an alpha of 128 and
                       this value is 128, the resulting pixel will have an
                       alpha of 64 before it is blended to the destination
                       image.  0 is fully transparent and 255 is fully opaque,
                       and 256 is a special value that means alpha blending is
                       disabled.
          merge_alpha: if True, the alpha channel is also blended.  If False,
                       the destination image's alpha channel is untouched and
                       the RGB values are compensated

        Returns: None.
        """

        if src_size[0] == -1: src_size = src.width, src_size[1]
        if src_size[1] == -1: src_size = src_size[0], src.height
        if dst_size[0] == -1: dst_size = src_size[0], dst_size[1]
        if dst_size[1] == -1: dst_size = dst_size[0], src_size[1]
        return self._image.blend(src._image, src_pos, src_size,
                     dst_pos, dst_size, int(alpha), merge_alpha)


    def clear(self, (x, y) = (0, 0), (w, h) = (-1, -1)):
        """
        Clears the image at the specified rectangle, resetting all pixels in
        that rectangle to fully transparent.

        Arguments:
          x, y: left and top coordinates of the rectangle to be cleared.
                Default is the top left corner.
          w, h: width and height of the rectangle to be cleared.  If either
                value is -1 then the image is cleared to the far edge.

        Returns: None
        """
        x = max(0, min(self.width, x))
        y = max(0, min(self.height, y))
        if w == -1: w = self.width - x
        if h == -1: h = self.height - y
        w = min(w, self.width-x)
        h = min(h, self.height-y)
        self._image.clear(x, y, w, h)


    def draw_mask(self, maskimg, (x, y)):
        """
        Applies the luma channel of maskimg to the alpha channel of the
        the current image.

        Arguments:
          maskimg: the image from which to read the luma channel
             x, y: the top left coordinates within the current image where the
                   alpha channel will be modified.  The mask is drawn to the
                   full width/height of maskimg.

        Returns: None
        """

        return self._image.draw_mask(maskimg._image, int(x), int(y))


    def copy(self):
        """
        Creates a copy of the current image.

        Returns: a new Image instance with a copy of the current image.
        """
        return Image(self._image.clone())


    def set_font(self, font_or_font_name):
        """
        Sets the font context to font_or_font_name.  Subsequent calls to
        draw_text() will be rendered using this font.

        Arguments:
          font_or_fontname: either a Font object, or a string containing the
                            font's name and size.  This string is in the
                            form "Fontname/Size" such as "Arial/16"


        Returns: a Font instance represent the specified font.  If
                 'font_or_fontname' is already a Font instance, it is simply
                 returned back to the caller.
        """
        if type(font) in types.StringTypes:
            self.font = Font(font)
        else:
            self.font = font
        return self.font


    def get_font(self):
        """
        Gets the current Font context.

        Returns: A Font instance as created by set_font() or None if no font
                 context is defined.
        """
        return self.font


    def draw_text(self, (x, y), text, color = None, font_or_fontname = None):
        """
        Draws text on the image.

        Arguments:
                      x, y: the left/top coordinates within the current image
                            where the text will be rendered.
                      text: a string holding the text to be rendered.
                     color: a 3- or 4-tuple holding the red, green, blue, and
                            alpha values of the color in which to render the
                            font.  If color is a 3-tuple, the implied alpha
                            is 255.  If color is None, the color of the font
                            context, as specified by set_font(), is used.
          font_or_fontname: either a Font object, or a string containing the
                            font's name and size.  This string is in the
                            form "Fontname/Size" such as "Arial/16".  If this
                            parameter is none, the font context is used, as
                            specified by set_font().

        Returns: a 4-tuple representing the width, height, horizontal advance,
                 and vertical advance of the rendered text.
        """
        if not font_or_fontname:
            font = self.font
        elif type(font_or_fontname) in types.StringTypes:
            font = Font(font)
        else:
            font = font_or_fontname

        if not color:
            color = font.color
        if len(color) == 3:
            color = tuple(color) + (255,)

        return self._image.draw_text(font._font, int(x), int(y),
                         utf8(text), color)


    def draw_rectangle(self, (x, y), (w, h), color, fill = True):
        """
        Draws a rectangle on the image.

        Arguments:
           x, y: the top left corner of the rectangle.
           w, h: the width and height of the rectangle.
          color: a 3- or 4-tuple holding the red, green, blue, and alpha
                 values of the color in which to draw the rectangle.  If
                 color is a 3-tuple, the implied alpha is 255.
           fill: whether the rectangle should be filled or not.  The default
                 is true.

        Returns: None
        """
        if len(color) == 3:
            color = tuple(color) + (255,)
        return self._image.draw_rectangle(int(x), int(y), int(w), int(h),
                          color, fill)

    def draw_ellipse(self, (xc, yc), (a, b), color, fill = True):
        """
        Draws an ellipse on the image.

        Arguments:
          xc, yc: the x, y coordinates of the center of the ellipse.
            a, b: the horizontal and veritcal amplitude of the ellipse.
           color: a 3- or 4-tuple holding the red, green, blue, and alpha
                  values of the color in which to draw the ellipse.  If
                  color is a 3-tuple, the implied alpha is 255.
            fill: whether the ellipse should be filled or not.  The default
                  is true.

        Returns: None
        """
        if len(color) == 3:
            color = tuple(color) + (255,)
        return self._image.draw_ellipse(int(xc), int(yc), int(a), int(b),
					color, fill)


    def get_pixel(self, (x, y)):
        """
        Get the color for the specified pixel.

        Arguments:
          x, y: Coordinates of the pixel for which to return the color.

        Returns: a 4-tuple representing the color of the pixel.  The tuple is
                 in BGRA format, or (blue, green, red, alpha).
        """
        return self._image.get_pixel((x,y))


    def set_alpha(self, has_alpha):
        """
        Enable / disable the alpha layer.

        Arguments:
        has_alpha: if True, the alpha layer will be enabled, if
                   False disabled
        Returns: None
        """
        if has_alpha:
            self._image.set_alpha(1)
        else:
            self._image.set_alpha(0)


    def save(self, filename, format = None):
        """
        Saves the image to a file.

        Arguments:
          format: the format of the written file (jpg, png, etc.).  If format
                  is None, the format is gotten from the filename extension.

        Returns: None.
        """
        if not format:
            format = os.path.splitext(filename)[1][1:]
        return self._image.save(filename, format)



class Display:
    """
    Although not part of Imlib2, this class is here as a convenience, and
    provides very basic X11 display support.

    Instances may have attributes 'expose_callback' and 'input_callback' set,
    and when the window receives an Expose or KeyPress event, the respective
    callbacks will be invoked.  If a backing store is set for the display,
    expose events will be handled and the damaged regions redrawn.  If an
    application requires something more elaborate, it will have to set its
    own 'expose_callback'.  These callbacks are in the form:

        expose_callback(regions_list)
            - where regions_list is a list of tuples, where each tuple is in
              the form ((x, y), (width, height)).

        input_callback(keycode)
            - where keycode is the X key code of the key that was pressed.

    """
    def __init__(self, (w, h), dither = True, blend = False, backing_store = None):
        """
        Create a new window of width 'w' and height 'h' on the current X11
        display (as specified in the DISPLAY environment variable).  If
        'dither' is True, images will be dithered to use the depth of the
        display (looks much better at the expense of performance).  If
        'blend' is True, all images being rendered to the window will be
        alpha-blended.  Both 'dither' and 'blend' options can be overridden
        on a per-image basis when calling Display.render().

        'backing_store' is an Image object that will be used for handling 
        expose events.  Damaged regions of the window will be redrawn from
        this Image.  If 'backing_store' is True, rather than an Image object,
        a new image will be automatically created for this purpose.
        """
        self.__dict__[ '_display' ] = _Imlib2.new_display(w, h)
        self.size = (w, h)
        self.width = w
        self.height = h
        self.blend = blend
        self.dither = dither
        self.set_cursor_hide_timeout(-1)
        self.set_backing_store(backing_store)

    def set_cursor_hide_timeout(self, timeout):
        """
        Hides mouse cursor after the specified timeout in seconds after no
        motion has occured.  A value of 0 makes the cursor permanently
        hidden, and -1 is permanently visible.)
        """
        self.cursor_timeout = timeout

    def set_backing_store(self, img):
        if img == True:
            img = new( (self.width, self.height) )
        self.backing_store = img
        if not self.expose_callback and img:
            self.expose_callback = self._handle_expose_default

    def _handle_expose_default(self, regions):
        if not self.backing_store:
            return

        for (pos, size) in regions:
            self._display.render(self.backing_store._image, pos, pos, size,
				    self.dither, self.blend)
        

    def render(self, image, dst_pos = (0, 0), src_pos = (0, 0),
               src_size = (-1, -1), dither = None, blend = None):
        """
        Renders the given image to the Window at the coordinates specified
        by 'dst_pos'.  The image will be offset by coordinates 'src_pos'.
        'src_size' specifies the target size of the rendered image.  A value
        of -1 for a dimension will use the image's original size for that
        dimension.  'dither' and 'blend' specifies whether the image will be
        dithered to the windows display depth, or alpha-blended onto the 
        display.  Both options will decrease performance at the expense of
        quality.  (However, if the image has no alpha channel, setting 'blend'
        has no effect.)  If neither of these options are specied, it will use
        the values that were passed to the constructor.
        """
        if blend == None:
            blend = self.blend
        if dither == None:
            dither = self.dither

        if not isinstance(image, Image):
            raise ValueError, image
        if self.backing_store and self.backing_store != image:
            self.backing_store.blend(image, src_pos, src_size, dst_pos, 
                                     merge_alpha = not blend)
        return self._display.render(image._image, dst_pos, src_pos, src_size,
				    dither, blend)

    def handle_events(self):
        """
        Handles pending X11 events.  Call this function regularly from within
        your mainloop.

        Returns: True if an event was handled, or False otherwise.
        """
        return self._display.handle_events(self.cursor_timeout)

    def __setattr__( self, key, value ):
        if key in ( 'input_callback', 'expose_callback' ):
            return setattr( self.__dict__[ '_display' ],
                    key, value )
        else:
            self.__dict__[ key ] = value

    def __getattr__( self, key ):
        if key in ( 'input_callback', 'expose_callback', 'socket' ):
            return getattr( self.__dict__[ '_display' ], key )
        else:
            return self.__dict__[ key ]


class Font:
    def __init__(self, fontdesc, color=(255,255,255,255)):
        """
        Create a new Font object.

        Arguments:
          fontdesc: the description of the font, in the form "Fontname/Size".
                    Only TrueType fonts are supported, and the .ttf file must
                    exist in a registered font path.  Font paths can be
                    registered by calling Imlib2.add_font_path().
             color: a 3- or 4-tuple holding the red, green, blue, and alpha
                    values of the color in which to render text with this
                    font context.  If color is a 3-tuple, the implied alpha
                    is 255.  If color is not specified, the default is fully
                    opaque white.
        """

        self._font = _Imlib2.load_font(fontdesc)
        sep = fontdesc.index("/")
        self.fontname = fontdesc[:sep]
        self.size = fontdesc[sep + 1:]
        self.set_color(color)


    def get_text_size(self, text):
        """
        Get the font metrics for the specified text as rendered by the
        current font.

        Arguments:
          text: the text for which to retrieve the metric.

        Returns: a 4-tuple containing the width, height, horizontal advance,
                 and vertical advance of the text when rendered.
        """
        return self._font.get_text_size(utf8(text))


    def set_color(self, color):
        """
        Sets the default color for text rendered with this font.

        Arguments:
            color: a 3- or 4-tuple holding the red, green, blue, and alpha
                   values of the color in which to render text with this
                   font context.  If color is a 3-tuple, the implied alpha
                   is 255.
        """
        if len(color) == 3:
            self.color = tuple(color) + (255,)
        else:
            self.color = color

    def __getattr__(self, attr):
        """
        These attributes are available:

               ascent: the current font's ascent value in pixels.
              descent: the current font's descent value in pixels.
          max_descent: the current font's maximum descent extent.
           max_ascent: the current font's maximum ascent extent.
        """
        if attr == "ascent":
            return self._font.ascent
        elif attr == "descent":
            return self._font.descent
        elif attr == "max_ascent":
            return self._font.max_ascent
        elif attr == "max_descent":
            return self._font.max_descent
        if attr not in self.__dict__:
            raise AttributeError, attr
        return self.__dict__[attr]


# Implement a crude image cache.
#
# Imlib2 maintains its own cache, but I don't think it caches
# the raw image data, since this ends up being faster.

_image_cache = {
    "images": {},
    "order": [],
    "size": 0,
    "max-size": 16*1024   # 16 MB
}

def open(file):
    """
    Create a new image object from the file 'file'.
    """
    if file in _image_cache["images"]:
        return _image_cache["images"][file].copy()

    image = Image(file)
    _image_cache["images"][file] = image
    _image_cache["order"].insert(0, file)
    _image_cache["size"] += image.width * image.height * 4 / 1024

    while _image_cache["size"] > _image_cache["max-size"]:
        file = _image_cache["order"].pop()
        expired = _image_cache["images"][file]
        del _image_cache["images"][file]
        _image_cache["size"] -= expired.width * expired.height * 4 / 1024

    return image


def new(size, bytes = None, from_format = "BGRA"):
    """
    Generates a new Image of size 'size', which is a tuple holding the width
    and height.  If 'bytes' is specified, the image is initialized from the
    raw BGRA data.
    """
    if 0 in size:
        raise ValueError, "Invalid image size %s" % repr(size)
    for val in size:
        if not isinstance(val, int):
            raise ValueError, "Invalid image size %s" % repr(size)
    if bytes:
        if False in map(lambda x: x in "RGBA", list(from_format)):
            raise ValueError, "Converting from unsupported format:",\
		  from_format
        if len(bytes) < size[0]*size[1]*len(from_format):
            raise ValueError, "Not enough bytes for converted format: "+\
		  "expected %d, got %d" % (size[0]*size[1]*len(from_format),
					   len(bytes))
        return Image(_Imlib2.create(size, bytes, from_format))
    else:
        return Image(_Imlib2.create(size))


def add_font_path(path):
    """
    Add the given path to the list of paths to scan when loading fonts.
    """
    _Imlib2.add_font_path(path)


def load_font(font, size):
    """
    Return a Font object from the given font specified in the form
    "FontName/Size", such as "Arial/16"
    """
    return Font(font + "/" + str(size))


def thumbnail_create(src, thumbnail_dir = ''):
    """
    Create a freedesktop.org thumbnail.
    """
    if thumbnail_dir:
        dst = thumbnail_dir + '/large/'
        if not os.path.isdir(dst):
            os.makedirs(dst, 0700)
        dst = dst + md5.md5('file://' + src).hexdigest() + '.'
    else:
        dst = _thumbnail_dir + md5.md5('file://' + src).hexdigest() + '.'
    if src.lower().endswith('jpg'):
        try:
            _Imlib2.epeg_thumbnail(src, dst + 'jpg', (256,256))
            return dst + 'jpg'
        except IOError:
            pass
    try:
        _Imlib2.png_thumbnail(src, dst + 'png', (256,256))
        return dst + 'png'
    except:
        # image is broken
        if thumbnail_dir:
            dst = thumbnail_dir + '/failed/pyimlib2/'
            if not os.path.isdir(dst):
                os.makedirs(dst, 0700)
            dst = dst + md5.md5('file://' + src).hexdigest() + '.png'
        else:
            dst = _failed_dir + md5.md5('file://' + src).hexdigest() + '.png'
        _Imlib2.fail_thumbnail(src, dst)
        return dst


def thumbnail_check(file, thumbnail_dir = ''):
    """
    Check if a freedesktop.org thumbnail exists. Return is either the filename,
    False when the thumbnail can't be created or None is no information is
    available.
    """
    if thumbnail_dir:
        dst = thumbnail_dir + '/large/' + md5.md5('file://' + file).hexdigest() + '.'
    else:
        dst = _thumbnail_dir + md5.md5('file://' + file).hexdigest() + '.'
    if os.path.isfile(dst + 'jpg'):
        return dst + 'jpg'
    if os.path.isfile(dst + 'png'):
        return dst + 'png'
    if thumbnail_dir:
        dst = thumbnail_dir + '/failed/pyimlib2/'
        dst = dst + md5.md5('file://' + file).hexdigest() + '.'
    else:
        dst = _failed_dir + md5.md5('file://' + file).hexdigest() + '.png'
    if os.path.isfile(dst):
        return False
    return None

