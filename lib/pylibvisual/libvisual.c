/*
 * Basic libvisual functionality module for Freevo.
 * Authored by: Viggo Fredriksen <viggo@katatonic.org> 2004
 * Released under LGPL.
 * -----------------------------------------------------------------------------
 * TODO:
 *  - Add morphing for changing between plugins
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
    visual_video_free_buffer( self->video );
    visual_object_unref( (VisObject*)self->video );
    visual_object_unref( (VisObject*)self->bin   );
    visual_quit();

    PyMem_DEL(self);
}

/*
 * Type init method
 */
static int
bin_init(Visual *self, PyObject *args, PyObject *kwds)
{
    visual_init(NULL, NULL);
    visual_log_set_verboseness(VISUAL_LOG_VERBOSENESS_NONE);

    // Default values
    self->depth         = 24;
    self->changed_input = 0;
    self->changed_actor = 0;
    self->changed_res   = 0;

    // Create the video and bin containers
    self->video = visual_video_new();   
    self->bin   = visual_bin_new();

    visual_bin_set_video(self->bin, self->video);
    visual_bin_set_depth(self->bin,             VISUAL_VIDEO_DEPTH_24BIT);
    visual_bin_set_supported_depth(self->bin,   VISUAL_VIDEO_DEPTH_24BIT);
    visual_video_set_depth (self->video,        VISUAL_VIDEO_DEPTH_24BIT);
    return 0;
}


/* ***** Python Methods *******************************************************/

/*
 * Set log verbosity
 */
static PyObject *
bin_set_log_verboseness(Visual *self, PyObject *args) {
    int verbosity = -1;

    if (!PyArg_ParseTuple(args, "i", &verbosity))
        return (PyObject*) NULL;

    switch(verbosity) {
        case 0:
           visual_log_set_verboseness(VISUAL_LOG_VERBOSENESS_NONE);
           break;
        case 1:
           visual_log_set_verboseness(VISUAL_LOG_VERBOSENESS_LOW);
           break;
        case 2:
           visual_log_set_verboseness(VISUAL_LOG_VERBOSENESS_MEDIUM);
           break;
        default:
           visual_log_set_verboseness(VISUAL_LOG_VERBOSENESS_HIGH);
           break;
    }


    RETURN_NONE;
}


/*
 * Set next actor
 */
static PyObject *
bin_set_nextactor(Visual *self, PyObject *args) {
    char* name = NULL;

    if (!PyArg_ParseTuple(args, "s", &name))
        return (PyObject*) NULL;

    if (visual_actor_valid_by_name(name) == 0)
        RAISE(PyExc_Exception, "Invalid actor name");

    self->changed_actor = 1;
    self->actor_name = name;

    RETURN_NONE;
}



/*
 * Set next input
 */
static PyObject *
bin_set_nextinput(Visual *self, PyObject *args) {
    char* name = NULL;

    if (!PyArg_ParseTuple(args, "s", &name))
        return (PyObject*) NULL;

    if (visual_input_valid_by_name(name) == 0) {
        RAISE(PyExc_Exception, "Invalid input name");
    }

    self->changed_input = 1;
    self->input_name = name;

    RETURN_NONE;
}


/*
 * Set next resolution
 */
static PyObject *
bin_set_nextresolution(Visual *self, PyObject *args) {
    int w = -1;
    int h = -1;

    /* valid input are width, height */
    if (!PyArg_ParseTuple(args, "ii", &w, &h))
        RAISE(PyExc_Exception, "Invalid argumets");
    self->width = w;
    self->height = h;
    self->changed_res = 1;


    RETURN_NONE;
}


/*
 * Syncs all changes
 */
static PyObject *
bin_sync(Visual *self) {

    VisActor* actor = NULL;
    VisInput* input = NULL;
    

    if(self->bin == NULL) {
        RAISE(PyExc_Exception, "Libvisual has not been initialized");
    }


    // resolution has changed
    if(self->changed_res == 1) {
        //printf("changing res\n");
        // Check if the user given depth is sane 
        VisVideoDepth dpt = visual_video_depth_enum_from_value(self->depth);
        if (visual_video_depth_is_sane (dpt) == 0)
           RAISE(PyExc_Exception, "Invalid depth given");
        visual_video_set_depth (self->video, dpt);

        visual_video_set_dimension (self->video, self->width, self->height);
    }

    // input has changed
    if(self->changed_input == 1) {
        //printf("setting input\n");

        // destroy the object
        if(self->bin->input != NULL) {
            //printf("Destroying input\n");
            visual_object_unref((VisObject*)self->bin->input);        
        }

        input = visual_input_new(self->input_name);
        visual_input_realize(input);
        visual_bin_set_input(self->bin, input);
    }

    // actor has changed
    if(self->changed_actor == 1) {
        //printf("Changing actor\n");

        // destroy the object
        if(self->bin->actor != NULL) {
            //printf("Destroying actor\n");
            visual_object_unref((VisObject*)self->bin->actor);
        }

        actor = visual_actor_new(self->actor_name);
        visual_actor_realize(actor);
        visual_actor_set_video(actor, self->video);
        visual_bin_set_actor(self->bin, actor);
    }


    // negotiate actor video
    if(self->changed_actor || self->changed_res) {
        //printf("negotiate\n");
        if (visual_actor_video_negotiate (self->bin->actor, 0, FALSE, FALSE) != VISUAL_OK)
            RAISE(PyExc_Exception, "Actor->video negotiation failed");
    
        // TODO: check if this is the correct place
        if(self->changed_res) {
             // create the video buffer
             visual_video_allocate_buffer(self->video);
        }
    }


    // reset changes
    self->changed_actor = 0;
    self->changed_input = 0;
    self->changed_res   = 0;

    // syncronize the bin
    visual_bin_sync(self->bin, FALSE);
 
    RETURN_NONE;
}



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
 * Get visualization plugin names
 */
static PyObject *
bin_get_actors(Visual *self)
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
     
     return PyBuffer_FromMemory(self->video->pixels, self->video->size);
}


/****** Methodes for the class ************************************************/

static PyMethodDef bin_methods[] =
{
{"get_inputs", (PyCFunction)bin_get_input_plugins,          METH_NOARGS },
{"set_input",  (PyCFunction)bin_set_nextinput,              METH_VARARGS },
{"set_actor",  (PyCFunction)bin_set_nextactor,              METH_VARARGS },
{"get_actors", (PyCFunction)bin_get_actors,                 METH_NOARGS },
{"set_size",   (PyCFunction)bin_set_nextresolution,         METH_VARARGS },
{"get_size",   (PyCFunction)bin_get_resolution,             METH_NOARGS },
{"get_frame",  (PyCFunction)bin_run,                        METH_NOARGS },
{"sync",       (PyCFunction)bin_sync,                       METH_NOARGS },
{"set_log_verboseness",   (PyCFunction)bin_set_log_verboseness,  METH_VARARGS },
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
}
