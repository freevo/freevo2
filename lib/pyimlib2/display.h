#include <X11/Xlib.h>

#define Display_PyObject_Check(v) ((v)->ob_type == &Display_PyObject_Type)

typedef struct {
	PyObject_HEAD

	Display *display;
	Window   window;
	Visual  *visual;
	Colormap cmap;
	int      depth;

  PyObject * callback;
  
} Display_PyObject;

extern PyTypeObject Display_PyObject_Type;
void Display_PyObject__dealloc(Display_PyObject *);
PyObject *Display_PyObject__getattr(Display_PyObject *, char *);
int Display_PyObject__setattr( Display_PyObject *self, char *name,
			       PyObject * result );

PyObject *display_new(int w, int h);
