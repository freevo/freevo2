#include <Python.h>
#include "config.h"

#ifdef USE_EPEG
#include "Epeg.h"
#endif

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

PyObject *epeg_thumbnail(PyObject *self, PyObject *args) {
  int w, h, dest_w, dest_h;
  char *source;
  char *dest;

#ifdef USE_EPEG
  Epeg_Image *im;

  if (!PyArg_ParseTuple(args, "ss(ii)", &source, &dest, &dest_w, &dest_h))
    return PyErr_SetString(PyExc_ValueError, "parameter error"), (PyObject*)NULL;

  im = epeg_file_open(source);
  if (!im)
    return PyErr_SetString(PyExc_IOError, "unable to load image"), (PyObject*)NULL;

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
  epeg_quality_set(im, 80);
  epeg_thumbnail_comments_enable(im, 1);
  
  epeg_file_output_set(im, dest);
  epeg_close(im);

  Py_INCREF(Py_None);
  return Py_None;

#else
  return PyErr_SetString(PyExc_ValueError, "epeg support missing"), 
    (PyObject*)NULL;
#endif
}
