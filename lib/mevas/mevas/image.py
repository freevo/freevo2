import types, time, math
from util import *

import imagelib
from canvasobject import *

class CanvasImage(CanvasObject):

	def __init__(self, image_or_size = None):
		CanvasObject.__init__(self)

		self.image = None
		if type(image_or_size) == types.TupleType:
			self.new(image_or_size)
		else:
			self.set_image(image_or_size)

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

	def scale(self, size):
		"""
		Scale the image to the given 'size', where 'size' is a tuple holding the
		new width and height.
		"""
		w, h = size

		# Clamp dimensions to multiples of two
		# FIXME: we only really need to do this for MPlayerCanvas since it
		# stores images in YV12.
		#if w % 2: w = int(math.ceil(w / 2.0)) * 2
		#if h % 2: h = int(math.ceil(h / 2.0)) * 2
		self.image = self.image.scale((w, h))
		self.set_size(self.image.size)
		self.needs_blitting(True)
		self.queue_paint()


	def crop(self, pos, size):
		"""
		Crop the image at position 'pos', a tuple holding the left and
		top coordinates, to the size 'size', a tuple holding the new
		width and height.
		"""
		self.image = self.image.crop(pos, size)
		self.set_size(size)
		self.needs_blitting(True)
		self.queue_paint()

	def rotate(self, angle):
		"""
		Rotate the image by the given angle.
		"""

		# FIXME: this seems broken.

		self.image = self.image.rotate(angle)
		self.set_size((self.image.size[0], self.image.size[1]))
		self.needs_blitting(True)
		self.queue_paint()

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
		self.needs_blitting(True)
		self.queue_paint()


	def draw_image(self, image, dst_pos = (0, 0), src_pos = (0, 0), src_size = (-1, -1), alpha = 255):
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
			self.image = image
		else:
			self.image.blend(image, dst_pos, src_pos, src_size, alpha)
		self.needs_blitting(True)
		self.queue_paint()


	def set_image(self, image):
		"""
		Sets the image for this object to 'image'
		"""
		if type(image) in types.StringTypes:
			self.filename = image
			image = imagelib.open(image)
		elif isinstance(image, CanvasImage):
			image = image.image

		if self.image == image:
			return
		if image == None:
			self.reset()

		self.image = image
		self.set_size((image.size[0], image.size[1]))
		self.needs_blitting(True)
		self.queue_paint()


	def draw_text(self, text, pos = (0, 0), font = "arial", size = 24, color = (255,255,255,255)):
		"""
		Draws the given text over the image at position 'pos', a tuple holding
		the left and top coordinates, with the supplied font, size, and color.
		color is a tuple holding the RGBA values for the text.
		"""
		if type(font) in types.StringTypes:
			font = imagelib.load_font(font, size)
		metrics = self.image.draw_text(pos, text, color, font)
		self.needs_blitting(True)
		self.queue_paint()
		return metrics

	def draw_rectangle(self, pos, size, color = (255, 255, 255, 255), fill = False):
		self.image.draw_rectangle(pos, size, color, fill)

	def draw_ellipse(self, center_pos, amplitude, color = (255, 255, 255, 255), fill = False):
		self.image.draw_ellipse(center_pos, amplitude, color, fill)


	def new(self, size):
		"""
		Initialize a blank image to the given size, a tuple containing the
		new width and height.
		"""
		self.image = imagelib.new(size)
		self.filename = None
		self.needs_blitting(True)
		self.set_size(size)


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