import Imlib2, types
import base


def get_capabilities():
	return {
		"to-raw-formats": [ "BGRA", "BGR", "ABGR", "RGBA", "RGB", "ARGB", "YV12A" ],
		"from-raw-formats": [ "BGRA", "ABGR", "RGBA", "ARGB", "BGR", "RGB" ],
		"preferred-format": "BGRA",  # Native format
		"shmem": True,
		"pickling": True,
		"unicode": True,
		"layer-alpha": True,
		"alpha-mask": True,
		"cache": True

	}


class Image(base.Image):

	def __init__(self, image_or_filename):
		if isinstance(image_or_filename, Image):
			self._image = image_or_filename._image
		elif isinstance(image_or_filename, Imlib2.Image):
			self._image = image_or_filename
		elif type(image_or_filename) in types.StringTypes:
			self._image = Imlib2.Image(image_or_filename)
		else:
			raise ValueError, "Unsupported image type: %s" % type(image_or_filename)
	def __getattr__(self, attr):
		if attr in ("width", "height", "size", "format", "mode", "filename", "has_alpha", "rowstride", "get_pixel"):
			return getattr(self._image, attr)
		return super(Image, self).__getattr__(attr)

	def get_raw_data(self, format = "BGRA"):
		return self._image.get_bytes(format)

	def rotate(self, angle):
		while angle >= 360: angle -= 360
		while angle <= -360: angle += 360
		if angle == 0:
			return

		if angle % 90 == 0:
			f = { 90: 1, 180: 2, 270: 3, -90: 3, -180: 2, -270: 1} [ angle ]
			self._image.orientate(f)
		else:
			self._image = self._image.rotate(angle) 

	def flip(self):
		self._image.flip_vertical()

	def mirror(self):
		self._image.flip_horizontal()

	def scale(self, size, src_pos = (0, 0), src_size = (-1, -1)):
		self._image =  self._image.scale(size, src_pos, src_size) 

	def blend(self, srcimg, dst_pos = (0, 0), dst_size = (-1, -1), 
	          src_pos = (0, 0), src_size = (-1, -1), 
	          alpha = 255, merge_alpha = True):
		return self._image.blend(srcimg._image, src_pos, src_size, dst_pos, dst_size, alpha, merge_alpha)

	def clear(self, pos = (0, 0), size = (-1, -1)):
		self._image.clear( pos, size )

	def draw_mask(self, maskimg, pos):
		return self._image.draw_mask(maskimg._image, pos)

	def copy(self):
		return Image( self._image.copy() )

	def set_font(self, font_or_fontname):
		if isinstance(font_or_fontname, Font):
			font_or_fontname = font_or_fontname._font
		return self._image.set_font(font_or_fontname._font)

	def get_font(self):
		return Font(self._image.get_font())
		
	def draw_text(self, pos, text, color = None, font_or_fontname = None):
		if isinstance(font_or_fontname, Font):
			font_or_fontname = font_or_fontname._font
		return self._image.draw_text(pos, text, color, font_or_fontname)	

	def draw_rectangle(self, pos, size, color, fill = True):
		return self._image.draw_rectangle(pos, size, color, fill)

	def draw_ellipse(self, center, size, amplitude, fill = True):
		return self._image.draw_ellipse(center, size, amplitude, fill)

	def move_to_shmem(self, format = "BGRA", id = None):
		return self._image.move_to_shmem(format, id)

	def save(self, filename, format = None):
		return self._image.save(filename)

	def get_capabilities(self):
		return get_capabilities()


	def crop(self, pos, size):
		self._image = self._image.crop(pos, size)

	def scale_preserve_aspect(self, size):
		self._image = self._image.scale_preserve_aspect(size)

	def copy_rect(self, src_pos, size, dst_pos):
		self._image.copy_rect(src_pos, size, dst_pos)


class Font(base.Font):

	def __init__(self, fontdesc, color = (255, 255, 255, 255)):
		self._font = Imlib2.Font(fontdesc, color)

	def get_text_size(self, text):
		return self._font.get_text_size(text)

	def set_color(self, color):
		return self._font.set_color(color)

	def __getattr__(self, attr):
		if attr in ("ascent", "descent", "max_ascent", "max_descent"):
			return getattr(self._font, attr)
		return super(Font, self).__getattr__(attr)


def scale(image, size, src_pos = (0, 0), src_size = (-1, -1)):
	image = image.copy()
	image.scale(size, src_pos, src_size)
	return image

def crop(image, pos, size):
	image = image.copy()
	image.crop(pos, size)
	return image

def rotate(image, angle):
	image = image.copy()
	image.rotate(angle)
	return image

def scale_preserve_aspect(image, size):
	image = image.copy()
	image.scale_preserve_aspect(size)
	return image



def open(file):
	return Image(file)

def new(size, rawdata = None, from_format = "BGRA"):
	if from_format not in get_capabilities()["from-raw-formats"]:
		raise ValueError, "Unsupported raw format: %s" % from_format
	return Image( Imlib2.new(size, rawdata, from_format) )

def add_font_path(path):
	return Imlib2.add_font_path(path)

def load_font(font, size):
	return Imlib2.load_font(font, size)


