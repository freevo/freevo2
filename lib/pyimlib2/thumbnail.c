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

#define X_DISPLAY_MISSING
#include <Imlib2.h>

#ifdef USE_EPEG
#include "Epeg.h"
#endif

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

/* png write function stolen from epsilon (see png.c) */
extern int _png_write (const char *file, DATA32 * ptr,
                       int tw, int th, int sw, int sh, char *imformat,
                       int mtime, char *uri);

PyObject *epeg_thumbnail(PyObject *self, PyObject *args)
{
    int iw, ih, tw, th, ret;
    char *source;
    char *dest;
    
#ifdef USE_EPEG
    Epeg_Image *im;
    Epeg_Thumbnail_Info info;
#endif

#ifdef USE_EPEG
    if (!PyArg_ParseTuple(args, "ss(ii)", &source, &dest, &tw, &th))
        return NULL;

    im = epeg_file_open(source);
    if (im) {
        Py_BEGIN_ALLOW_THREADS
        epeg_size_get(im, &iw, &ih);

        if (iw > tw || ih > th) {
            if (iw / tw > ih / th)
                th = (ih * tw) / iw;
            else
                tw = (iw * th) / ih;
        } else {
            tw = iw;
            th = ih;
        }
    
        epeg_decode_size_set(im, tw, th);
        epeg_quality_set(im, 80);
        epeg_thumbnail_comments_enable(im, 1);
    
        epeg_file_output_set(im, dest);
        ret = epeg_encode (im);
        Py_END_ALLOW_THREADS
        if (!ret) {
            epeg_close(im);
            Py_INCREF(Py_None);
            return Py_None;
        }
        
        epeg_close(im);
        PyErr_SetString(PyExc_IOError, "epeg failed");
    } else
        PyErr_SetString(PyExc_IOError, "epeg failed");
      
#else
    PyErr_SetString(PyExc_IOError, "epeg support missing");
#endif
    return NULL;
}

PyObject *png_thumbnail(PyObject *self, PyObject *args)
{
    int iw, ih, tw, th;
    char *source;
    char *dest;

    int mtime;
    char uri[PATH_MAX];
    char format[32];
    struct stat filestatus;
    Imlib_Image tmp = NULL;
    Imlib_Image src = NULL;

    if (!PyArg_ParseTuple(args, "ss(ii)", &source, &dest, &tw, &th))
        return NULL;

    if (stat (source, &filestatus) != 0) {
        PyErr_SetString(PyExc_ValueError, "pyimlib2: unable to load image");
        return NULL;
    }
      
    mtime = filestatus.st_mtime;
    if ((tmp = imlib_load_image_immediately_without_cache (source))) {
        imlib_context_set_image (tmp);
        snprintf (format, 32, "image/%s", imlib_image_format ());
        iw = imlib_image_get_width ();
        ih = imlib_image_get_height ();
        if (iw > tw || ih > th) {
            if (iw / tw > ih / th)
                th = (ih * tw) / iw;
            else
                tw = (iw * th) / ih;

	    /* scale image down to thumbnail size */
	    imlib_context_set_cliprect (0, 0, tw, th);
	    src = imlib_create_cropped_scaled_image (0, 0, iw, ih, tw, th);
	    if (!src) {
	        imlib_free_image_and_decache ();
	        PyErr_SetString(PyExc_IOError, "pyimlib2 scale error");
		return NULL;
	    }
	    /* free original image and set context to new one */
	    imlib_free_image_and_decache ();
	    imlib_context_set_image (src);
	      
        } else {
            tw = iw;
            th = ih;
        }
    } else {
        PyErr_SetString(PyExc_ValueError, "pyimlib2: unable to load image");
        return NULL;
    }
    
    imlib_image_set_has_alpha (1);
    imlib_image_set_format ("argb");
    snprintf (uri, PATH_MAX, "file://%s", source);
    if (_png_write (dest, imlib_image_get_data (), tw, th, iw, ih,
		    format, mtime, uri)) {
      imlib_free_image_and_decache ();
      Py_INCREF(Py_None);
      return Py_None;
    }

    PyErr_SetString(PyExc_ValueError, "pyimlib2: unable to save image");
    return NULL;
}


PyObject *fail_thumbnail(PyObject *self, PyObject *args)
{
    Imlib_Image image = NULL;
    char uri[PATH_MAX];
    char *source;
    char *dest;
    char format[32];

    if (!PyArg_ParseTuple(args, "ss", &source, &dest))
        return NULL;

    image = imlib_create_image(1, 1);
    imlib_context_set_image(image);
    imlib_image_set_has_alpha(1);
    imlib_image_clear_color(0, 0, 0, 0);

    snprintf (uri, PATH_MAX, "file://%s", source);
    snprintf (format, 32, "image/%s", imlib_image_format ());
    
    if (_png_write (dest, imlib_image_get_data (), 1, 1, 1, 1, format, 0, uri)) {
        imlib_free_image_and_decache ();
	Py_INCREF(Py_None);
	return Py_None;
    }
    imlib_free_image_and_decache ();
    PyErr_SetString(PyExc_ValueError, "pyimlib2: unable to save image");
    return NULL;
}
