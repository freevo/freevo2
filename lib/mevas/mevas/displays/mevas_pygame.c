#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>
#include <pygame.h>


PyTypeObject *Image_PyObject_Type;
Imlib_Image (*imlib_image_from_pyobject)(PyObject *pyimg);

PyObject *image_to_surface(PyObject *self, PyObject *args)
{
	PyObject *pyimg;
	Imlib_Image *img;
	PySurfaceObject *pysurf;
	unsigned char *pixels;

	static int init = 0;

	if (init == 0) {
		import_pygame_surface();
		init = 1;
	}

	if (!PyArg_ParseTuple(args, "O!O!", Image_PyObject_Type, &pyimg, &PySurface_Type, &pysurf))
        return NULL;

	img  = imlib_image_from_pyobject(pyimg);
	imlib_context_set_image(img);
	pixels = (unsigned char *)imlib_image_get_data_for_reading_only();
	memcpy(pysurf->surf->pixels, pixels, imlib_image_get_width() * imlib_image_get_height() * 4);

	Py_INCREF(Py_None);
	return Py_None;

} 


PyMethodDef Imlib2_methods[] = {
    { "image_to_surface", image_to_surface, METH_VARARGS }, 
    { NULL }
};

void initmevas_pygame()
{
    PyObject *m, *pyimlib2_module, *c_api;
    void **api_ptrs;
    m = Py_InitModule("mevas_pygame", Imlib2_methods);

    pyimlib2_module = PyImport_ImportModule("_Imlib2");
    if (pyimlib2_module == NULL)
       return;

    c_api = PyObject_GetAttrString(pyimlib2_module, "_C_API");
    if (c_api == NULL || !PyCObject_Check(c_api))
	   return;
    api_ptrs = (void **)PyCObject_AsVoidPtr(c_api);
    Py_DECREF(c_api);
    imlib_image_from_pyobject = api_ptrs[0];
	Image_PyObject_Type = api_ptrs[1];
}
