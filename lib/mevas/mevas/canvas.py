import types, time, math, Imlib2
from util import *
from container import *

class Canvas(CanvasContainer):
	"""
	Base class for all Canvases.  This class is pretty much "pure virtual" and
	defines a few new methods intended to be implemented by derived classes.
	"""
	def __init__(self, size):
		CanvasContainer.__init__(self)
		self.set_size(size)
		self.canvas = make_weakref(self)

	def freeze(self):
		pass

	def thaw(selF):
		pass	

	def child_deleted(self, child):
		pass

	def child_reset(self, child):
		pass

	def child_paint(self, child):
		pass

	def rebuild(self):
		pass



# vim: ts=4
