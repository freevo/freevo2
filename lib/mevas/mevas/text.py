import types, time, math
from util import *

import imagelib
from image import *

class CanvasText(CanvasImage):

	# TODO: get default font and color from theme or something
	def __init__(self, text = None, font = "arial", size = 24, color = (255,255,255,255)):
		CanvasImage.__init__(self)
		self.fontname = self.size = None

		self.set_font(font, size)
		self.set_color(color)
		self.metrics = None
		if text:
			self.set_text(text, color)

	def __repr__(self):
		text = None
		if hasattr(self, "text"): text=self.text
		return "<CanvasText object at 0x%x: \"%s\">" % (id(self), text)



	def set_color(self, color):
		if not hasattr(self, "color") or color != self.color:
			self.color = color
			
			# Rerender text in new color
			if hasattr(self, "text"):
				self.set_text(self.text)


	def set_font(self, font, size = 24):
		try:
			if type(font) in types.StringTypes:
				self.font = imagelib.load_font(font, size)
			else:
				self.font = font
			if hasattr(self, "text") and (font, size) != (self.fontname, self.size):
				# Need to re-render text with new font and/or size.
				self.set_text(self.text)
		except IOError:
			print "Font %s/%d failed to load, so using default" % (font, size)
			self.font = imagelib.load_font("arial", 24)

		self.fontname, self.size = self.font.fontname, self.font.size


	def set_text(self, text, color = None, force = False):
		if hasattr(self, "text") and self.text == text and not force:
			return
		self.text = text
		self.metrics = metrics = self.font.get_text_size(text)
		self.new( (metrics[0] + 2, metrics[1]) )
		if not color:
			color = self.color
		self.draw_text(text + " ", (0, 0), font=self.font, color=color)
		self.needs_blitting(True)
		self.queue_paint()

	def get_text(self):
		return self.text

	def get_metrics(self):
		return self.metrics

#	def get_height(self):
#		return self.metrics[3]


# vim: ts=4
