#include <Python.h>
#include "display.h"
#include <Imlib2.h>
#include "image.h"

PyTypeObject Display_PyObject_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_Imlib2.Display",             /*tp_name*/
    sizeof(Display_PyObject),    /*tp_basicsize*/
    0,                         /*tp_itemsize*/
	(destructor)Display_PyObject__dealloc, /* tp_dealloc */
    0,                         /*tp_print*/
	(getattrfunc)Display_PyObject__getattr, /* tp_getattr */
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Imlib2 Display Object"           /* tp_doc */
};

void Display_PyObject__dealloc(Display_PyObject *self)
{
	PyMem_DEL(self);
}

void display_set_context(Display_PyObject *self)
{
	imlib_context_set_display(self->display);
	imlib_context_set_visual(self->visual);
	imlib_context_set_colormap(self->cmap);
	imlib_context_set_drawable(self->window);
}

PyObject *Display_PyObject__render(PyObject *self, PyObject *args)
{
    Image_PyObject *img;
	int dst_x = 0, dst_y = 0, src_x = 0, src_y = 0, 
	    w = -1, h = -1, img_w, img_h, dither = 1, blend = 0;
    if (!PyArg_ParseTuple(args, "O!|(ii)(ii)(ii)ii", &Image_PyObject_Type, &img, &dst_x, &dst_y, &src_x, &src_y, &w, &h, &dither, &blend))
        return NULL;

	imlib_context_set_image(((Image_PyObject *)img)->image);
	img_w = imlib_image_get_width();
	img_h = imlib_image_get_height();

	if (w == -1) w = img_w;
	if (h == -1) h = img_h;

	display_set_context((Display_PyObject *)self);

	imlib_context_set_dither(dither);
	imlib_context_set_blend(blend);
	if (src_x == 0 && src_y == 0 && w == img_w && h == img_h)
		imlib_render_image_on_drawable(dst_x, dst_y);
	else
		imlib_render_image_part_on_drawable_at_size(src_x, src_y, w, h, dst_x, dst_y, w, h);

	Py_INCREF(Py_None);
	return Py_None;
}

PyMethodDef Display_PyObject_methods[] = {
	{ "render", Display_PyObject__render, METH_VARARGS },
	{ NULL, NULL }
};

PyObject *Display_PyObject__getattr(Display_PyObject *self, char *name)
{
	return Py_FindMethod(Display_PyObject_methods, (PyObject *)self, name);
}


PyObject *display_new(int w, int h)
{
	Display_PyObject *o;
	int screen;
	XEvent ev;

	o = PyObject_NEW(Display_PyObject, &Display_PyObject_Type);
	o->display = XOpenDisplay(NULL);
	screen = DefaultScreen(o->display);

	o->visual = DefaultVisual(o->display, screen);
	o->depth = DefaultDepth(o->display, screen);
	o->cmap = DefaultColormap(o->display, screen);

	o->window = XCreateSimpleWindow(o->display, 
			DefaultRootWindow(o->display),
			0, 0, w, h, 0, 0, 0);

	XSelectInput(o->display, o->window, ButtonPressMask | ButtonReleaseMask | 
                PointerMotionMask | ExposureMask);
	XMapWindow(o->display, o->window);

	do {
		XNextEvent(o->display, &ev);
	} while (XPending(o->display));

	return (PyObject *)o;
}

// vim: ts=4
