/*
 * Basic libvisual functionality module for Freevo.
 * Authored by: Viggo Fredriksen <viggo@katatonic.org> 2004
 * Released under LGPL.
 */

#define HAVE_MMX 1
#include <Python.h>
#include <libvisual.h>
#include <stdio.h>


// Handy macros
#define RAISE(x,y) (PyErr_SetString((x), (y)), (PyObject*)NULL)
#define RETURN_NONE return (Py_INCREF(Py_None), Py_None);


/* The visualization object datastruct */
typedef struct {
    PyObject_HEAD
    VisVideo *video;
    VisBin *bin;
    int depth;
    int width;
    int height;
    char *input_name;
    char *actor_name;
    int changed_res;
    int changed_input;
    int changed_actor;
} Visual;
