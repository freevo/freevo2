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

#include <X11/Xlib.h>

#define Display_PyObject_Check(v) ((v)->ob_type == &Display_PyObject_Type)

typedef struct {
    PyObject_HEAD

    Display *display;
    Window   window;
    Visual  *visual;
    Colormap cmap;
    int      depth;
    Cursor   invisible_cursor;
    double   last_mousemove_time;

    PyObject * input_callback;
    PyObject * expose_callback;

} Display_PyObject;

extern PyTypeObject Display_PyObject_Type;
void Display_PyObject__dealloc(Display_PyObject *);
PyObject *Display_PyObject__getattr(Display_PyObject *, char *);
int Display_PyObject__setattr( Display_PyObject *self, char *name,
			       PyObject * result );

PyObject *display_new(int w, int h);
