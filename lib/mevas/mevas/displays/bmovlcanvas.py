import mevas.rect as rect
import os
from bitmapcanvas import *
from mevas import imagelib

fifo_counter = 0

class BmovlCanvas(BitmapCanvas):

	def __init__(self, size):
		self.open_fifo()
		self.bmovl_visible = True
		self.send('SHOW\n')
		super(BmovlCanvas, self).__init__(size, preserve_alpha = True)
		self._update_rect = None


	def open_fifo(self):
		if os.path.exists(self.get_fname()):
			os.unlink(self.get_fname())
		os.mkfifo(self.get_fname())
		self.fifo = os.open(self.get_fname(), os.O_RDWR, os.O_NONBLOCK)

		
	def close_fifo(self):
		if self.fifo:
			try:
				os.close(self.fifo)
			except OSError:
				self.fifo = None
		if os.path.exists(self.get_fname()):
			os.unlink(self.get_fname())

		
	def get_fname(self):
		"""
		return fifo filename
		"""
		try:
			return self.__fname
		except AttributeError:
			pass
		global fifo_counter
		self.__fname = '/tmp/bmovl-%s-%s' % (os.getpid(), fifo_counter)
		fifo_counter += 1
		return self.__fname

		
	def send(self, msg):
		try:
			os.write(self.fifo, msg)
			return True
		except (IOError, OSError):
			return False
		
	def has_visible_child(self):
		for c in self.children:
			if c.visible and c.get_alpha():
				return True
		return False

	
	def _update_end(self, object = None):
		if not self._update_rect:
			return
		if not self.fifo:
			return

		if self.bmovl_visible and not self.has_visible_child():
			self.send('HIDE\n')
			self.send('CLEAR %s %s 0 0\n' % \
				  (self.width, self.height))
			self.bmovl_visible = False
			return

		# get update rect
		pos, size = self._update_rect
		# increase update rect because mplayer sometimes draws outside
		pos = (max(0, pos[0] - 2), max(pos[1] - 2, 0))
		size = (min(size[0] + 4, self.width), 
			min(size[1] + 4, self.height))

		img = imagelib.crop(self._backing_store, pos, size)
		self.send('RGBA32 %d %d %d %d %d %d\n' % \
			  (size[0], size[1], pos[0], pos[1], 0, 0))
		self.send(str(img.get_raw_data('RGBA')))
		self._update_rect = None

		if not self.bmovl_visible and self.has_visible_child():
			self.send('SHOW\n')
			self.bmovl_visible = True


	def _blit(self, img, r):
		if self._update_rect:
			self._update_rect = rect.union(r, self._update_rect)
		else:
			self._update_rect = r

# vim: ts=4
