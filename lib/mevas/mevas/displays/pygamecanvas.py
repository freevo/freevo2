import time
import mevas
import pygame

from bitmapcanvas import *
from pygame.locals import *

class PygameCanvas(BitmapCanvas):

	def __init__(self, size):
		super(PygameCanvas, self).__init__(size, preserve_alpha = False)
		pygame.init()
		self._screen = pygame.display.set_mode(size)

	def _blit(self, img, r):
		pos, size = r
		t0=time.time()

		if isinstance(img, mevas.imagelib.get_backend("pygame").Image):
			# FIXME: add code for native pygame images here.
			pass
		else:
			t1=time.time()
			if img.size != size:
				img = imagelib.crop(img, pos, size)

			data = img.get_raw_data("RGB")
			# pygame.image.fromstring refuses to read from a buffer :(
			img = pygame.image.fromstring( str(data), size, "RGB")
			print "Conversion took", time.time()-t1
			self._screen.blit(img, pos)

		pygame.display.update(r)
		print "Blit", r, "took", time.time()-t0


# vim: ts=4
