import weakref

def make_weakref(object, callback = None):
	if type(object) == weakref.ReferenceType or not object:
		return object
	if callback:
		return weakref.ref(object, callback)
	else:
		return weakref.ref(object)

def check_weakref(object):
	if not object:
		return None
	if not object():
		return None

	return object

