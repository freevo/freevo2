/*
 * Basic libvisual functionality module for Freevo.
 * Authored by: Viggo Fredriksen <viggo@katatonic.org> 2004
 * Released under GPL.
 */

// TODO: This is NOT working

#define HAVE_MMX 1
//#define USE_IMLIB2
#include <Python.h>

#ifdef USE_IMLIB2
#define X_DISPLAY_MISSING
#include <Imlib2.h>

typedef struct {
	PyObject_HEAD
	Imlib_Image *image;
} Image_PyObject;

#endif //USE_IMLIB2

#include <libvisual.h>
#include <stdio.h>


// Handy macros
#define RAISE(x,y) (PyErr_SetString((x), (y)), (PyObject*)NULL)
#define RETURN_NONE return (Py_INCREF(Py_None), Py_None);


/* The visualization object datastruct */
typedef struct {
    PyObject_HEAD
    VisActor *actor;
    VisVideo *video;
    VisInput *input;
    VisBin *bin;
    int depth;
    int width;
    int height;
    char *input_name;
    char *vis_name;
    unsigned char *scrbuf;

} Visual;
