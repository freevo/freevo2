import time
import mevas
import Imlib2

from bitmapcanvas import *

class Imlib2Canvas(BitmapCanvas):


	def __init__(self, size, dither = True, blend = False):
		super(Imlib2Canvas, self).__init__(size, preserve_alpha = blend)
		self._display = Imlib2.Display(size, dither, blend)

	def _blit(self, img, r):
		pos, size = r
		t0=time.time()

		if isinstance(img, mevas.imagelib.get_backend("imlib2").Image):
			self._display.render(img._image, pos, pos, size)
		else:
			if img.size != size:
				img = imagelib.crop(img, pos, size)
                                                                                                                                   
			data = img.get_raw_data("RGB")
			img = Imlib2.new( size, data, "RGB" )
			self._display.render(img, pos)

		print "Blit", r, "took", time.time()-t0, r



# vim: ts=4
