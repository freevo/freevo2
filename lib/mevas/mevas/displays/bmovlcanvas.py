import mevas.rect as rect
import os
from bitmapcanvas import *
from mevas import imagelib

class BmovlCanvas(BitmapCanvas):

	def __init__(self, size):
		super(BmovlCanvas, self).__init__(size, preserve_alpha = True)
		self._update_rect = None
		self.fifo = os.open('/tmp/bmovl-%s' % os.getpid(), os.O_WRONLY)
		self.bmovl_visible = True
		self.send('SHOW\n')


	def send(self, msg):
		try:
			os.write(self.fifo, msg)
			return True
		except (IOError, OSError):
			print 'IOError on bmovl.fifo'
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
			print 'IOError: no bmovl fifo'
			return

		if self.bmovl_visible and not self.has_visible_child():
			print 'bmovl hide'
			self.send('HIDE\n')
			self.send('CLEAR %s %s 0 0\n' % \
				  (self.width, self.height))
			self.bmovl_visible = False
			return
		
		pos, size = self._update_rect
		img = imagelib.crop(self._backing_store, pos, size)
		print 'bmovl update', pos, size
		self.send('RGBA32 %d %d %d %d %d %d\n' % \
			  (size[0], size[1], pos[0], pos[1], 0, 0))
		self.send(str(img.get_raw_data('RGBA')))
		self._update_rect = None

		if not self.bmovl_visible and self.has_visible_child():
			print 'bmovl show'
			self.send('SHOW\n')
			self.bmovl_visible = True


	def _blit(self, img, r):
		if self._update_rect:
			self._update_rect = rect.union(r, self._update_rect)
		else:
			self._update_rect = r

# vim: ts=4
