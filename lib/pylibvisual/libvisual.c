/*
 * Basic libvisual functionality module for Freevo.
 * Authored by: Viggo Fredriksen <viggo@katatonic.org> 2004
 * Released under GPL.
 * -----------------------------------------------------------------------------
 * TODO:
 *  - Add morphing for changing between plugins
 *  - Optimize set methods for faster (re)init
 *  - Add support for pyimlib2
 * --- What's working right now:
 *  - changing actor on the fly
 *  - changing size on the fly
 *  - changing input actor on the fly
 */
#include "libvisual.h"

/*
 * Deallocates data for the visualization
 */
static void
bin_dealloc(Visual *self)
{
    /* This deallocation is what I have found to be working
     * best, the examples shows an destroying self->bin,
     * but I hade some leaks when doing this */
    visual_actor_destroy(self->actor);
    visual_video_free(self->video);
    visual_input_destroy(self->input);
    visual_bin_free(self->bin);
    free(self->scrbuf);

    //self->ob_type->tp_free((PyObject*)self);
    PyMem_DEL(self);
}

/*
 * Type init method
 */
static int
bin_init(Visual *self, PyObject *args, PyObject *kwds)
{
    /* default values */
    self->depth = 24;
    self->input_name = "mplayer";
    if (!PyArg_ParseTuple(args, "s(ii)|si",
			  &self->vis_name,   &self->width, &self->height,
			  &self->input_name )) {
        PyErr_SetString(PyExc_AttributeError, "wrong parameter");
        return -1;
    }
    
    /* Create the video container */
    self->video = visual_video_new();

    /* Create an actor */
    self->actor = visual_actor_new(self->vis_name);

    /* Realize the actor */
    visual_actor_realize (self->actor);

    /* Link the video context to the actor */
    visual_actor_set_video (self->actor, self->video);

    /* Set the depth */
    VisVideoDepth dpt = visual_video_depth_enum_from_value(self->depth);

    /* Check if the user given depth is sane */
    if (visual_video_depth_is_sane (dpt) == 0) {
        PyErr_SetString(PyExc_RuntimeError, "visual_video_depth_is_sane");
        return -1;
    }

    visual_video_set_depth (self->video, dpt);

    /* Set dimension */
    visual_video_set_dimension (self->video, self->width, self->height);


    /* Negotiate with video, if needed, the actor will set up and enviroment
     * for depth transformation and it does all the size negotation stuff */
    if (visual_actor_video_negotiate (self->actor, 0, FALSE, FALSE) == -1) {
      PyErr_SetString(PyExc_RuntimeError, "visual_actor_video_negotiate");
      return -1;
    }
    
    /* Now we know the size, allocate the buffer */
    self->scrbuf = malloc (self->video->size);

    /* Link the buffer to the video context */
    visual_video_set_buffer (self->video, self->scrbuf);


    /* Create the input plugin */
    self->input = visual_input_new (self->input_name);

    if (self->input == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "input == NULL");
        return -1;
    }
      
    /* Create a new bin, a bin is a container for easy
     * management of an working input, actor, render, output pipeline */
    self->bin = visual_bin_new ();

    /* Add the actor, input, video to the bin */
    visual_bin_connect (self->bin, self->actor, self->input);
    visual_bin_realize (self->bin);
    visual_bin_sync(self->bin, FALSE);

    return 0;
}


/* ***** Python Methods *******************************************************/

/*
 * Get input plugin names
 */
static PyObject *
bin_get_input_plugins(Visual *self)
{
    char* name = NULL;
    PyObject *list = PyList_New(0);

    do {
        name = visual_input_get_next_by_name(name);

        if (name != NULL) {
            PyObject *str = PyString_FromString(name);
            Py_XINCREF(str);
            PyList_Append(list, str);
            Py_XDECREF(str);
        }
    } while (name != NULL);

    Py_INCREF(list);

    return list;
}


/*
 * Set input plugin
 */
static PyObject *
bin_set_input_plugin(Visual *self, PyObject *args)
{

    if (!PyArg_ParseTuple(args, "s", &self->input_name))
        return (PyObject*) NULL;
    if (visual_input_valid_by_name(self->input_name) == 0)
        RAISE(PyExc_Exception, "Invalid input name");

    visual_input_destroy(self->input);
    self->input = visual_input_new(self->input_name);

    /* Add the actor, input, video to the bin */
    visual_bin_connect (self->bin, self->actor, self->input);
    visual_bin_realize (self->bin);
    visual_bin_sync(self->bin, FALSE);

    RETURN_NONE;
}


/*
 * Set visualization plugin
 */
static PyObject *
bin_set_visualization_plugin(Visual *self, PyObject *args)
{
    if (!PyArg_ParseTuple(args, "s", &self->vis_name))
        RAISE(PyExc_ValueError, "Wrong parameters");
    /* check if the actor name is valid */
    if (visual_input_valid_by_name(self->vis_name) == -1) {
        RAISE(PyExc_Exception, "Invalid visualization plugin name");
    }

    /* destroy the old actor */
    visual_actor_destroy(self->actor);

    /* Create the actor */
    self->actor = visual_actor_new(self->vis_name);

    /* Realize the actor */
    visual_actor_realize (self->actor);

    /* Link the video context to the actor */
    visual_actor_set_video (self->actor, self->video);

    /* negotiate the actor and video */
    if (visual_actor_video_negotiate (self->actor,0,FALSE,FALSE)==-1)
        RAISE(PyExc_Exception, "Actor->video negotiation failed");

    visual_bin_sync(self->bin, FALSE);

    RETURN_NONE;
}

/*
 * Get visualization plugin names
 */
static PyObject *
bin_get_visualization_plugins(Visual *self)
{
    char* name = NULL;
    PyObject *list = PyList_New(0);

    do {
        name = visual_actor_get_next_by_name_nogl(name);

        if (name != NULL) {
            PyObject *str = PyString_FromString(name);
            Py_XINCREF(str);
            PyList_Append(list, str);
            Py_XDECREF(str);
        }
    } while (name != NULL);

    Py_INCREF(list);

    return list;
}

/*
 * Get next visualization plugin name
 * XXX: This have had some problems, but somehow seems to work atm
 */
static PyObject *
bin_get_next_visualization_plugin(Visual *self) {
    char *str;
    str = visual_actor_get_next_by_name_nogl(self->vis_name);
    return (PyObject*)Py_BuildValue("s",str);
}


/*
 * Get possible morph plugins
 */
static PyObject *
bin_get_morph_plugins(Visual *self)
{
    char* name = NULL;
    PyObject *list = PyList_New(0);

    do {
        name = visual_morph_get_next_by_name(name);

        if (name != NULL) {
            PyObject *str = PyString_FromString(name);
            Py_XINCREF(str);
            PyList_Append(list, str);
            Py_XDECREF(str);
        }
    } while (name != NULL);

    Py_INCREF(list);
    return list;
}

/*
 * Set resolution and depth for the visualization
 */
static PyObject *
bin_set_resolution(Visual *self, PyObject *args)
{
    /* valid input are width, height, depth or width, height */
    if (!PyArg_ParseTuple(args, "ii",&self->width,&self->height))
        return (PyObject*)NULL;

    /* set the new dimensions */
    visual_video_set_dimension (self->video, self->width, self->height);

    /* negotiate with the actor */
    if (visual_actor_video_negotiate (self->actor, 0, FALSE, FALSE) == -1)
        RAISE(PyExc_Exception, "Actor->video negotiation failed");


    /* create a new screen buffer */
    free(self->scrbuf);
    self->scrbuf = malloc (self->video->size);
    visual_video_set_buffer (self->video, self->scrbuf);

    /* syncronize */
    visual_bin_sync (self->bin, FALSE);

    RETURN_NONE;
}

/*
 * Return the currernt resolution
 */
static PyObject *
bin_get_resolution(Visual *self)
{
    return (PyObject*)Py_BuildValue("ii", self->width, self->height);
}

/*
 * The main polling method
 *  Polls libvisual for updated images.
 *  Returns the image as a string
 */
static PyObject *
bin_run(Visual *self, PyObject *args)
{
     if(visual_bin_run (self->bin) != 0) {
         return RAISE(PyExc_Exception, "Error while updating image");
     }
#ifndef USE_IMLIB2
     return PyBuffer_FromMemory(self->scrbuf, self->video->size);
/*      return PyString_FromStringAndSize(self->scrbuf, self->video->size); */
#else
    Image_PyObject *image;
    Image_PyObject *o;
    image = imlib_create_image_using_copied_data(self->width, self->height, (DATA32*) self->scrbuf);
    o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
    o->image = image;
    return (PyObject *)o;
#endif // USE_IMLIB2
}

/*
 * Sets morphing on the current
 * playing visualization
 * TODO: Make it work
 */
static PyObject *
bin_set_morph(Visual *self, PyObject *args)
{
    RETURN_NONE;
    char *m_name = NULL;
    visual_bin_sync(self->bin, FALSE);

   if (!PyArg_ParseTuple(args, "s",&m_name))
        return (PyObject*)NULL;

    visual_bin_set_morph_by_name (self->bin, m_name);
    visual_bin_switch_set_style (self->bin, VISUAL_SWITCH_STYLE_MORPH);
    visual_bin_switch_set_automatic (self->bin, TRUE);
    /* When automatic is set on TRUE this defines in how many
     * frames the morph should take place */
    visual_bin_switch_set_steps (self->bin, 10);
    visual_bin_switch_actor_by_name (self->bin, self->vis_name);

    RETURN_NONE;
}



/****** Methodes for the class ************************************************/

static PyMethodDef bin_methods[] =
{
{"get_inputs", (PyCFunction)bin_get_input_plugins,         METH_NOARGS },
{"set_input",  (PyCFunction)bin_set_input_plugin,         METH_VARARGS },
{"set_actor",  (PyCFunction)bin_set_visualization_plugin, METH_VARARGS },
{"get_actors", (PyCFunction)bin_get_visualization_plugins, METH_NOARGS },
{"get_next_actor",(PyCFunction)bin_get_next_visualization_plugin,METH_NOARGS},
{"get_morphs", (PyCFunction)bin_get_morph_plugins,         METH_NOARGS },
{"set_size",   (PyCFunction)bin_set_resolution,        METH_VARARGS },
{"get_size",   (PyCFunction)bin_get_resolution,         METH_NOARGS },
{"set_morph",  (PyCFunction)bin_set_morph,          METH_VARARGS },
{"run",        (PyCFunction)bin_run,                 METH_VARARGS },
{ NULL }
};



static PyTypeObject VisualType =
{
    PyObject_HEAD_INIT(NULL)
    0,                              /*ob_size*/
    "bin",                          /*tp_name*/
    sizeof(Visual),                 /*tp_basicsize*/
    0,                              /*tp_itemsize*/
    (destructor)bin_dealloc,        /*tp_dealloc*/
    0,                              /*tp_print*/
    0,                              /*tp_getattr*/
    0,                              /*tp_setattr*/
    0,                              /*tp_compare*/
    0,                              /*tp_repr*/
    0,                              /*tp_as_number*/
    0,                              /*tp_as_sequence*/
    0,                              /*tp_as_mapping*/
    0,                              /*tp_hash */
    0,                              /*tp_call*/
    0,                              /*tp_str*/
    0,                              /*tp_getattro*/
    0,                              /*tp_setattro*/
    0,                              /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,             // | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    "visual objects",               /* tp_doc */
    0,                              /* tp_traverse */
    0,                              /* tp_clear */
    0,                              /* tp_richcompare */
    0,                              /* tp_weaklistoffset */
    0,                              /* tp_iter */
    0,                              /* tp_iternext */
    bin_methods,                    /* tp_methods */
    0,                              /* tp_members */
    0,                              /* tp_getset */
    0,                              /* tp_base */
    0,                              /* tp_dict */
    0,                              /* tp_descr_get */
    0,                              /* tp_descr_set */
    0,                              /* tp_dictoffset */
    (initproc)bin_init,             /* tp_init */
    0,                              /* tp_alloc */
    0,                              /* tp_new */
};

static PyMethodDef visualization_methods[] =
{
    {NULL}  /* Sentinel */
};



#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

PyMODINIT_FUNC
initlibvisual(void)
{
   PyObject* m;
   VisualType.tp_new = PyType_GenericNew;

    if (PyType_Ready(&VisualType) < 0) {
        return;
    }

    m = Py_InitModule3("libvisual", visualization_methods,
                       "libvisual module.");

    if (m == NULL) {
      return;
    }

    Py_INCREF(&VisualType);
    PyModule_AddObject(m, "bin", (PyObject *)&VisualType);
    visual_init(NULL, NULL);
}
