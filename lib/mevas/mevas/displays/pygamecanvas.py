import mevas
import mevas.rect as rect

import pygame
import time

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
		if self._screen.get_bitsize() != 32:
			# if the bitsize is not 32 as requested, we need
			# a tmp surface to convert from imlib2 to pygame
			# because imlib2 uses 32 bit and with a different
			# value memcpy will do nasty things
			self._surface = pygame.Surface(size, 0, 32)
		self._rect = []


	def _update_end(self, object = None):
		if not self._rect:
			return
		if hasattr(self, '_surface'):
			self._backing_store._image.to_sdl_surface(self._surface)
			for pos, size in self._rect:
				self._screen.blit(self._surface, pos, pos + size)
		else:
			self._backing_store._image.to_sdl_surface(self._screen)
		pygame.display.update(self._rect)
		self._rect = []


	def _blit(self, img, r):
		if isinstance(img, mevas.imagelib.get_backend("imlib2").Image):
			pass
		elif isinstance(img, mevas.imagelib.get_backend("pygame").Image):
			# FIXME: add code for native pygame images here.
			pass
		else:
			# FIXME: add code for not imlib2 images here
			pass
		self._rect.append(r)

# vim: ts=4
