import mevas
import mevas.rect as rect

import pygame

from bitmapcanvas import *
from pygame.locals import *

class PygameCanvas(BitmapCanvas):

	def __init__(self, size):
		super(PygameCanvas, self).__init__(size, preserve_alpha = False)

		# Initialize the PyGame modules.
		if not pygame.display.get_init():
			pygame.display.init()
			pygame.font.init()

		self._screen  = pygame.display.set_mode(size, 0, 32)
		self._surface = pygame.Surface(size, 0, 32)
		self._rect    = []


	def _update_end(self, object = None):
		if not self._rect:
			return
		self._rect = rect.optimize_for_rendering(self._rect)
		self._backing_store._image.to_sdl_surface(self._surface)
		for pos, size in self._rect:
			self._screen.blit(self._surface, pos, pos + size)
		pygame.display.update(self._rect)
		self._rect = []

	def _blit(self, img, r):
		if isinstance(img, mevas.imagelib.get_backend("pygame").Image):
			# FIXME: add code for native pygame images here.
			pass
		if isinstance(img, mevas.imagelib.get_backend("imlib2").Image):
			pass
		else:
			# FIXME: add code for not imlib2 images here
			pass
		self._rect.append(r)


# vim: ts=4
