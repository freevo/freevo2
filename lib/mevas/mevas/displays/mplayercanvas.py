import types, time, math
from mevas.util import *
from kaa import Imlib2

from mevas.canvas import *
from mevas.image import *
from mevas.text import *

class MPlayerCanvas(Canvas):
	"""
	Canvas that uses bmovl2 MPlayer filter for rendering.
	"""

	# Counter for bmovl2 image ids.
	_img_id_counter = 0

	def __init__(self, size, overlay = None, x_adjust = 1.0):
		"""
		Initialize canvas.  'overlay' is an mplayer.Overlay object and
		size is a tuple holding the width and height of the canvas.
		(Presumably enforced by calling MPlayer with -vf expand=width:height 
		"""

		Canvas.__init__(self, size)
		self.set_overlay(overlay)
		# Keep track of objects which are deleted so that we can delete them
		# from bmovl2 on the next update.
		self._deleted_ids = []
		# Keep track of canvas objects' attributes (like alpha, zindex, etc.)
		# so we only need to update the ones that have changed.
		self._cached_values = {}
		self._x_adjust = x_adjust
		self.atom = 0


	def set_overlay(self, overlay):
		self.overlay = make_weakref(overlay, lambda x: self.set_overlay(None))
		if self.overlay:
			self.rebuild()


	def freeze(self):
		"""
		Freezes the canvas by sending an ATOM to bmovl2.
		"""
		if self.overlay and self.overlay().can_write():
			if self.atom == 0:
				self.overlay().atom()
			self.atom += 1


	def thaw(self):
		"""
		Thaw the canvas by sending ENDATOM to bmovl2.  When bmovl2 receives
		the last ENDATOM, all of the previous commands get applied 
		immediately.
		"""
		if self.overlay and self.overlay().can_write():
			self.atom -= 1
			if self.atom == 0:
				self.overlay().endatom()
				self.overlay().flush()

	def _update_begin(self, object = None):
		"""
		Called by a child 'object' when it wants to be updated.  If 'object'
		is None, it means update() was called on the canvas itself.
		"""

		# Bail if the overlay isn't writable.  Returning false in this
		# function will abort the update and the child will not ask the
		# canvas to paint it.
		if not self.overlay or not self.overlay().can_write():
			return False

		self.freeze()
	
		# At this point we can take care of any bmovl2 images that need to be
		# deleted.
		if len(self._deleted_ids) > 0 and self.overlay:
			for id in self._deleted_ids:
				self.overlay().delete(id)
			self._deleted_ids = []

		return True


	def _update_end(self, object = None):
		self.thaw()
		return True

	def _test_visibility(self, x, y, w, h, visible, alpha):
		if not visible or alpha == 0 or x > self.width or x + w < 0 or \
		   y > self.height or y + h < 0:
			return False
		return True

	def child_paint(self, child, force_children = False):
		"""
		Render the image on the bmovl2 overlay.  This is really where it all
		happens.
		"""
		if isinstance(child, CanvasContainer):
			children = child.children[:]
			children.reverse()
			dirty = child.dirty
			for o in children:
				# The child will be painted if it's dirty, but we can force the
				# paint if we're dirty, or of the child is container and has
				# dirty children.
				force = isinstance(o, CanvasContainer) and len(o.dirty_children)
				#print "CHILD", o, force_children, dirty, len(o.dirty_children), child.dirty_children
				o.update(force or dirty or force_children or o in child.dirty_children)
			child.dirty_children = []

			return

		# Get the child's attributes relative to the canvas.
		x, y, visible, alpha, zindex = child.get_relative_values(self)
		alpha = max(0, min(256, alpha))   # 0 <= alpha <= 256

		# Ultimately, the only objects with images get rendered, or specifically
		# CanvasImage or CanvasText objects. 
		if not isinstance(child, CanvasImage) or \
		   not self.overlay or not child.image:
			return

		if not hasattr(child, "_bmovl2_id"):
			# Create a bmovl2 id for this image.
			child._bmovl2_id = MPlayerCanvas._img_id_counter
			MPlayerCanvas._img_id_counter += 1
			
		id = child._bmovl2_id
		w, h = child.width, child.height
#		print "MPlayerCanvas paint:", id, x, y, visible, alpha, zindex, child, child.parent().get_abs_values(), child.is_frozen()

		# Don't bother updating if the image isn't visible on the overlay.
		if id not in self.overlay().blitted_ids:
			if not self._test_visibility(x, y, w, h, visible, alpha):
				return
			# If the MPlayer overlay doesn't know about this id and it's
			# visible, we reset all the cached bmovl2 attributes to ensure
			# they get synced.
			child.reset()
		elif id not in self._cached_values:
			child.reset()

		cval = self._cached_values[id]

		# If bmovl2 knows about the image and it isn't visible and it wasn't
		# visible before we don't bother either ...
		if not self._test_visibility(x, y, w, h, visible, alpha) and \
		   not self._test_visibility(cval["pos"][0], cval["pos"][1], w, h, cval["visible"], cval["alpha"]):
			return

		self.freeze()

		# Send the image to mplayer if it's visible and requires blitting.
		if visible and child.needs_blitting() and child.image:
			self.overlay().rawimg(id, child.image, 0)
			child.needs_blitting(False)
	
		# Now update the image's position, visibility, alpha, and z-index
		# attributes only if they have changed since last bmovl2 update.

		if (x, y) != cval["pos"]:
			self.overlay().move(id, x, y)
			cval["pos"] = (x, y)

		if visible != cval["visible"]:
			self.overlay().visible(id, visible)
			cval["visible"] = visible

		if alpha != cval["alpha"]:
			self.overlay().alpha(id, alpha)
			cval["alpha"] = alpha

		if zindex != cval["zindex"]:
			self.overlay().zindex(id, zindex)
			cval["zindex"] = zindex

		self.thaw()

		# All clean!
		child.dirty = False


	def child_deleted(self, child):
		"""
		Children notify the canvas when they've been deleted.  Here we just
		add the child id to a list so that we can delete them from bmovl2 on
		the next update.
		"""
		if hasattr(child, "_bmovl2_id"):
			self._deleted_ids.append(child._bmovl2_id)
			if child._bmovl2_id in self._cached_values:
				del self._cached_values[child._bmovl2_id]
			del child._bmovl2_id


	def child_reset(self, child):
		"""
		Children notify the canvas when they've been reset.  This canvas
		keeps track of childrens' attributes sent to bmovl2 so we only need
		to update the ones that have changed.
		"""
		if not hasattr(child, "_bmovl2_id"):
			return

		self._cached_values[child._bmovl2_id]= {
			"visible": True, "alpha": 255, "zindex": 0, "pos": (0,0) 
		}


	def rebuild(self):
		"""
		Rebuilds the canvas by dirtying all child objects, clearing all images
		from bmovl2, and redrawing from scratch.

		This is useful if MPlayer has restarted, or a new instance has started
		and we want to move the canvas from one instance to another.
		"""
		self.freeze()
		self.reset()
		self.overlay().delete_all()
		self.update(force = True)
		self.thaw()


# vim: ts=4
