/* Imlib2 module for python.
   Written by Jason Tackaberry <tack@sault.org> and released under the LGPL.

   This is a quick hack.  It is not complete.
   See Imlib2.py for usage details.
*/

#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include "image.h"
#include "rawformats.h"
#include "font.h"
#include "config.h"

#ifdef USE_IMLIB2_DISPLAY
#include "display.h"
#endif

PyObject *imlib2_create(PyObject *self, PyObject *args)
{
	int w, h, num_bytes;
	unsigned char *bytes = NULL, *from_format = "BGRA";
	Imlib_Image *image;
	Image_PyObject *o;

	if (!PyArg_ParseTuple(args, "(ii)|s#s", &w, &h, &bytes, &num_bytes, &from_format))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;

	if (bytes) {
		if (!strcmp(from_format, "BGRA"))
			image = imlib_create_image_using_copied_data(w, h, (void *)bytes);
		else {
			bytes = convert_raw_rgba_bytes(from_format, "BGRA", bytes, 
						       NULL, w, h);
			image = imlib_create_image_using_copied_data(w, h, (void *)bytes);
			free(bytes);
		}
		imlib_context_set_image(image);
		if (strlen(from_format) == 4)
			imlib_image_set_has_alpha(1);
	} else {
		image = imlib_create_image(w, h);
		imlib_context_set_image(image);
		imlib_image_set_has_alpha(1);
		imlib_image_clear_color(0, 0, 0, 0);
	}
	if (!image) {
		PyErr_Format(PyExc_RuntimeError, "Failed to create image");
		return NULL;
	}

	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;

}

PyObject *imlib2_open(PyObject *self, PyObject *args)
{
	char *file;
	Imlib_Image *image;
	Image_PyObject *o;
	Imlib_Load_Error error_return;

	if (!PyArg_ParseTuple(args, "s", &file))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;
		
	image = imlib_load_image_with_error_return(file, &error_return);
	if (!image) {
		PyErr_Format(PyExc_IOError, "Could not open %s: %d", file, error_return);
		if (error_return == IMLIB_LOAD_ERROR_NO_LOADER_FOR_FILE_FORMAT)
		    PyErr_Format(PyExc_IOError, "no loader for file format");
		return NULL;
	}
	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;
} 

PyObject *imlib2_add_font_path(PyObject *self, PyObject *args)
{
	char *font_path;

	if (!PyArg_ParseTuple(args, "s", &font_path))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;

	imlib_add_path_to_font_path(font_path);
	Py_INCREF(Py_None);
	return Py_None;
} 
PyObject *imlib2_load_font(PyObject *self, PyObject *args)
{
	char *font_spec;
	Imlib_Font *font;
	Font_PyObject *o;

	if (!PyArg_ParseTuple(args, "s", &font_spec))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;

	font = imlib_load_font(font_spec);
	if (!font) {
		PyErr_Format(PyExc_IOError, "Couldn't open font: %s", font_spec);
		return NULL;
	}
	o = PyObject_NEW(Font_PyObject, &Font_PyObject_Type);
	o->font = font;
	return (PyObject *)o;
} 

PyObject *imlib2_new_display(PyObject *self, PyObject *args)
{
#ifdef USE_IMLIB2_DISPLAY
	int w, h;

	if (!PyArg_ParseTuple(args, "ii", &w, &h))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;

	return display_new(w, h);
#else
	return PyErr_SetString(PyExc_ValueError, "X11 support missing"), (PyObject*)NULL;
#endif

} 
PyObject *imlib2__shm_unlink(PyObject *self, PyObject *args)
{
	char *name;

	if (!PyArg_ParseTuple(args, "s", &name))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;

	shm_unlink(name);
	Py_INCREF(Py_None);
	return Py_None;
} 

PyObject *imlib2__free_buffer(PyObject *self, PyObject *args)
{
	void *buffer;

	if (!PyArg_ParseTuple(args, "l", &buffer))
                return PyErr_SetString(PyExc_AttributeError, ""), (PyObject*)NULL;
	
	if (buffer)
		free(buffer);
	
	Py_INCREF(Py_None);
	return Py_None;
} 

PyMethodDef Imlib2_methods[] = {
    { "new_display", imlib2_new_display, METH_VARARGS }, 
    { "add_font_path", imlib2_add_font_path, METH_VARARGS }, 
    { "load_font", imlib2_load_font, METH_VARARGS }, 
    { "create", imlib2_create, METH_VARARGS }, 
    { "open", imlib2_open, METH_VARARGS }, 
    { "_shm_unlink", imlib2__shm_unlink, METH_VARARGS }, 
    { "_free_buffer", imlib2__free_buffer, METH_VARARGS }, 
    { NULL }
};

void init_Imlib2()
{
	PyObject *m;

	init_rgb2yuv_tables();
	m = Py_InitModule("_Imlib2", Imlib2_methods);
	Image_PyObject_Type.tp_new = PyType_GenericNew;
	if (PyType_Ready(&Image_PyObject_Type) < 0)
	    return;
	PyModule_AddObject(m, "Image", (PyObject *)&Image_PyObject_Type);
	imlib_set_cache_size(1024*1024*4);
	imlib_set_font_cache_size(1024*1024*2);
}

// vim: ts=4
