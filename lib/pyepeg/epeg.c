#include <Python.h>
#include "Epeg.h"

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

static PyObject *epeg_jpeg_thumbnail(PyObject *self, PyObject *args) {
  int w, h, dest_w, dest_h;
  char *source;
  char *dest;
  
  Epeg_Image *im;

  if (!PyArg_ParseTuple(args, "ssii", &source, &dest, &dest_w, &dest_h))
    return PyErr_SetString(PyExc_ValueError, "parameter error"), (PyObject*)NULL;

  im = epeg_file_open(source);
  if (!im)
    return PyErr_SetString(PyExc_ValueError, "image error"), (PyObject*)NULL;

  epeg_size_get(im, &w, &h);
  
  if (w / dest_w > h / dest_h)
    dest_h = (h * dest_w) / w;
  else if (w / dest_w < h / dest_h)
    dest_w = (w * dest_h) / h;
  
  epeg_decode_size_set(im, dest_w, dest_h);
  epeg_quality_set(im, 80);
  epeg_thumbnail_comments_enable(im, 1);
  epeg_file_output_set(im, dest);
  epeg_encode(im);
  epeg_close(im);
  Py_INCREF(Py_None);
  return Py_None;
}

static PyObject *epeg_freevo_thumbnail(PyObject *self, PyObject *args) {
  int w, h;
  int dest_w=255;
  int dest_h=255;
  char *source;
  char *dest;
  const char *pixel;
  int fd;
  
  Epeg_Image *im;

  if (!PyArg_ParseTuple(args, "ss", &source, &dest)) {
    return PyErr_SetString(PyExc_ValueError, "parameter error"), (PyObject*)NULL;
  }
  
  im = epeg_file_open(source);
  if (!im) {
    return PyErr_SetString(PyExc_ValueError, "image error"), (PyObject*)NULL;
  }

  epeg_size_get(im, &w, &h);
  
  if (w / dest_w > h / dest_h)
    dest_h = (h * dest_w) / w;
  else if (w / dest_w < h / dest_h)
    dest_w = (w * dest_h) / h;
  
  epeg_decode_size_set(im, dest_w, dest_h);
  epeg_quality_set(im, 80);

  pixel = epeg_pixels_get(im, 0, 0, dest_w, dest_h);

  fd = open(dest, O_CREAT | O_TRUNC | O_WRONLY, 
	    S_IRUSR | S_IWUSR | S_IRGRP | S_IWGRP | S_IROTH);
  write(fd, "FRI", 3);
  write(fd, (char*) &dest_w, 1);
  write(fd, (char*) &dest_h, 1);
  write(fd, "RGB  ", 5);
  write(fd, pixel, dest_h * dest_w * 3);
  close(fd);
    
  epeg_pixels_free(im, pixel);
  epeg_close(im);
  Py_INCREF(Py_None);
  return Py_None;
}


static PyMethodDef epegMethods[] = {
  {"jpg_thumbnail",  epeg_jpeg_thumbnail, METH_VARARGS},
  {"fri_thumbnail", epeg_freevo_thumbnail, METH_VARARGS},
  {NULL, NULL}
};

void initepeg() {
  (void) Py_InitModule("epeg", epegMethods);
}
