import mevas.rect as rect
import os
from bitmapcanvas import *

class BmovlCanvas(BitmapCanvas):

	def __init__(self, size):
		super(BmovlCanvas, self).__init__(size, preserve_alpha = True)
		self._update_rect = None
		self.fifo = os.open('/tmp/bmovl-%s' % os.getpid(), os.O_WRONLY)
		self.bmovl_visible = True
		try:
			os.write(self.fifo, 'SHOW\n')
		except (IOError, OSError):
			print 'IOError on bmovl.fifo'


	def has_visible_child(self):
		for c in self.children:
			if c.visible and c.get_alpha():
				return True
		return False

	
	def _update_end(self, object = None):
		if not self._update_rect:
			return
		if not self.fifo:
			print 'IOError: no bmovl fifo'
			return

		if self.bmovl_visible and not self.has_visible_child():
			print 'bmovl hide'
			try:
				os.write(self.fifo, 'HIDE\n')
				os.write(self.fifo, 'CLEAR %s %s 0 0\n' % \
					 (self.width, self.height))
			except (IOError, OSError):
				print 'IOError on bmovl.fifo'
			self.bmovl_visible = False
			return
		
		pos, size = self._update_rect
		img = imagelib.crop(self._backing_store, pos, size)
		try:
			print 'bmovl update', pos, size
			os.write(self.fifo, 'RGBA32 %d %d %d %d %d %d\n' % \
				 (size[0], size[1], pos[0], pos[1], 0, 0))

			os.write(self.fifo, str(img.get_raw_data('RGBA')))
		except (IOError, OSError):
			print 'IOError on bmovl.fifo'
		self._update_rect = None

		if not self.bmovl_visible and self.has_visible_child():
			print 'bmovl show'
			try:
				os.write(self.fifo, 'SHOW\n')
			except (IOError, OSError):
				print 'IOError on bmovl.fifo'
			self.bmovl_visible = True


	def _blit(self, img, r):
		if self._update_rect:
			self._update_rect = rect.union(r, self._update_rect)
		else:
			self._update_rect = r

# vim: ts=4
