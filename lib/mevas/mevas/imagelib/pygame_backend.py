import pygame, types
import base

def get_capabilities():
	return {
		"to-raw-formats": [ "RGBA", "RGB" ],
		"from-raw-formats": [ "RGBA", "RGB" ],
		"preferred-format": "RGBA",  # Native format
		"shmem": False,
		"pickling": True,
		"unicode": True,
		"layer-alpha": True,
		"alpha-mask": False,
		"cache": False 

	}


# TODO: Finish me.


class Image(base.Image):
	def __init__(self, image_or_filename):
		if isinstance(image_or_filename, Image):
			self._image = image_or_filename._image
		elif type(image_or_filename) == pygame.Surface:
			self._image = image_or_filename
		elif type(image_or_filename) in types.StringTypes:
			self._image = pygame.image.load(image_or_filename)
		else:
			raise ValueError, "Unsupported image type: %s" % type(image_or_filename)


	def __getattr__(self, attr):
		if attr == "size":
			return self._image.get_size()
		elif attr == "width":
			return self._image.get_width()
		elif attr == "height":
			return self._image.get_height()
		# FIXME: implement format, mode, filename

		return super(Image, self).__getattr__(attr)

	def get_capabilities(self):
		return get_capabilities()
	


def open(file):
	return Image(file)

def new(size, rawdata = None, from_format = "RGBA"):
	if from_format not in get_capabilities()["from-raw-formats"]:
		raise ValueError, "Unsupported raw format: %s" % from_format
	if rawdata:
		return Image( pygame.image.fromstring(rawdata, size, from_format) )
	return Image( pygame.Surface(size) )

def add_font_path(path):
	pass

def load_font(font, size):
	pass
