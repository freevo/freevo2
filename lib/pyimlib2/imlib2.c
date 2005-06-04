/*
 * ----------------------------------------------------------------------------
 * Imlib2 wrapper for Python
 * ----------------------------------------------------------------------------
 * $Id$
 *
 * ----------------------------------------------------------------------------
 * Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
 *
 * First Edition: Jason Tackaberry <tack@sault.org>
 * Maintainer:    Dirk Meyer <dmeyer@tzi.de>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MER-
 * CHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
 * Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 * ----------------------------------------------------------------------------
 */

#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include "image.h"
#include "rawformats.h"
#include "font.h"
#include "thumbnail.h"
#include "config.h"

#ifdef USE_IMLIB2_DISPLAY
#include "display.h"
#endif

PyObject *imlib2_create(PyObject *self, PyObject *args)
{
    int w, h, num_bytes;
    unsigned char *bytes = NULL;
	char *from_format = "BGRA";
    Imlib_Image *image;
    Image_PyObject *o;

    if (!PyArg_ParseTuple(args, "(ii)|s#s", &w, &h, &bytes, &num_bytes, 
			  &from_format))
        return NULL;

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
    o->raw_data = NULL;
    return (PyObject *)o;
}


PyObject *imlib2_open(PyObject *self, PyObject *args)
{
    char *file;
    Imlib_Image *image;
    Image_PyObject *o;
    Imlib_Load_Error error_return;

    if (!PyArg_ParseTuple(args, "s", &file))
        return NULL;
        
    image = imlib_load_image_with_error_return(file, &error_return);
    if (!image) {
        PyErr_Format(PyExc_IOError, "Could not open %s: %d", file, 
		     error_return);
        if (error_return == IMLIB_LOAD_ERROR_NO_LOADER_FOR_FILE_FORMAT)
            PyErr_Format(PyExc_IOError, "no loader for file format");
        return NULL;
    }
    o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
    o->image = image;
    o->raw_data = NULL;
    return (PyObject *)o;
} 


PyObject *imlib2_add_font_path(PyObject *self, PyObject *args)
{
    char *font_path;

    if (!PyArg_ParseTuple(args, "s", &font_path))
        return NULL;

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
        return NULL;

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
        return NULL;
    return display_new(w, h);
#else
    PyErr_SetString(PyExc_ValueError, "X11 support missing");
    return NULL;
#endif
} 


PyMethodDef Imlib2_methods[] = {
    { "new_display", imlib2_new_display, METH_VARARGS }, 
    { "add_font_path", imlib2_add_font_path, METH_VARARGS }, 
    { "load_font", imlib2_load_font, METH_VARARGS }, 
    { "create", imlib2_create, METH_VARARGS }, 
    { "open", imlib2_open, METH_VARARGS }, 
    { "epeg_thumbnail", epeg_thumbnail, METH_VARARGS }, 
    { "png_thumbnail", png_thumbnail, METH_VARARGS }, 
    { "fail_thumbnail", fail_thumbnail, METH_VARARGS }, 
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
