import types, time, math
from util import *

class CanvasObject(object):
	"""
	Base class for all canvas objects.
	"""

	def __init__(self):
		# Initialize object attributes to defaults.
		self.x, self.y = 0, 0
		self.visible, self.alpha, self.zindex = True, 255, 0
		self._frozen = 0
		self.set_size( (None, None) )

		# Orphan by default.
		self.parent = self.canvas = None

		# Reset the object's status on the display (i.e. make it dirty).
		self.reset()


	def __del__(self):
		self._unparent()

	def freeze(self):
		self._frozen += 1

	def thaw(self):
		if self._frozen > 0:
			self._frozen -= 1
			if self._frozen == 0:
				self.update()

	def is_frozen(self):
		o = self
		while o:
			if o._frozen != 0:
				return True
			o = o.get_parent()
		return False

	def _destroy(self):
		"""
		Tells the canvas to delete the object.  This
		gets called by the object's destructor (indirectly through unparent()), 
		but if we need the image to disappear from the canvas right away, we 
		can explicitly call _destroy()
		"""
		if self.has_canvas():
			self.canvas().child_deleted(self)


	def reset(self):
		"""
		Resets the object's display status.  This doesn't change the object's
		attributes themselves, but rather makes the canvas think they are 
		dirty, so on the next update, the object will get refreshed if 
		necessary.
		"""
		if self.has_canvas():
			self.canvas().child_reset(self)
		self.dirty = True
		self._contents_dirty = True
		self._properties_dirty = True


	def _unparent(self, destroy = True):
		"""
		Makes the object an orphan.  Tells the parent to disown it and then
		unqueues any pending paint requests.
		"""

		# Without a parent, we have no root canvas, so we must ask the canvas
		# to destroy us.  If destroy is False, it probably means we're being
		# reparented within the same canvas, so there's no need to destroy.
		if destroy:
			self._destroy()
#		if check_weakref(self.parent) and self in self.parent().children:
#			self.parent().children.remove(self)
		self.unqueue_paint()
		self.canvas = self.parent = None


	def unparent(self):
		parent = self.get_parent()
		if parent:
			parent.remove_child(self)

	def _reparent(self, parent):
		if not isinstance(parent, CanvasContainer):
			print "*** WARNING: Trying to reparent to a non-container (%s)" % repr(parent)
			return

		dirty = self.dirty

		# Unparent first from any existing parent before reparenting.
		if check_weakref(self.parent) and self.parent() != parent:
			# Unparent, but no need to destroy if we're reparenting within
			# the same canvas.
			if parent.canvas == self.canvas:
				self._unparent(destroy = False)
			else:
				self._unparent(destroy = True)

		self.parent = self.canvas = None
		if parent:
			self.canvas = self.parent = make_weakref(parent, lambda x: self._unparent())
			if check_weakref(parent.canvas):
				self.canvas = parent.canvas

			# If we're dirty, we need to tell our new parent that we need
			# drawing.
			if dirty:
				self.queue_paint()



	def set_size(self, (w, h)):
		self.width, self.height = w, h

	def get_size(self):
		return self.width, self.height

	def get_width(self):
		return self.get_size()[0]

	def get_height(self):
		return self.get_size()[1]


	def has_canvas(self):
		"""
		Determine if the object is part of a canvas yet.  Objects can
		have parents (containers, for example), but ultimately they must
		be added (either directly, or indirectly through a container) to a
		canvas.
		"""
		if check_weakref(self.canvas):
			if isinstance(self.canvas(), Canvas):
				return True
		return False


	def get_canvas(self):
		if not self.has_canvas():
			return None

		if check_weakref(self.canvas):
			return self.canvas()

	def get_parent(self):
		if check_weakref(self.parent):
			return self.parent()

	def _update_begin(self, object = None):
		"""
		Called when object begins an update.  Its main purpose is to notify
		the canvas about intent to update.  If this function returns False,
		the update must abort.  (It means the canvas is not in a state where
		it can be drawn to.)

		This method is intended to be derived.
		"""
		if self.has_canvas():
			return self.canvas()._update_begin(self)
		return False


	def _update_end(self, object = None):
		if self.has_canvas():
			return self.canvas()._update_end(self)
		return False


	def update(self, force = False):
		"""
		Cause the object to be updated (rendered) on the canvas.
		"""

		# If we're not dirty, then we don't need to paint.  The caller can
		# force the paint, which may be necessary for example if the object's
		# container has been changed (moved, new alpha, etc.) and we must be
		# repainted to reflect this change.
		#if self.is_frozen():
		#	print "ABORTING DRAW due to FROZEN", self, self._frozen
		if not force and not self.dirty or self.is_frozen():
			return

		# Off we go ...
		if not self._update_begin():
			return False

		if check_weakref(self.canvas):
			self.canvas().child_paint(self, force)
		self.unqueue_paint()
		return self._update_end()


	def get_relative_values(self, container = None):
		"""
		Returns the object's coordinates, alpha, and zindex relative
		to the specified ancestor container.  If container is none, it 
		defaults to the top-most container (i.e. the canvas).
		"""
		x, y, zindex = self.x, self.y, self.zindex
		visible, alpha = self.visible, self.alpha
		parent = self.parent
		while check_weakref(parent):
			x, y = parent().x + x, parent().y + y
			zindex += parent().zindex
			visible = visible and parent().visible

			# Apply parent alpha
			temp = (alpha * parent().alpha) + 0x80
			alpha = (temp + (temp >> 8)) >> 8
			if container and parent() == container:
				break
			parent = parent().parent
		
		return x, y, visible, alpha, zindex


	def queue_paint(self):
		"""
		Mark this object as dirty and flag it for painting on the next
		update(). 
		"""
		self.dirty = True

		# Inform the parent that we need repainting should it get updated.
		if check_weakref(self.parent):
			self.parent().queue_paint(self)


	def unqueue_paint(self):
		"""
		No longer require to be painted on the next call to update().
		"""
		if not self.dirty:
			return

		self.dirty = False

		# Inform the parent that we no longer need repainting.
		if check_weakref(self.parent):
			self.parent().unqueue_paint(self)


	def move(self, (x, y)):
		self.set_pos( (x, y) )


	def set_pos(self, (x, y)):
		if x == self.x and y == self.y:
			return

		self.x, self.y = int(x), int(y)
		self.queue_paint()


	def get_pos(self):
		return self.x, self.y


	def hide(self):
		self.set_visible(False)


	def show(self):
		self.set_visible(True)


	def toggle_visible(self):
		self.set_visible(1 - self.visible)


	def set_visible(self, visible):
		if visible == self.visible:
			return
		self.visible = visible
		self.queue_paint()

	def get_visible(self):
		return self.visible
		
	def set_alpha(self, alpha):
		"""
		Set the overall alpha for the whole image.  0 is fully transparent, 
		and 255 is fully opaque.  256 is a special value that causes the 
		canvas to ignore the image's alpha channel.
		"""
		# Require 0 <= alpha <= 256
		alpha = min(256, max(0, alpha))
		if alpha == self.alpha:
			return
		self.alpha = alpha
		self.queue_paint()

	def get_alpha(self):
		return self.alpha

	def set_zindex(self, zindex):
		"""
		Set the canvas z-index (or height) of the image.  Lower values mean
		lower on the stack.  That is, images with lower values get drawn first.
		"""
		if zindex == self.zindex:
			return
		self.zindex = zindex
		self.queue_paint()

	def get_zindex(self):
		return self.zindex


	def set_all(self, pos, visibility, alpha, zindex):
		self.move(pos)
		self.set_visible(visibility)
		self.set_alpha(alpha)
		self.set_zindex(zindex)

# Import down here to prevent recursive import problems.
from canvas import *
from container import *

# vim: ts=4
