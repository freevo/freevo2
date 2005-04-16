/*
 * ----------------------------------------------------------------------------
 * Imlib2 wrapper for Python
 * ----------------------------------------------------------------------------
 * $Id$
 *
 * ----------------------------------------------------------------------------
 * Copyright (C) 2004-2005 Jason Tackaberry <tack@sault.org>
 *
 * First Edition: Dirk Meyer <dmeyer@tzi.de>
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
#include "config.h"

#ifdef USE_EPEG
#include "Epeg.h"
#endif

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

PyObject *epeg_thumbnail(PyObject *self, PyObject *args)
{
    int w, h, dest_w, dest_h;
    char *source;
    char *dest;

#ifdef USE_EPEG
    Epeg_Image *im;
    Epeg_Thumbnail_Info info;

    if (!PyArg_ParseTuple(args, "ss(ii)", &source, &dest, &dest_w, &dest_h))
        return NULL;

    im = epeg_file_open(source);
    if (!im)
        return PyErr_SetString(PyExc_IOError, "unable to load image"), NULL;

    epeg_thumbnail_comments_get (im, &info);
    epeg_size_get(im, &w, &h);

    if (w > dest_w || h > dest_h) {
        if (w / dest_w > h / dest_h)
            dest_h = (h * dest_w) / w;
        else
            dest_w = (w * dest_h) / h;
    } else {
        dest_w = w;
        dest_h = h;
    }

    epeg_decode_size_set(im, dest_w, dest_h);
    epeg_quality_set(im, 100);
    epeg_thumbnail_comments_enable(im, 1);

    epeg_file_output_set(im, dest);
    if(epeg_encode (im)) {
        epeg_close(im);
        PyErr_SetString(PyExc_IOError, "unable to encode image");
	return NULL;
    }
    epeg_close(im);

    Py_INCREF(Py_None);
    return Py_None;

#else
  return PyErr_SetString(PyExc_ValueError, "epeg support missing"), NULL;
#endif
}
