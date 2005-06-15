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

#define HAVE_MMX 1
#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include "image.h"
#include "rawformats.h"
#include "font.h"

#include <sys/mman.h>
#include <fcntl.h>
#include "config.h"

int Image_PyObject_Buffer__get_read_buffer(PyObject *, int, void **);
int Image_PyObject_Buffer__get_readwrite_buffer(PyObject *, int, void **);
int Image_PyObject_Buffer__get_seg_count(PyObject *, int *);

PyBufferProcs buffer_procs = {
    Image_PyObject_Buffer__get_read_buffer, 
    Image_PyObject_Buffer__get_readwrite_buffer, 
    Image_PyObject_Buffer__get_seg_count, 
    NULL
};

PyTypeObject Image_PyObject_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_Imlib2.Image",           /*tp_name*/
    sizeof(Image_PyObject),    /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Image_PyObject__dealloc, /* tp_dealloc */
    0,                         /*tp_print*/
    (getattrfunc)Image_PyObject__getattr, /* tp_getattr */
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
    &buffer_procs,             /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "Imlib2 Image Object"      /* tp_doc */
};

// Exported _C_API function
Imlib_Image *imlib_image_from_pyobject(Image_PyObject *pyimg)
{
    return pyimg->image;
}

int Image_PyObject_Buffer__get_read_buffer(PyObject *self, int segment, void **ptr)
{
    imlib_context_set_image(((Image_PyObject *)self)->image);
    if (ptr)
        *ptr = (void *)imlib_image_get_data_for_reading_only();
    return imlib_image_get_width() * imlib_image_get_height() * 4;
}

int Image_PyObject_Buffer__get_readwrite_buffer(PyObject *self, int segment, void **ptr)
{
    Image_PyObject *o = (Image_PyObject *)self;
    imlib_context_set_image(o->image);
    if (segment > 0) {
        PyErr_Format(PyExc_SystemError, "Invalid segment for read/write buffer.");
        return -1;
    }
    if (ptr) {
        if (o->raw_data)
            *ptr = o->raw_data;
        else 
            *ptr = o->raw_data = (void *)imlib_image_get_data();
    }
    return imlib_image_get_width() * imlib_image_get_height() * 4;
}

int Image_PyObject_Buffer__get_seg_count(PyObject *self, int *lenp)
{
    if (lenp) {
        imlib_context_set_image(((Image_PyObject *)self)->image);
        *lenp = imlib_image_get_width() * imlib_image_get_height() * 4;
    }
    return 1;
}

Image_PyObject *_new_image_pyobject(Imlib_Image *image)
{
    Image_PyObject *o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
    o->image = image;
    o->raw_data = NULL;
    return o;
}

void Image_PyObject__dealloc(Image_PyObject *self)
{
    imlib_context_set_image(self->image);
    imlib_free_image();
    PyMem_DEL(self);
}


PyObject *Image_PyObject__clear(PyObject *self, PyObject *args)
{
    int x, y, w, h, max_w, max_h, cur_y;
    unsigned char *data;


    if (!PyArg_ParseTuple(args, "iiii", &x, &y, &w, &h))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    data = (unsigned char *)imlib_image_get_data();
    max_w = imlib_image_get_width();
    max_h = imlib_image_get_height();
    if (x < 0) x = 0;
    if (y < 0) y = 0;
    if (x+w > max_w) w = max_w-x;
    if (y+h > max_h) h = max_h-y;

    /* FIXME: make it faster (optimize for slices; memcpy might be faster) */
    for (cur_y = y; cur_y < y + h; cur_y++)
        memset(&data[cur_y*max_w*4+(x*4)], 0, 4*w);
    imlib_image_put_back_data((DATA32 *)data);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__scale(PyObject *self, PyObject *args)
{
    int x, y, dst_w, dst_h, src_w, src_h;
    Imlib_Image *image;
    Image_PyObject *o;

    if (!PyArg_ParseTuple(args, "iiiiii", &x, &y, &src_w, &src_h, &dst_w,
              &dst_h))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    image = imlib_create_cropped_scaled_image(x, y, src_w, src_h,
                          dst_w, dst_h);
    if (!image) {
        PyErr_Format(PyExc_RuntimeError, "Failed scaling image (%d, %d)",
             dst_w, dst_h);
        return NULL;
    }

    o = _new_image_pyobject(image);
    return (PyObject *)o;
}


PyObject *Image_PyObject__rotate(PyObject *self, PyObject *args)
{
    Imlib_Image *image;
    Image_PyObject *o;
    double angle;

    if (!PyArg_ParseTuple(args, "d", &angle))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);

    image = imlib_create_rotated_image(angle);
    if (!image) {
        PyErr_Format(PyExc_RuntimeError, "Failed rotating image (%f) degrees",
             angle);
        return NULL;
    }

    o = _new_image_pyobject(image);
    return (PyObject *)o;
}


PyObject *Image_PyObject__orientate(PyObject *self, PyObject *args)
{
    int orientation;

    if (!PyArg_ParseTuple(args, "i", &orientation))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_image_orientate(orientation);
    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *Image_PyObject__flip(PyObject *self, PyObject *args)
{
    int horiz, vert, diag;

    if (!PyArg_ParseTuple(args, "iii", &horiz, &vert, &diag))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    if (horiz) imlib_image_flip_horizontal();
    if (vert)  imlib_image_flip_vertical();
    if (diag)  imlib_image_flip_diagonal();

    Py_INCREF(Py_None);
    return Py_None;
}

PyObject *Image_PyObject__clone(PyObject *self, PyObject *args)
{
    Imlib_Image *image;
    Image_PyObject *o;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    image = imlib_clone_image();
    if (!image) {
        PyErr_Format(PyExc_RuntimeError, "Failed to clone image");
    return NULL;
    }

    o = _new_image_pyobject(image);
    return (PyObject *)o;
}


PyObject *Image_PyObject__blend(PyObject *self, PyObject *args)
{
    int dst_x, dst_y, src_alpha = 255, merge_alpha = 1,
        src_w, src_h, src_x = 0, src_y = 0, dst_w, dst_h;
    Image_PyObject *src;
    Imlib_Image *src_img;
    Imlib_Color_Modifier cmod;

    if (!PyArg_ParseTuple(args, "O!(ii)(ii)(ii)(ii)ii", &Image_PyObject_Type,
              &src, &src_x, &src_y, &src_w, &src_h, &dst_x, &dst_y,
              &dst_w, &dst_h, &src_alpha, &merge_alpha))
        return NULL;


    if (src_alpha == 0) {
        Py_INCREF(Py_None);
        return Py_None;
    }

    src_img = ((Image_PyObject *)src)->image;

    if (src_alpha < 255) {
        unsigned char a[256], linear[256];
        int i;
        for (i = 0; i < 256; i++) {
            int temp = (i * src_alpha) + 0x80;
            a[i] = ((temp + (temp >> 8)) >> 8);
            linear[i] = i;
        }
        cmod = imlib_create_color_modifier();
        imlib_context_set_color_modifier(cmod);
        imlib_set_color_modifier_tables(linear, linear, linear, a);
    }

    imlib_context_set_image(((Image_PyObject *)self)->image);

    imlib_context_set_blend( src_alpha == 256 ? 0 : 1);
    imlib_blend_image_onto_image(src_img, merge_alpha,
                     src_x, src_y, src_w, src_h,
                     dst_x, dst_y, dst_w, dst_h);
    imlib_context_set_blend(1);
    imlib_context_set_color_modifier(NULL);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__draw_mask(PyObject *self, PyObject *args)
{
    int dst_x, dst_y, mask_w, mask_h, dst_w, dst_h;
    Image_PyObject *mask;
    unsigned long xpos, ypos, dst_pos, mask_pos;
    unsigned char *dst_data, *mask_data;

    unsigned char *mask_chunk, *dst_chunk, avg;

    if (!PyArg_ParseTuple(args, "O!ii", &Image_PyObject_Type, &mask, &dst_x,
              &dst_y))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)mask)->image);
    mask_w = imlib_image_get_width();
    mask_h = imlib_image_get_height();
    mask_data = (unsigned char *)imlib_image_get_data_for_reading_only();

    imlib_context_set_image(((Image_PyObject *)self)->image);
    dst_w = imlib_image_get_width();
    dst_h = imlib_image_get_height();
    dst_data = (unsigned char *)imlib_image_get_data();

    // Use the passed image as a mask.  Again, no obvious way to do this in
    // Imlib natively.
    for (ypos = 0; ypos < mask_h; ypos++) {
        if (ypos + dst_y >= dst_h) break;
        for (xpos = 0; xpos < mask_w; xpos++) {
            if (xpos + dst_x >= dst_w) break;
            mask_pos = (xpos << 2) + (ypos * mask_w << 2);
            dst_pos = ((dst_x + xpos) << 2) + ((dst_y + ypos) * dst_w << 2);

            mask_chunk = &mask_data[mask_pos];
            dst_chunk = &dst_data[dst_pos];

            // Any way to optimize this?
            avg = (mask_chunk[0] + mask_chunk[1] + mask_chunk[2]) / 3;

            // Blend average (grayscale) pixel from the mask with the
            // alpha channel of the image
#if 1
            // This is the code from Tack, but it doesn't work
            // like it should ... -- Dischi
            // (tack) Well, should work like this:
            int temp = (dst_chunk[3] * avg) + 0x80;
            dst_chunk[3] = ((temp + (temp >> 8)) >> 8);
#else
            // ... so this is my guess -- Dischi
            dst_chunk[3] = (dst_chunk[3] * avg) / 255;
#endif
        }
    }
    imlib_image_put_back_data((DATA32 *)dst_data);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__draw_text(PyObject *self, PyObject *args)
{
    int x, y, w, h, advance_w, advance_h, r, g, b, a;
    char *text;
    Font_PyObject *font;

    if (!PyArg_ParseTuple(args, "O!iis(iiii)", &Font_PyObject_Type, &font, &x,
              &y, &text, &r, &g, &b, &a))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_context_set_font(((Font_PyObject *)font)->font);

    imlib_context_set_color(r, g, b, a);
    imlib_text_draw_with_return_metrics(x, y, text, &w, &h, &advance_w,
                    &advance_h);
    return Py_BuildValue("(llll)", w, h, advance_w, advance_h);
}


PyObject *Image_PyObject__draw_rectangle(PyObject *self, PyObject *args)
{
    int x, y, w, h, r, g, b, a, fill = 0;

    if (!PyArg_ParseTuple(args, "iiii(iiii)|i", &x, &y, &w, &h, &r, &g, &b, &a,
              &fill))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_image_set_has_alpha(1);
    imlib_context_set_color(r, g, b, a);
    if (!fill)
        imlib_image_draw_rectangle(x, y, w, h);
    else
        imlib_image_fill_rectangle(x, y, w, h);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__draw_ellipse(PyObject *self, PyObject *args)
{
    int xc, yc, ea, eb, r, g, b, a, fill = 0;

    if (!PyArg_ParseTuple(args, "iiii(iiii)|i", &xc, &yc, &ea, &eb, &r, &g, &b,
              &a, &fill))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_context_set_color(r, g, b, a);
    imlib_context_set_anti_alias(1);
    if (!fill)
        imlib_image_draw_ellipse(xc, yc, ea, eb);
    else
        imlib_image_fill_ellipse(xc, yc, ea, eb);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__set_alpha(PyObject *self, PyObject *args)
{
    int alpha = 0;

    if (!PyArg_ParseTuple(args, "i", &alpha))
        return NULL;
    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_image_set_has_alpha(alpha);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__copy_rect(PyObject *self, PyObject *args)
{
    int src_x, src_y, w, h, dst_x, dst_y;
    if (!PyArg_ParseTuple(args, "(ii)(ii)(ii)", &src_x, &src_y, &w, &h, &dst_x,
              &dst_y))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_image_copy_rect(src_x, src_y, w, h, dst_x, dst_y);
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__get_pixel(PyObject *self, PyObject *args)
{
    int x, y;
    Imlib_Color col;
    if (!PyArg_ParseTuple(args, "(ii)", &x, &y))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    imlib_image_query_pixel(x, y, &col);

    return Py_BuildValue("(iiii)", col.blue, col.green, col.red, col.alpha);
}

// This function returns a buffer object that contains the requested
// raw pixel data.  If native pixel format (BGRA) is requested, it
// will return a buffer object of the Image_PyObject itself (which
// implements the buffer interface above).  If it's a non-native pixel
// format, it will create a new buffer object from new memory (the buffer
// object maintains its own memory) and memcpy the pixel data to that object.
PyObject *Image_PyObject__get_raw_data(PyObject *self, PyObject *args)
{
    char *format;
    int len, write;
    Image_PyObject *o = (Image_PyObject *)self;


    if (!PyArg_ParseTuple(args, "si", &format, &write))
        return NULL;

    imlib_context_set_image(o->image);
    if (!strcmp(format, "BGRA")) {
        // Requested native format, so create a buffer directly from the
        // Image pyobject.
        if (write)
            return PyBuffer_FromReadWriteObject(self, 0, Py_END_OF_BUFFER);
        else
            return PyBuffer_FromObject(self, 0, Py_END_OF_BUFFER);
    } else {
        // Requested different format, create a new buffer.
        PyObject *buffer;
        unsigned char *data;

        buffer = PyBuffer_New(get_raw_bytes_size(format));
        PyObject_AsWriteBuffer(buffer, (void **)&data, &len);
        get_raw_bytes(format, data);
        return buffer;
    }
}


PyObject *Image_PyObject__put_back_raw_data(PyObject *self, PyObject *args)
{
    Image_PyObject *o = (Image_PyObject *)self;
    PyObject *buffer_object;
    unsigned char *buffer;
    int len;
    
    if (!PyArg_ParseTuple(args, "O!", &PyBuffer_Type, &buffer_object))
        return NULL;

    imlib_context_set_image(o->image);
    PyObject_AsWriteBuffer(buffer_object, (void **)&buffer, &len);
    if (buffer != o->raw_data) {
        PyErr_Format(PyExc_ValueError, "Putting back a buffer that wasn't gotten with get_raw_data()!");
        return NULL;
    }
    imlib_image_put_back_data((DATA32 *)buffer);
    o->raw_data = NULL;
    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Image_PyObject__save(PyObject *self, PyObject *args)
{
    char *filename, *ext;

    if (!PyArg_ParseTuple(args, "ss", &filename, &ext))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)self)->image);
    // TODO: call imlib_save_image_with_error_return

    /* set the image format to be the format of the extension of our last */
    /* argument - i.e. .png = png, .tif = tiff etc. */
    imlib_image_set_format(ext);
    imlib_save_image(filename);
    Py_INCREF(Py_None);
    return Py_None;
}


PyMethodDef Image_PyObject_methods[] = {
    { "draw_rectangle", Image_PyObject__draw_rectangle, METH_VARARGS },
    { "draw_ellipse", Image_PyObject__draw_ellipse, METH_VARARGS },
    { "draw_text", Image_PyObject__draw_text, METH_VARARGS },
    { "draw_mask", Image_PyObject__draw_mask, METH_VARARGS },
    { "clear", Image_PyObject__clear, METH_VARARGS },
    { "copy_rect", Image_PyObject__copy_rect, METH_VARARGS },
    { "clone", Image_PyObject__clone, METH_VARARGS },
    { "scale", Image_PyObject__scale, METH_VARARGS },
    { "rotate", Image_PyObject__rotate, METH_VARARGS },
    { "orientate", Image_PyObject__orientate, METH_VARARGS },
    { "flip", Image_PyObject__flip, METH_VARARGS },
    { "blend", Image_PyObject__blend, METH_VARARGS },
    { "set_alpha", Image_PyObject__set_alpha, METH_VARARGS },
    { "get_raw_data", Image_PyObject__get_raw_data, METH_VARARGS },
    { "put_back_raw_data", Image_PyObject__put_back_raw_data, METH_VARARGS },
    { "get_pixel", Image_PyObject__get_pixel, METH_VARARGS },
    { "save", Image_PyObject__save, METH_VARARGS },
    { NULL, NULL }
};

PyObject *Image_PyObject__getattr(Image_PyObject *self, char *name)
{
    imlib_context_set_image(self->image);
    if (!strcmp(name, "width"))
        return Py_BuildValue("l", imlib_image_get_width());
    else if (!strcmp(name, "height"))
        return Py_BuildValue("l", imlib_image_get_height());
    else if (!strcmp(name, "has_alpha"))
        return Py_BuildValue("l", imlib_image_has_alpha());
    else if (!strcmp(name, "rowstride"))
        return Py_BuildValue("l", imlib_image_get_width() * 4);
    else if (!strcmp(name, "format"))
        return Py_BuildValue("s", imlib_image_format());
    else if (!strcmp(name, "mode"))
        return Py_BuildValue("s", "BGRA");
    else if (!strcmp(name, "filename"))
        return Py_BuildValue("s", imlib_image_get_filename());

    return Py_FindMethod(Image_PyObject_methods, (PyObject *)self, name);
}
