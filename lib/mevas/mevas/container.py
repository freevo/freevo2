import types, time, math, random

from util import *
from canvasobject import *
from image import *
from text import *
import rect
import imagelib

class CanvasContainer(CanvasObject):
	"""
	Container objects can have children.  CanvasObjects already expect to have
	parents, and know how to render themselves relative to their parent.
	"""

	def __init__(self):
		self.children = []
		CanvasObject.__init__(self)

		self._backing_store = None
		self._backing_store_info = { "dirty-rects": [] }
		self._backing_store_dirty = True

	def _destroy(self):
		for child in self.children[:]:
			child._destroy()
		CanvasObject._destroy(self)


	def reset(self):
		CanvasObject.reset(self)
		for child in self.children:
			child.reset()
		self.dirty_children = []


	def clear(self):
		for child in self.children[:]:
			self.remove_child(child)

		self.children = []
		self.reset()

		if check_weakref(self.parent):
			self.queue_paint()


	def add_child(self, o):
		assert( o != self )
		assert( isinstance(o, CanvasObject) )

		if o in self.children:
			return

		# Child will queue_paint, making us dirty as well.
		o._reparent(self)
		self.children.append(o)


	def remove_child(self, o):
		if o not in self.children:
			return

		o._unparent()
		self.children.remove(o)

		# If this child has been rendered to the backing store, we add the
		# child's backing store rectangle to the list of dirty rectangles
		# to be updated on next call to _get_backing_store().
		if self._backing_store and hasattr(o, "_backing_store_info"):
			self._backing_store_dirty = True
			x, y = o._backing_store_info["pos"]
			w, h = o._backing_store_info["size"]
			self._backing_store_info["dirty-rects"] += [( (x, y), (w, h) )]
			#print "Child delete", o,  self._backing_store_info["dirty-rects"]
	
		self.queue_paint()		


	def draw_image(self, image, dst_pos = (0, 0), dst_size = (-1, -1), 
	               src_pos = (0, 0), src_size = (-1, -1), 
	               visible = True, alpha = 255, zindex = 0):
		"""
		Convenience function to add an image object to the container.
		"""

		o = CanvasImage(image)
		src_w, src_h = src_size
		dst_w, dst_h = dst_size
		if src_w == -1: src_w = o.get_width()
		if src_h == -1: src_h = o.get_height()
		if dst_w == -1: dst_w = src_w
		if dst_h == -1: dst_h = dst_h
		o.scale((dst_w, dst_h), src_pos, (src_w, src_h))
		o.set_all(dst_pos, visible, alpha, zindex)
		self.add_child(o)
		return o


	def draw_text(self, text, pos = (0, 0), font = "arial", size = 24, color = (255,255,255,255), 
	              visible = True, alpha = 255, zindex = 0):
		"""
		Convenience function to add an text object to the container.
		"""
		o = CanvasText(text, font, size, color)
		o.set_all(pos, visible, alpha, zindex)
		self.add_child(o)
		return o

	def draw_ellipse(self, pos, (a, b), color = (255,255,255,255), fill = True, visible = True, alpha = 255, zindex = 0):
		"""
		Convenience function to add an image object with an ellipse to the container.
		"""
		o = CanvasImage( (a * 2 + 2, b * 2 + 2) )
		o.draw_ellipse( (a+1, b+1), (a, b), color, fill )
		o.set_all(pos, visible, alpha, zindex)
		self.add_child(o)
		return o

	def draw_rectangle(self, pos, (w, h), color = (255,255,255,255), fill = True, visible = True, alpha = 255, zindex = 0):
		"""
		Convenience function to add an image object with a rectangle to the container.
		"""
		o = CanvasImage( (w, h) )
		o.draw_rectangle( (0, 0), (w, h), color, fill )
		o.set_all(pos, visible, alpha, zindex)
		self.add_child(o)
		return o


	def get_size(self):
		"""
		Compute the size of the container based on all of its children.
		"""
		left = top = bottom = right = 0
		for child in self.children:
			child_w, child_h = child.get_size()
			child_x, child_y= child.get_pos()

			left = min(left, child_x)
			right = max(right, child_x + child_w)
			top = min(top, child_y)
			bottom = max(bottom, child_y + child_h)
	
		return right-left, bottom-top	

			
	def queue_paint(self, child = None):
		"""
		Mark this object as dirty and flag it for painting on the next
		update().  If child is not None, it means a child object is informing
		us that it needs to be redrawn.  We must pass this message through
		the tree to the root (i.e. the canvas).

		Containers are considered dirty if any of their children are dirty or
		if a property (position, alpha, zindex, visibility) has changed.  It's
		up to the canvas child_paint() method to figure out what to do, since that
		will depend on the backend.
		"""
		self.dirty = True
		self._backing_store_dirty = True

		if child and child not in self.dirty_children:
			self.dirty_children.append(child)

		if check_weakref(self.parent):
			self.parent().queue_paint(self)


	def unqueue_paint(self, child = None):
		"""
		No longer require to be painted on the next call to update().  As
		with queue_paint(), if child is not None, we pass this up the
		object hierarchy to the canvas.
		"""

		if child in self.dirty_children:
			self.dirty_children.remove(child)

		# A child can make us dirty (by saying it is dirty), but only the
		# container can clear the dirty flag.
		if not child and len(self.dirty_children) == 0:
			self.dirty = False

		if  check_weakref(self.parent):
			self.parent().unqueue_paint(self)


	def _reparent(self, parent):
		CanvasObject._reparent(self, parent)
		# Reparent children to update their canvas attribute.
		for child in self.children:
			child._reparent(self)


	def _get_child_min_pos(self, recursed = False):
		if recursed:
			left, top = self.get_pos()
		else:
			left = top = 0
		for child in self.children:
			if isinstance(child, CanvasContainer):
				child_x, child_y = child._get_child_min_pos(True)
			else:
				child_x, child_y = child.get_pos()
			left = min(left, left + child_x)
			top = min(top, top + child_y)

		return left, top

	def render_to_image(self):
		img = self._get_backing_store()[0]
		if self.alpha != 255:
			blended_img = imagelib.new( img.size )
			blended_img.blend(img, alpha = self.alpha)
			img = blended_img
		return CanvasImage(img)

	def _get_backing_store(self, update = False, use_cached = False, 
	                       update_object = None, preserve_alpha = True,
	                       clip = False):
		"""
		Render the container and all of its children to an image.  This image
		is cached as the container's backing store and subsequent calls to
		_get_backing_store() will only update those regions of the backing
		store that require it.

		If 'update_object' is not None, it specifies an object somewhere in
		the container's hierarchy that is to be updated on the backing store.
		It may be that all objects in the container are dirty, but if we only
		want one object to be updated on the backing store, we can specify it
		in update_object.  This is useful for BitmapCanvas, as it translates
		child.update() to self._get_backing_store(update_object = child).

		If 'update' is True, unqueue_paint() is called on dirty children.
		This is intended specifically for canvas implementations that rely
		on _get_backing_store(), like BitmapCanvas.

		If 'use_cached' is True and a backing store exists for this container
		(that is, _get_backing_store() has been called before), the old image
		will be returned; dirty children will not be updated.

		If 'preserve_alpha' is True, the canvas backing store image has the
		appropriate alpha channel (relative to its children).  If it is False,
		the backing store image's pixels are fully opaque and the alpha is
		applied is if the backing store's backround is black.  This is useful
		for BitmapCanvas-based canvases that will be blitting to a screen.

		This function returns a tuple whose first item is an imagelib.Image
		representing the rendered container, and whose second item is a list
		of rectangles that have been updated since the last call to
		_get_backing_store().  This is useful for subclasses of BitmapCanvas
		that want to blit only changed regions to the display.  Rectangles
		are in the form ( (left, top), (width, height) ).
		"""

		# WARNING: This code is scary. :)
		#
		#
		# Part of the reason the code below is sticky is that is solves a
		# a problem with sticky requirements, particularly the fact that
		# canvas objects can have negative coordinates, so coords must
		# be continually translated.  
		
		# Another requirement is that if 'update_object' is specified, 
		# all parent or sibling objects to 'update_object' shouldn't be 
		# touched.  But because we may need blit an object that isn't to 
		# be updated (if it is underneath an image that _is_ to be updated, 
		# for instance), we need to know its position.  If the position has
		# changed, we need to use the old position, so this means we must
		# maintain a cache of old values.  We use the _backing_store_info 
		# dict for this.
		#
		# HOW THIS FUNCTION WORKS
		# =======================
		#
		# The work is divided into three steps:
		#
		#    1. Update the backing stores of all dirty children and obtain a
		#       list of rectangles that are considered dirty.  (Rectangles
		#       of all dirty children are updated if 'update_object' is None.)
		#    2. Clear the dirty rectangles in the backing store.
		#    3. For each child in the container, create a list of rectangles
		#       that intersect with all dirty rectangles.  Then blend the
		#       intersection rectangle of that child to the backing store.
		# 
		# It's a bit more complicated than that (read the code below for
		# the real truth :)), but that's the general approach.
		#

		width, height = self.get_size()
		left, top = self.get_pos()
		if 0 in (width, height):
			return None, []

		t0=time.time()
		#print "*** Begin _get_backing_store", self, update_object, self._backing_store_dirty
		if not self._backing_store_dirty or (use_cached and self._backing_store):
			return self._backing_store, []
		# Offset of container image relative to container.  Because container
		# children can have negative positions, (0,0) of the container may
		# not be (0,0) of the backing store image.
		offset_x, offset_y = self._get_child_min_pos()
		
		# List of dirty rectangles relative to the container.  This means
		# a rect of ((0, 0), (100, 100)) may not map directly to the backing
		# store if offset_x or offset_y are non-zero.
		dirty_rects = []
		if self._backing_store_info["dirty-rects"]:
			dirty_rects += self._backing_store_info["dirty-rects"]
			self._backing_store_info["dirty-rects"] = []

		# If the alpha of the container has changed then we need to
		# invalidate the whole thing.
		if "alpha" not in self._backing_store_info or \
		   self._backing_store_info["alpha"] != self.alpha:
			self._backing_store_info["alpha"] = self.alpha
			# Optimization: if alpha has changed but none of the children
			# are dirty, and we already have a backing store, we just return
			# the backing store as is.  It's up to the caller to blend us at
			# our alpha.
			dirty_rects += ( (offset_x, offset_y), (width, height) ),
			if len(self.dirty_children) == 0 and self._backing_store:
				if update_object == self and update:
					self.unqueue_paint()
				return self._backing_store, dirty_rects

		if "pos" not in self._backing_store_info:
			# First time _get_backing_store() is called on this container, so we
			# initialize pos with the present position.
			self._backing_store_info["pos"] = self.get_pos()

		# 'uo' is used in the children loop below.  If update_object is this
		# container (self), then all children must be updated too, so as far
		# as chlidren are concerned, update_object is None.
		if self == update_object: 
			uo = None
		else: 
			uo = update_object


		# STEP 1
		# ======
		# Iterate through all children and update the backing stories of all
		# dirty children (or rather, those dirty children according to 'ua'),
		# and collect a list of dirty rectangles relative to this container.
		# (Note rectangles are relative to the container, not the backing
		# store, so negative coordinates are ok; they will be translated
		# later).
		t1 = time.time()
		# Sort children in order of their z-index.
		self.children.sort(lambda a, b: cmp(a.zindex, b.zindex))

		for child in self.children:
			if not child.dirty:
				continue

			child_x, child_y = child.get_pos()
			child_w, child_h = child.get_size()
			child_offset_x = child_offset_y = 0

			# If update_object isn't this child, then we use the child's old
			# backing store position (if one exists).
			if uo and uo != child and hasattr(child, "_backing_store_info") and "pos" in child._backing_store_info:
				child_x, child_y = child._backing_store_info["pos"]

			# If child is a container, we need to recurse.
			if isinstance(child, CanvasContainer):
				img, child_dirty_rects = child._get_backing_store(update, update_object = uo)
				# For each of the dirty rectangles returned by the above call,
				# translate them so they are relative to this container,
				# rather than the child container.
				dirty_rects += rect.offset_list(child_dirty_rects, (child_x, child_y))
				# Get the container's min coordinates; they are used below.
				child_offset_x, child_offset_y = child._get_child_min_pos()

			if not hasattr(child, "_backing_store_info"):
				# First time for this non-container child.
				child._backing_store_info = {}

			# If this child is not the requested update object, continue on.
			# Note that we traverse child containers because the update_object
			# may be one of our grand children.
			if uo and uo != child:
				continue	
		
			# 'bsi' for convenience.
			bsi = child._backing_store_info

			# If the child is invisible (either hidden or alpha of 0) then 
			# we don't bother with this child.
			if ("visible" in bsi and not child.visible and not bsi["visible"]) or \
			   ("alpha" in bsi and child.alpha == 0 and bsi["alpha"] == 0):
				continue

			# If the child has either changed positions or changed sizes (or
			# both), we add the child's old rectangle and the new one to the
			# list of dirty rectangles.
			if "size" in bsi and (bsi["pos"] != (child_x, child_y) or bsi["size"] != (child_w, child_h)):
				# Positions get offsetted by child_offset_x/y which are both 0
				# for non-containers, but may be non-zero for containers.  We
				# need to translate child containers with children with
				# negative coordinates.

				if bsi["pos"] != (child_x, child_y): print "OBJECT MOVE", child
				if bsi["size"] != (child_w, child_h): print "OBJECT RESIZE", child
				# Old rectangle.
				dirty_rects += ( (bsi["pos"][0] + child_offset_x, bsi["pos"][1] + child_offset_y), bsi["size"]),
				# New rectangle.
				dirty_rects += ( (child_x + child_offset_x, child_y + child_offset_y), (child_w, child_h) ),
				print dirty_rects

			# If visibility or zindex has changed, entire child region gets invalidated.
			elif ("visible" in bsi and bsi["visible"] != child.visible) or \
			     ("z-index" in bsi and bsi["z-index"] != child.zindex):
				dirty_rects += ( (child_x + child_offset_x, child_y + child_offset_y), (child_w, child_h) ),

			# If we've gotten this far and the child is an image, then we
			# assume the whole image needs blitting.
			elif isinstance(child, CanvasImage):
				dirty_rects += ( (child_x, child_y), (child_w, child_h) ),

			# Remember the current values.
			bsi["pos"] = child_x, child_y
			bsi["size"] = child_w, child_h
			bsi["alpha"] = child.alpha
			bsi["z-index"] = child.zindex
			bsi["visible"] = child.visible

			if update:
				child.unqueue_paint()
				if isinstance(child, CanvasImage):
					child.needs_blitting(False)


			# If we've found the child whose updated was requested, there's
			# no need to loop any further.
			if uo == child:
				break

			# END CHILDREN LOOP

		# Unqueue paint for this container if necesary.
		if update_object == self and update:
			self.unqueue_paint()

		# So now we have a list of dirty rectangles.   We optimize the
		# list for rendering by removing redundant rectangles (if A is fully
		# contained in B, remove A), and removing interections.
		dirty_rects = rect.optimize_for_rendering(dirty_rects)

		# Broken code.
		#if self.has_canvas():
		#	print "PRE CLIP", dirty_rects
		#	canvas_width, canvas_height = self.get_canvas().get_size()
		#	dirty_rects = rect.offset_list(dirty_rects, (left, top))
		#	dirty_rects = rect.clip_list( dirty_rects, ((0, 0), (canvas_width, canvas_height)) )
		#	dirty_rects = rect.offset_list(dirty_rects, (-left, -top))
		#	print "POST CLIP", left, top, dirty_rects


		# STEP 2
		# ======
		# Clear all dirty rectangles on the backing store.  "Clear" in this
		# context means setting those pixels to (0, 0, 0, 0).

		t2 = time.time()
		if not self._backing_store:
			# First time calling _get_backing_store() on this container or it
			# has resized, so create backing store image.
			self._backing_store = imagelib.new( (width, height) )
			if not preserve_alpha:
				self._backing_store.draw_rectangle((0, 0), (width, height), (0, 0, 0, 255), fill=True)
		else:
			# If the container has resized, we create a backing store of the
			# new size and copy the old contents over.  Dirty regions are 
			# still valid, and they are relative to the container's new 
			# dimensions. 

			# FIXME: if clip == True, limit backing store image size to 
			# canvas size.
			if self._backing_store and (width, height) != self._backing_store.size:
				bs_width, bs_height = self._backing_store.size
				old_offset_x, old_offset_y = self._backing_store_info["offset"]
				move_x = old_offset_x - offset_x
				move_y = old_offset_y - offset_y

				# Grow the backing store if needed.
				if width > bs_width or height > bs_height:
					img = imagelib.new( (width, height) )
					img.blend(self._backing_store, (move_x, move_y), alpha = 256)
					self._backing_store = img
				else:
					# We're not growing the backing store, but we still need
					# to shift its contents.  So we do that, and then dirty
					# the edges that are stale.
					self._backing_store.copy_rect( (0, 0), self._backing_store.size, (move_x, move_y))
					if move_x < 0:
						dirty_rects += [ ((width + move_x, 0), (bs_width-width, bs_height)) ]
					if move_y < 0:
						dirty_rects += [ ((0, height + move_y), (bs_width, bs_height-height)) ]

			dirty_rects = rect.remove_intersections(dirty_rects)
			for r in dirty_rects:
				# Clip rect to backing store image boundary.
				r = rect.clip(r, ((offset_x, offset_y), self._backing_store.size) )
				if preserve_alpha:
					self._backing_store.clear( (r[0][0] - offset_x, r[0][1] - offset_y), r[1] )
				else:
					self._backing_store.draw_rectangle((r[0][0] - offset_x, r[0][1] - offset_y), r[1] , (0, 0, 0, 255), fill=True)

		self._backing_store_info["offset"] = (offset_x, offset_y)
		self._backing_store_info["size"] = (width, height)

		#dirty_rects += [((offset_x, offset_y), (width, height))]
		# STEP 3
		# ======
		# Render the intersections between all children and all dirty
		# rectangles.  Children are already sorted in order of z-index.
		t3 = time.time()
		for child in self.children:
			if not child.visible or child.alpha <= 0 or not dirty_rects:
				continue

			if isinstance(child, CanvasContainer):
				child_offset_x, child_offset_y = child._get_child_min_pos()
			else:
				child_offset_x = child_offset_y = 0

			# Use the backing store position if it exists.
			if hasattr(child, "_backing_store_info") and "pos" in child._backing_store_info:
				child_x, child_y = child._backing_store_info["pos"]
			else:
				child_x, child_y = child.get_pos()

			# Get all regions this child intersects with.
			intersects = []
			for r in dirty_rects:
				intersect = rect.intersect( ((child_x + child_offset_x, child_y + child_offset_y), child.get_size() ), r)
				if intersect != rect.empty:
					intersects.append(intersect)

			# We must remove all intersections from the list because drawing
			# over a rectangle multiple times with an image whose opacity is
			# less than 255 will cause incorrect results.  (Intersections are
			# collapsed into unions.)  remove_intersections() could be more
			# intelligent: see rect.py for details.
			draw_regions = rect.remove_intersections(intersects)
			if len(draw_regions) == 0:
				continue

			# FIXME: image objects don't have backing stores; we just use the
			# underlying image directly.  This is broken because it may happen
			# that update_object is a sibling or "uncle" to an image that has
			# been modified, we should blit the old image before the update, not
			# the new one.  IN PRACTICE this likely isn't a problem, however it
			# is not correct according to how the canvas should behave.
			if isinstance(child, CanvasContainer):
				img = child._get_backing_store(use_cached = True)[0]
			else:
				img = child.image
			#scale_x=scale_y=1
			for r in draw_regions:
				rx, ry = r[0]
				dst_x, dst_y = rx - offset_x, ry - offset_y
				src_x, src_y = rx - child_offset_x - child_x, ry - child_offset_y - child_y
				src_w, src_h = dst_w, dst_h = r[1]
				# Draw random colored rectangles over updated regions: useful for debugging.
				#c = map(lambda x: int(random.random()*127)+127, range(3))
				#self._backing_store.draw_rectangle( ( dst_x, dst_y ), r[1], c+[200], fill=True)
				self._backing_store.blend(img, (dst_x, dst_y), (dst_w, dst_h),
				    (src_x, src_y), (src_w, src_h), alpha = child.alpha, merge_alpha = preserve_alpha)
				#print "PAINT", child, (dst_x, dst_y), (dst_w, dst_h), (src_x, src_y), (src_w, src_h), child.alpha

		if not update_object or update_object == self:
			self._backing_store_dirty = False
		t4 = time.time()
		#print "*!* Return from _get_backing_store", self, " - (0 = %.04f, 1 = %.04f, 2 = %.04f, 3 = %.04f, total = %.04f" % (t1-t0, t2-t1, t3-t2, t4-t3, t4-t0)
		return self._backing_store, dirty_rects

				

	def collapse_to_image(self, parent = None):
		"""
		Render all of the child objects of the container to a single image
		and replace itself with the resulting image.  This may be desired for
		performance reasons, but of course once you collapse the container to
		an image you can no longer manipulate the individual objects of the
		container.
		"""
		if parent == None:
			parent = self.parent

		if parent == None:
			print "*** WARNING: CanvasContainer.collapse_to_image() called with no parent."
			return None

		img = self.render_to_image()
		img.move(self.get_pos())
		img.set_zindex(self.get_zindex())
		index = parent().children.index(self)
		parent().remove_child(self)
		parent().add_child(img)
		self.clear()
		return img

# vim: ts=4
