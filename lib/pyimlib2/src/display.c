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
#include "display.h"
#include <Imlib2.h>
#include "image.h"

double get_curtime()
{
    struct timeval curtime;
    struct timezone tz;

    gettimeofday(&curtime, &tz);
    return curtime.tv_sec + (curtime.tv_usec/(1000.0*1000));
}


PyTypeObject Display_PyObject_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_Imlib2.Display",         /*tp_name*/
    sizeof(Display_PyObject),  /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)Display_PyObject__dealloc, /* tp_dealloc */
    0,                         /*tp_print*/
    (getattrfunc)Display_PyObject__getattr, /* tp_getattr */
    (setattrfunc)Display_PyObject__setattr, /* tp_setattr */
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


PyObject *Display_PyObject__render( Display_PyObject *self, PyObject *args)
{
    Image_PyObject *img;
    int dst_x = 0, dst_y = 0, src_x = 0, src_y = 0,
        w = -1, h = -1, img_w, img_h, dither = 1, blend = 0;
    if (!PyArg_ParseTuple(args, "O!|(ii)(ii)(ii)ii", &Image_PyObject_Type,
			  &img, &dst_x, &dst_y, &src_x, &src_y, &w, &h,
			  &dither, &blend))
        return NULL;

    imlib_context_set_image(((Image_PyObject *)img)->image);
    img_w = imlib_image_get_width();
    img_h = imlib_image_get_height();

    if (w == -1) w = img_w;
    if (h == -1) h = img_h;

    display_set_context(self);

    imlib_context_set_dither(dither);
    imlib_context_set_blend(blend);
    if (src_x == 0 && src_y == 0 && w == img_w && h == img_h)
        imlib_render_image_on_drawable(dst_x, dst_y);
    else
        imlib_render_image_part_on_drawable_at_size(src_x, src_y, w, h, dst_x,
                                dst_y, w, h);

    Py_INCREF(Py_None);
    return Py_None;
}


PyObject *Display_PyObject__handle_events( Display_PyObject *self, PyObject *args )
{
  XEvent ev;
  double now = get_curtime();
  float cursor_timeout;
  PyObject *retval = Py_False, *regions = NULL, *val;

  if (args && !PyArg_ParseTuple(args, "f", &cursor_timeout))
     return NULL;

  while ( XPending( self->display ) ) {
    XNextEvent( self->display, &ev );

    if ( ( ev.type == KeyPress ) && PyCallable_Check( self->input_callback ) ) {
      val = Py_BuildValue( "(i)", ev.xkey.keycode);
      PyEval_CallObject(self->input_callback, val);
      Py_DECREF(val);
    } else if ( ( ev.type == Expose ) && PyCallable_Check( self->expose_callback ) ) {
        if (!regions)
            regions = PyList_New(0);
        val = Py_BuildValue("((ii)(ii))", ev.xexpose.x, ev.xexpose.y, 
                            ev.xexpose.width, ev.xexpose.height);
        PyList_Append(regions, val);
        Py_DECREF(val);
    } else if (ev.type == MotionNotify) {
       self->last_mousemove_time = now;
       if (cursor_timeout != 0)
          XUndefineCursor(self->display, self->window);
    }
	retval = Py_True;
  }
  if (self->last_mousemove_time && now - self->last_mousemove_time >= cursor_timeout) {
    self->last_mousemove_time = 0;
    if (cursor_timeout >= 0)
       XDefineCursor(self->display, self->window, self->invisible_cursor);
  }

  if (regions) {
      val = Py_BuildValue("(O)", regions);
      PyEval_CallObject( self->expose_callback, val);
      Py_DECREF(val);
      Py_DECREF(regions);
    }
  // Returns True if an event was handled, or False otherwise.
  Py_INCREF(retval);
  return retval;
}


PyMethodDef Display_PyObject_methods[] = {
    { "render", ( PyCFunction ) Display_PyObject__render, METH_VARARGS },
    { "handle_events", ( PyCFunction ) Display_PyObject__handle_events, METH_VARARGS },
    { NULL, NULL }
};


PyObject *Display_PyObject__getattr(Display_PyObject *self, char *name)
{
  if ( ! strcmp( name, "socket" ) )
    return Py_BuildValue( "i", ConnectionNumber( self->display ) );
  if ( ! strcmp(name,  "input_callback" ) )
    return Py_BuildValue( "O", self->input_callback );
  if ( ! strcmp(name,  "expose_callback" ) )
    return Py_BuildValue( "O", self->expose_callback );

  return Py_FindMethod(Display_PyObject_methods, (PyObject *)self, name);
}


int Display_PyObject__setattr( Display_PyObject *self, char *name,
			       PyObject * value )
{
  if ( ! strcmp(name,  "input_callback" ) ) {
    if ( ! PyCallable_Check( value ) ) {
      PyErr_SetString( PyExc_TypeError,
               "value is not a callable object" );
      return -1;
    }

    Py_DECREF( self->input_callback );
    self->input_callback = value;
    Py_INCREF( self->input_callback );

    return 0;
  } else if ( ! strcmp(name,  "expose_callback" ) ) {
    if ( ! PyCallable_Check( value ) ) {
      PyErr_SetString( PyExc_TypeError,
               "value is not a callable object" );
      return -1;
    }

    Py_DECREF( self->expose_callback );
    self->expose_callback = value;
    Py_INCREF( self->expose_callback );

    return 0;
  }

  ( void )PyErr_Format( PyExc_ValueError, "unknown: %s\n", name );
  return -1;
}


PyObject *display_new(int w, int h)
{
    Display_PyObject *o;
    Display *display;
    int screen;
    // For hidden cursor
    Pixmap pix;
    static char bits[] = {0, 0, 0, 0, 0, 0, 0, 0};
    XColor cfg;

    display = XOpenDisplay(NULL);
    if (!display) {
        PyErr_Format( PyExc_RuntimeError, "Can't open X11 display\n");
        return NULL;
    }

    o = PyObject_NEW(Display_PyObject, &Display_PyObject_Type);
    o->display = display;
    screen = DefaultScreen(o->display);

    o->visual = DefaultVisual(o->display, screen);
    o->depth = DefaultDepth(o->display, screen);
    o->cmap = DefaultColormap(o->display, screen);

    o->window = XCreateSimpleWindow(o->display,
            DefaultRootWindow(o->display),
            0, 0, w, h, 0, 0, 0);
    Py_INCREF(Py_None);
    o->input_callback = Py_None;
    Py_INCREF(Py_None);
    o->expose_callback = Py_None;

    // Construct an invisible cursor for mouse hiding.
    cfg.red = cfg.green = cfg.blue = 0;
    pix = XCreateBitmapFromData(o->display, o->window, bits, 8, 8);
    o->invisible_cursor = XCreatePixmapCursor(o->display, pix, pix, &cfg, &cfg, 0, 0);
    XFreePixmap(o->display, pix);

    XSelectInput( o->display, o->window, ExposureMask | KeyPressMask | PointerMotionMask);
    XMapWindow(o->display, o->window);

    if ( XPending( o->display ) )
      Display_PyObject__handle_events( o, NULL );

    return (PyObject *)o;
}
