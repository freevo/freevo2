import time, mevas

from mevas.util import *
from mevas.canvas import *
from mevas.image import *
from mevas.text import *

class BitmapCanvas(Canvas):
	"""
	Canvas that renders to a bitmap.  This canvas isn't very useful by itself,
	but is intended to be derived by bitmap-based displays.  This canvas uses
	CanvasContainer._get_backing_store to do the heavy lifting, so most of
	the real logic can be found in that function.

	Derived classes will have to implement _blit(), and likely also 
	_update_end() to flip the buffered page.
	"""

	def __init__(self, size, preserve_alpha = False, blit_once = True, slices = False):
		super(BitmapCanvas, self).__init__(size)
		self._preserve_alpha = preserve_alpha
		self._blit_once = blit_once
		self._slices = slices
		self._blit_rects = []
		self._canvas_frozen = 0
		self._backing_store_with_alpha = mevas.imagelib.new(size)

	def _update_begin(self, object = None):
		# Returning False here will abort the update, such as if the display
		# is not yet initialized or otherwise ready for blitting.
		return True

	def _update_end(self, object = None):
		# We don't do anything here, but subclasses will probably flip page
		# so what we drew in _blit() gets updated on the display.
		return True

	def freeze(self):
		self._canvas_frozen += 1

	def thaw(self):
		if self._canvas_frozen > 0:
			self._canvas_frozen -= 1
			if self._canvas_frozen == 0 and len(self._blit_rects):
				self._update_begin()
				img = self._get_backing_store(use_cached = True)[0]
				self._blit_regions( img, self._blit_rects )
				self._update_end()
				self._blit_rects = []


	def child_paint(self, child, force_children = False):
		img, dirty_rects = self._get_backing_store(update = True, update_object = child, clip = True,
		                                           preserve_alpha = self._preserve_alpha)
		if len(dirty_rects) == 0:
			return

		if self._canvas_frozen > 0:
			self._blit_rects = rect.reduce(self._blit_rects + dirty_rects)
		else:
			self._blit_regions(img, dirty_rects)


	def _blit_regions(self, img, regions):
		# Merge the regions into one big union of blit_once is True
		if self._slices:
			new_regions = []
			for ((x, y), (w, h)) in regions:
				new_regions.append( ((0, y), (img.width, h)), )
			regions = new_regions
			
		if self._blit_once:
			region = regions.pop()
			while regions:
				region = rect.union(region, regions.pop())
			regions = [region]
			
		# It's the container's responsibility to apply children's alpha
		# values.  But there is no parent of the canvas to do that, so we
		# do that here if it's necessary.
		if self.alpha < 255:
			t0=time.time()
			if self._preserve_alpha:
				self._backing_store_with_alpha.clear()
				self._backing_store_with_alpha.blend(img, alpha = self.alpha)
			else:
				self._backing_store_with_alpha.draw_rectangle( (0, 0), img.size, (0, 0, 0, 255), fill = True)
				self._backing_store_with_alpha.blend(img, alpha = self.alpha, merge_alpha = False)

			img = self._backing_store_with_alpha

		regions = rect.optimize_for_rendering(regions)
		for r in regions:
			# Clip rectangle to screen.
			r = rect.intersect( r, ((0, 0), self.get_size()) )
			if r == rect.empty:
				continue
			self._blit(img, r)

	def _blit(self, img, r):
		pass

	def rebuild(self):
		self.queue_paint()
		self.update()

	def child_deleted(self, child):
		# If we have rendered this child to the backing store, we need to
		# queue its parent for redraw so that the child gets visibly removed
		# on the next update().  The child's rectangle was dirtied on the
		# backing store by remove_child(), so all we need to do is ensure it
		# gets drawn on the next update.
		if child.get_parent() and hasattr(child, "_backing_store_info"):
			#print "Child deleted", child
			child.parent().queue_paint()


# vim: ts=4
