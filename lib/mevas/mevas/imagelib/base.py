def get_capabilities():
	"""
	Returns a dictionary of capabilities for this backend.

	Required items are:
	    to-raw-formats: list of supported pixel formats that get_raw_data()
	                    supports.  e.g. BGRA, RGB, YV12A.
	  from-raw-formats: list of supported pixel formats that new() supports.
	  preferred-format: the native or preferred pixel format for the backend.
	                    When format parameters are unspecified, this is the
	                    default format.
	             shmem: If the backend supports writing raw data to shared
	                    shared memory.
	          pickling: If Image and Font objects can be pickled.
	           unicode: If the backend correctly supports unicode strings.
	       layer-alpha: If the alpha parameter in Image.blend() is supported.
	        alpha-mask: If Image.draw_mask() is supported.
	             cache: If the the backend implements an image cache.
	"""
	return {
	}


class Image(object):

	def __init__(self, image_or_filename):
		"""
		Create a new Image object wrapper for the given backend.

		Arguments:
		  image_or_filename: Instantiate the image from another Image
		                     instance, an instance of the backend's image
		                     class or type, or a file name from which to load
		                     the image.             
		"""
		pass


	def __getattr__(self, attr):
		"""
		These attributes must be available:

		      size: tuple containing the width and height of the image
		     width: width of the image
		    height: height of the image
		    format: format of the image if loaded from file (e.g. PNG, JPEG)
		  filename: filename if loaded from file
		"""

		if attr not in self.__dict__:
			raise AttributeError, attr
		return self.__dict__[attr]


	def get_raw_data(self, format = "RGBA"):
		"""
		Returns raw image data.

		Arguments:
		  format: pixel format of the raw data to be returned.  If 'format' is
		          not a supported format, raise ValueError.

		Returns: A string or buffer object containing the raw image data.
		"""
		pass


	def scale(self, (w, h)):
		"""
		Scale the image and return a new image.

		Arguments:
		  w, h: the width and height of the new image.  If either argument
		        is -1, that dimension is calculated from the other dimension
		        while retaining the original aspect ratio.

		Returns: a new Image instance representing the scaled image.
		"""
		
		pass

	def crop(self, (x, y), (w, h)):
		"""
		Crop the image and return a new image.

		Arguments:
		  x, y, w, h: represents the left, top, width, height region in
		              the image.

		Returns: a new Image instance representing the cropped image.
		"""
		pass

	def rotate(self, angle):
		"""
		Rotate the image and return a new image.

		Arguments:
		  angle: the angle in degrees by which to rotate the image.

		Return: a new Image instance representing the rotated image.
		"""
		pass

	def scale_preserve_aspect(self, (w, h)):
		"""
		Scales the image while retaining the original aspect ratio and return
		a new image.

		Arguments:
		  w, h: the maximum size of the new image.  The new image will be as
		        large as possible, using w, h as the upper limits, while
		        retaining the original aspect ratio.

		Return: a new Image insatnce represented the scaled image.
		"""
		pass


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
		pass


	def blend(self, srcimg, dst_pos = (0, 0), src_pos = (0, 0),
	          src_size = (-1, -1), alpha = 255, merge_alpha = True):
		"""
		Blends one image onto another.  

		Arguments:
		       srcimg: the image being blended onto 'self'
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
		pass

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
		pass

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
		pass

	def copy(self):
		"""
		Creates a copy of the current image.

		Returns: a new Image instance with a copy of the current image.
		"""
		pass

	def set_font(self, font_or_fontname):
		"""
		Sets the font context to font_or_font_name.  Subsequent calls to
		draw_text() will be rendered using this font.

		Arguments:
		  font_or_fontname: either a Font object, or a string containing the
		                    font's name and size.  This string is in the
		                    form "Fontname/Size" such as "Arial/16"


		Returns: a Font instance represent the specified font.  It
		         'font_or_fontname' is already a Font instance, it is simply
		         returned back to the caller.
		"""
		pass


	def get_font(self):
		"""
		Gets the current Font context.

		Returns: A Font instance as created by set_font() or None if no font
		         context is defined.
		"""
		pass


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
		pass

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
		pass

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
		pass


	def move_to_shmem(self, format = "RGBA", id = None):
		"""
		Creates a POSIX shared memory object and copy the image's raw data.  

		Arguments:
		  format: the format of the raw data to copy to shared memory.  If
		          the specified format is not supported, raise ValueError.
		      id: the name of the shared memory object (as passed to 
		          shm_open(3)).  If id is None, a suitable unique id is
		          generated.

		Returns: the id of the shared memory object.
		"""
		pass


	def save(self, filename, format = None):
		"""
		Saves the image to a file.

		Arguments:
		  format: the format of the written file (jpg, png, etc.).  If format
		          is None, the format is gotten from the filename extension.

		Returns: None.
		"""
		pass

	def get_capabilities(self):
		"""
		Get the capabilities of the imagelib backend used to create this
		image.
		"""
		return get_capabilities()


class Font:

	def __init__(self, fontdesc, color = (255, 255, 255, 255)):
		"""
		Create a new Font object wrapper.

		Arguments:
		  fontdesc: the description of the font, in the form "Fontname/Size".
		            Only TrueType fonts are supported, and the .ttf file must
		            exist in a registered font path.  Font paths can be
		            registered by calling imagelib.add_font_path().
  		     color: a 3- or 4-tuple holding the red, green, blue, and alpha 
		            values of the color in which to render text with this 
		            font context.  If color is a 3-tuple, the implied alpha 
		            is 255.  If color is not specified, the default is fully
		            opaque white.

		"""
		pass

	def get_text_size(self, text):
		"""
		Get the font metrics for the specified text as rendered by the 
		current font.

		Arguments:
		  text: the text for which to retrieve the metric.

		Returns: a 4-tuple containing the width, height, horizontal advance,
		         and vertical advance of the text when rendered.
		"""
		pass

	def set_color(self, color):
		"""
		Sets the default color for text rendered with this font.

		Arguments:
  		  color: a 3- or 4-tuple holding the red, green, blue, and alpha 
		         values of the color in which to render text with this 
		         font context.  If color is a 3-tuple, the implied alpha 
		         is 255.
		"""
		pass

	def __getattr__(self, attr):
		"""
		These attributes must be available:

		       ascent: the current font's ascent value in pixels.
		      descent: the current font's descent value in pixels.
		  max_descent: the current font's maximum descent extent.
		   max_ascent: the current font's maximum ascent extent.
		"""
		if attr not in self.__dict__:
			raise AttributeError, attr
		return self.__dict__[attr]


# These methods must be provided by the backend and are accessed by
# imagelib.functionname when the backend is loaded.

def open(file):
	"""
	Opens a file and returns an Image instance.

	Arguments:
	  file: the filename of the image to load.

	Returns: a new Image instance representing the file.
	"""
	pass

def new(size, rawdata = None, from_format = "RGBA"):
	"""
	Creates a new image and returns an Image instance.

	Arguments:
	         size: a tuple containing the width and height of the new image.
	      rawdata: the raw image data from which to create the new image.  If
	               rawdata is not None, it is expected to be in the same
	               format as specified by from_format, and be the required
	               size.  If the size is invalid, raise ValueError.  If
	               rawdata is not None, the all pixels are initialized to
	               fully transparent.
	  from_format: the format the raw data is specified in.  If the format is
	               not a supported format by this backend, raise ValueError.

	Returns: a new Image instance, either blank if rawdata is not specified,
	         or initialized from rawdata.
	"""
	pass

def add_font_path(path):
	"""
	Adds a path to the list of paths scanned when loading fonts.

	Arguments:
	  path: the path name to add.

	Returns: None.
	"""
	pass
                                                                                                                                   
def load_font(font, size):
	"""
	Load the specified font and return a new Font instance.

	Arguments:
	  font: the name of the font to load.
	  size: the size of font.

	Returns: a new Font instance representing the specified font.
	"""
	pass
