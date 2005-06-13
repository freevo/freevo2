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

#define Image_PyObject_Check(v) ((v)->ob_type == &Image_PyObject_Type)

typedef struct {
    PyObject_HEAD
    Imlib_Image *image;
    void *raw_data;
} Image_PyObject;

extern PyTypeObject Image_PyObject_Type;
void Image_PyObject__dealloc(Image_PyObject *);
PyObject *Image_PyObject__getattr(Image_PyObject *, char *);

// Exported
Imlib_Image *imlib_image_from_pyobject(Image_PyObject *pyimg);

