from gtk import gdk
import pango
import types
import base


def get_capabilities():
	return {
		"to-raw-formats": [ "RGB", "RGBA" ],
		"from-raw-formats": [ "RGB", "RGBA" ],
		"preferred-format": "RGBA",  # Native format
		"shmem": False,
		"pickling": True,
		"unicode": True,
		"layer-alpha": True,
		"alpha-mask": False, # ?
		"cache":  False  # ?

	}


class Image(base.Image):

	def __init__(self, image_or_filename):
		self.filename = None

		if isinstance(image_or_filename, Image):
			self._image = image_or_filename._image
			self.filename = image_or_filename.filename
		elif isinstance(image_or_filename, gdk.Pixbuf):
			self._image = image_or_filename
		elif type(image_or_filename) in types.StringTypes:
			self._image = gdk.pixbuf_new_from_file(image_or_filename)
			self.filename = image_or_filename
		else:
			raise ValueError, "Unsupported image type: %s" % type(image_or_filename)

	def __getattr__(self, attr):
		if attr == "width":
			return self._image.get_width()
		elif attr == "height":
			return self._image.get_height()
		elif attr == "size":
			return self._image.get_width(), self._image.get_height()
		elif attr == "format":
			return None
		elif attr == "mode":
			if self._image.get_has_alpha():
				return "RGBA"
			return "RGB"
		return super(Image, self).__getattr__(attr)

	def get_raw_data(self, format = "RGBA"):
		return self._image.get_pixels()
		#return self._image.get_bytes(format)

	def scale(self, size, src_pos = (0, 0), src_size = (-1, -1)):
		pass
		#return Image( self._image.scale(size, src_pos, src_size) )

	def crop(self, pos, size):
		pass
		#return Image( self._image.crop(pos, size) )

	def rotate(self, angle):
		pass
		#return Image( self._image.rotate(angle) )

	def scale_preserve_aspect(self, size):
		pass
		#return Image( self._image.scale_preserve_aspect(size) )

	def copy_rect(self, src_pos, size, dst_pos):
		pass
		#return self._image.copy_rect( src_pos, size, dst_pos )

	def blend(self, srcimg, dst_pos = (0, 0), dst_size = (-1, -1),
	          src_pos = (0, 0), src_size = (-1, -1),
	          alpha = 255, merge_alpha = False):
		pass
		#return self._image.blend(srcimg._image, src_pos, src_size, dst_pos, dst_size, alpha, merge_alpha)

	def clear(self, pos = (0, 0), size = (-1, -1)):
		pass
		#self._image.clear( pos, size )

	def draw_mask(self, maskimg, pos):
		pass
		#return self._image.draw_mask(maskimg._image, pos)

	def copy(self):
		pass
		#return Image( self._image.copy() )

	def set_font(self, font_or_fontname):
		pass
		#if isinstance(font_or_fontname, Font):
		#	font_or_fontname = font_or_fontname._font
		#return self._image.set_font(font_or_fontname._font)

	def get_font(self):
		pass
		#return Font(self._image.get_font())
		
	def draw_text(self, pos, text, color = None, font_or_fontname = None):
		pass
		#if isinstance(font_or_fontname, Font):
		#	font_or_fontname = font_or_fontname._font
		#return self._image.draw_text(pos, text, color, font_or_fontname)	

	def draw_rectangle(self, pos, size, color, fill = True):
		pass
		#return self._image.draw_rectangle(pos, size, color, fill)

	def draw_ellipse(self, center, size, amplitude, fill = True):
		pass
		#return self._image.draw_ellipse(center, size, amplitude, fill)

	def move_to_shmem(self, format = "BGRA", id = None):
		pass

	def save(self, filename, format = None):
		pass
		#return self._image.save(filename)

	def get_capabilities(self):
		return get_capabilities()


class Font(base.Font):

	def __init__(self, fontdesc, color = (255, 255, 255, 255)):
		pass
		#self._font = Imlib2.Font(fontdesc, color)

	def get_text_size(self, text):
		pass
		#return self._font.get_text_size(text)

	def set_color(self, color):
		pass
		#return self._font.set_color(color)

	def __getattr__(self, attr):
		if attr in ("ascent", "descent", "max_ascent", "max_descent"):
			return None
		return super(Font, self).__getattr__(attr)


def open(file):
	return Image(file)

def new((w, h), rawdata = None, from_format = "BGRA"):
	if from_format not in get_capabilities()["from-raw-formats"]:
		raise ValueError, "Unsupported raw format: %s" % from_format
	if rawdata:
		has_alpha, bpp = { "RGBA": (True, 4), "RGB": (False, 3) } [from_format]
		return Image( gdk.pixbuf_new_from_data(rawdata, gdk.COLORSPACE_RGB, 
		                  has_alpha, 8, w, h, w*bpp) )
	else:
		return Image( gdk.Pixbuf(gdk.COLORSPACE_RGB, True, 8, w, h) )

def add_font_path(path):
	pass

def load_font(font, size):
	pass


