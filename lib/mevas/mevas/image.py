import types, time, math
from util import *

import imagelib
from canvasobject import *

class CanvasImage(CanvasObject):

	def __init__(self, image_or_size = None):
		CanvasObject.__init__(self)

		self.image = None
		if type(image_or_size) == types.TupleType:
			if 0 in image_or_size:
				raise ValueError, "Invalid dimension for CanvasImage %s" % repr(image_or_size)
			self.new(image_or_size)
		else:
			self.set_image(image_or_size)
			if not self.image.has_alpha:
				self.set_alpha(256)
			
	def needs_blitting(self, blit = None):
		"""
		Sets whether or not the image needs blitting (i.e. the actual image
		data has changed, not just its attributes like position, zindex,
		etc.).  If True, the image will get blitted on the next paint.

		With no arguments, it just returns the last value passed.
		"""
		if blit == None:
			return self._needs_blitting
		self._needs_blitting = blit

	def _image_changed(self):
		self.set_size(self.image.size)
		self.needs_blitting(True)
		self.queue_paint()

	def scale(self, dst_size, src_pos = (0,0), src_size = (-1, -1)):
		"""
		Scale the image to the given 'size', where 'size' is a tuple holding the
		new width and height.
		"""
		# Clamp dimensions to multiples of two
		# FIXME: we only really need to do this for MPlayerCanvas since it
		# stores images in YV12.
		#w, h = dst_size
		#if w % 2: w = int(math.ceil(w / 2.0)) * 2
		#if h % 2: h = int(math.ceil(h / 2.0)) * 2
		self.image.scale(dst_size, src_pos, src_size)
		self._image_changed()


	def crop(self, pos, size):
		"""
		Crop the image at position 'pos', a tuple holding the left and
		top coordinates, to the size 'size', a tuple holding the new
		width and height.
		"""
		self.image.crop(pos, size)
		self._image_changed()

	def rotate(self, angle):
		"""
		Rotate the image by the given angle.
		"""
		self.image.rotate(angle)
		self._image_changed()

	def flip(self):
		self.image.flip()
		self._image_changed()

	def mirror(self):
		self.image.mirror()
		self._image_changed()

	def draw_mask(self, mask_image, pos = (0, 0)):
		"""
		Draw 'mask_image' over top of the existing image.  The luma channel of
		the mask image is blended with the alpha channel of the existing 
		image.
		"""
		if type(mask_image) in types.StringTypes:
			mask_image = imagelib.open(mask_image)
		elif isinstance(mask_image, CanvasImage):
			mask_image = mask_image.image

		self.image.draw_mask(mask_image, pos)
		self._image_changed()


	def draw_image(self, image, dst_pos = (0, 0), dst_size = (-1, -1), 
	               src_pos = (0, 0), src_size = (-1, -1), alpha = 255):
		"""
		Draws (and blends) another image 'image' on top of the existing image,
		at position 'pos', a tuple containing the left and top coordinates 
		relative to the destination image with layer alpha 'alpha'
		"""
		if type(image) in types.StringTypes:
			image = imagelib.open(image)
		elif isinstance(image, CanvasImage):
			image = image.image
		if not self.image:
			if dst_size != (-1, -1):
				image.scale(dst_size)
			else:
				self.image = image
		else:
			self.image.blend(image, dst_pos, dst_size, src_pos, src_size, alpha)
		self._image_changed()


	def get_image(self, image):
		return self.image

	def set_image(self, image):
		"""
		Sets the image for this object to 'image'
		"""
		if type(image) in types.StringTypes:
			self.filename = image
			image = imagelib.open(image)
		elif isinstance(image, CanvasImage):
			image = image.image.copy()
			self.filename = None
		if self.image == image:
			return
		if image == None:
			self.reset()

		self.image = image
		self._image_changed()


	def draw_text(self, text, pos = (0, 0), font = "arial", size = 24, color = (255,255,255,255)):
		"""
		Draws the given text over the image at position 'pos', a tuple holding
		the left and top coordinates, with the supplied font, size, and color.
		color is a tuple holding the RGBA values for the text.
		"""
		if type(font) in types.StringTypes:
			font = imagelib.load_font(font, size)
		metrics = self.image.draw_text(pos, text, color, font)
		self._image_changed()
		return metrics

	def draw_rectangle(self, pos, size, color = (255, 255, 255, 255), fill = True):
		#print "Draw rect", pos, size, color, fill
		self.image.draw_rectangle(pos, size, color, fill)
		self._image_changed()

	def draw_ellipse(self, center_pos, amplitude, color = (255, 255, 255, 255), fill = True):
		self.image.draw_ellipse(center_pos, amplitude, color, fill)
		self._image_changed()


	def new(self, size):
		"""
		Initialize a blank image to the given size, a tuple containing the
		new width and height.
		"""
		self.image = imagelib.new(size)
		self.filename = None
		self._image_changed()

	def get_size(self):
		if not self.image:
			return 0, 0
		return self.image.width, self.image.height

	def reset(self):
		CanvasObject.reset(self)
		self.needs_blitting(True)

	def save(self, filename):
		return self.image.save(filename)


# vim: ts=4
