/* Imlib2 module for python.
   Written by Jason Tackaberry <tack@sault.org> and released under the LGPL.

   This is a quick hack.  It is not complete.
   See Imlib2.py for usage details.
*/

#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include "font.h"

PyTypeObject Font_PyObject_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_Imlib2.Font",             /*tp_name*/
    sizeof(Font_PyObject),    /*tp_basicsize*/
    0,                         /*tp_itemsize*/
	(destructor)Font_PyObject__dealloc, /* tp_dealloc */
    0,                         /*tp_print*/
	(getattrfunc)Font_PyObject__getattr, /* tp_getattr */
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
    "Imlib2 Font Object"           /* tp_doc */
};

void Font_PyObject__dealloc(Font_PyObject *self)
{
	imlib_context_set_font(self->font);
	imlib_free_font();
	PyMem_DEL(self);
}

PyObject *Font_PyObject__get_text_size(PyObject *self, PyObject *args)
{ 
	char *text;
	int w, h, advance_w, advance_h;

	if (!PyArg_ParseTuple(args, "s", &text))
		return NULL;

	imlib_context_set_font( ((Font_PyObject *)self)->font );
	imlib_get_text_size(text, &w, &h);
	imlib_get_text_advance(text, &advance_w, &advance_h);
	return Py_BuildValue("(llll)", w, h, advance_w, advance_h);
}

PyMethodDef Font_PyObject_methods[] = {
	{ "get_text_size", Font_PyObject__get_text_size, METH_VARARGS },
	{ NULL, NULL }
};

PyObject *Font_PyObject__getattr(Font_PyObject *self, char *name)
{
	imlib_context_set_font(self->font);
    if (!strcmp(name, "descent"))
        return Py_BuildValue("l", imlib_get_font_descent());
    else if (!strcmp(name, "ascent"))
        return Py_BuildValue("l", imlib_get_font_ascent());
    else if (!strcmp(name, "max_ascent"))
        return Py_BuildValue("l", imlib_get_maximum_font_ascent());
    else if (!strcmp(name, "max_descent"))
        return Py_BuildValue("l", imlib_get_maximum_font_descent());

	return Py_FindMethod(Font_PyObject_methods, (PyObject *)self, name);
}

// vim: ts=4
