/* Imlib2 module for python.
   Written by Jason Tackaberry <tack@sault.org> and released under the LGPL.

   This is a quick hack.  It is not complete.
   See Imlib2.py for usage details.
*/

#include <Python.h>
#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include "image.h"
#include "rawformats.h"
#include "font.h"

#include <sys/mman.h>
#include <fcntl.h>

static int _shm_ctr = 0;

PyTypeObject Image_PyObject_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_Imlib2.Image",             /*tp_name*/
    sizeof(Image_PyObject),    /*tp_basicsize*/
    0,                         /*tp_itemsize*/
	(destructor)Image_PyObject__dealloc, /* tp_dealloc */
    0,                         /*tp_print*/
	(getattrfunc)Image_PyObject__getattr, /* tp_getattr */
    0,                         /*tp_setattr*/
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
    "Imlib2 Image Object"           /* tp_doc */
};

void Image_PyObject__dealloc(Image_PyObject *self)
{
	imlib_context_set_image(self->image);
//	fprintf(stderr, "IMLIB free image %s\n", imlib_image_get_filename());
	imlib_free_image();
	PyMem_DEL(self);
}

PyObject *Image_PyObject__clear(PyObject *self, PyObject *args)
{ 
	int x, y, w, h, max_w, max_h, cur_y;
	unsigned char *data;
	

	if (!PyArg_ParseTuple(args, "iiii", &x, &y, &w, &h))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	data = (unsigned char *)imlib_image_get_data();
	max_w = imlib_image_get_width();
	max_h = imlib_image_get_height();
	if (x < 0) x = 0;
	if (y < 0) y = 0;
	if (x+w > max_w) w = max_w-x;
	if (y+h > max_h) h = max_h-y;

	// TODO: make this faster.
	for (cur_y = y; cur_y < y + h; cur_y++)
		memset(&data[cur_y*max_w*4+(x*4)], 0, 4*w);

	imlib_image_put_back_data((DATA32 *)data);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *Image_PyObject__scale(PyObject *self, PyObject *args)
{ 
	int dst_w, dst_h, src_w, src_h;
	Imlib_Image *image;
	Image_PyObject *o;

	if (!PyArg_ParseTuple(args, "ii", &dst_w, &dst_h))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	src_w = imlib_image_get_width();
	src_h = imlib_image_get_height();
	image = imlib_create_cropped_scaled_image(0, 0, src_w, src_h, dst_w, dst_h);
	if (!image) {
		PyErr_Format(PyExc_RuntimeError, "Failed scaling image (%d, %d)", dst_w, dst_h);
		return NULL;
	}
	
	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;
}

PyObject *Image_PyObject__crop(PyObject *self, PyObject *args)
{ 
	int x, y, w, h, src_w, src_h;
	Imlib_Image *image;
	Image_PyObject *o;

	if (!PyArg_ParseTuple(args, "iiii", &x, &y, &w, &h))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	src_w = imlib_image_get_width();
	src_h = imlib_image_get_height();
	if (w > src_w) w = src_w;
	if (h > src_h) h = src_h;
	if (x > src_w) x = 0;
	if (y > src_h) y = 0;

	// Errmm, why imlib_Create_cropped_image terribly broken?
	//image = imlib_create_cropped_image(x, y, w, h);

	image = imlib_create_cropped_scaled_image(x, y, w, h, w, h);
	if (!image) {
		PyErr_Format(PyExc_RuntimeError, "Failed cropping image (%d, %d), (%d, %d)", x, y, w, h);
		return NULL;
	}
	
	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;
}

PyObject *Image_PyObject__rotate(PyObject *self, PyObject *args)
{ 
	Imlib_Image *image;
	Image_PyObject *o;
	double angle;

	if (!PyArg_ParseTuple(args, "d", &angle))
		return NULL;

	fprintf(stderr, "Rotate image by %f\n", angle);
	imlib_context_set_image(((Image_PyObject *)self)->image);

	image = imlib_create_rotated_image(angle);
	if (!image) {
		PyErr_Format(PyExc_RuntimeError, "Failed rotating image (%f) degrees", angle);
		return NULL;
	}
	
	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;
}

PyObject *Image_PyObject__clone(PyObject *self, PyObject *args)
{ 
	int dst_w, dst_h, src_w, src_h;
	Imlib_Image *image;
	Image_PyObject *o;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	image = imlib_clone_image();
	if (!image) {
		PyErr_Format(PyExc_RuntimeError, "Failed to clone image");
		return NULL;
	}
	
	o = PyObject_NEW(Image_PyObject, &Image_PyObject_Type);
	o->image = image;
	return (PyObject *)o;
}


PyObject *Image_PyObject__blend(PyObject *self, PyObject *args)
{ 
	int dst_x, dst_y, src_alpha = 255, merge_alpha = 1,
	    src_w, src_h, src_x = 0, src_y = 0;
	Image_PyObject *src;
	Imlib_Image *src_img;
	Imlib_Color_Modifier cmod;

	if (!PyArg_ParseTuple(args, "O!(ii)(ii)(ii)ii", &Image_PyObject_Type, &src, &dst_x, &dst_y, &src_x, &src_y, &src_w, &src_h, &src_alpha, &merge_alpha))
		return NULL;

	Py_INCREF(Py_None);

	if (src_alpha == 0)
		return Py_None;

	src_img = ((Image_PyObject *)src)->image;

	// This yields incorrect results.  We would need to duplicate
	// the image and apply the color modifer to it for this to
	// have the correct result, but that's actually slower than the
	// above code.
	if (src_alpha < 255) {
		unsigned char a[256], linear[256];
		int i;
		for (i = 0; i < 256; i++) {
			int temp = (i * src_alpha) + 0x80;
			a[i] = ((temp + (temp >> 8)) >> 8);
			linear[i] = i;
		}
		cmod = imlib_create_color_modifier();
		imlib_context_set_color_modifier(cmod);
		imlib_set_color_modifier_tables(linear, linear, linear, a);
	}

	imlib_context_set_image(((Image_PyObject *)self)->image);

//	imlib_context_set_operation(IMLIB_OP_SUBTRACT);
	imlib_context_set_blend( src_alpha == 256 ? 0 : 1);
	imlib_blend_image_onto_image(src_img, merge_alpha, src_x, src_y, 
			src_w, src_h, dst_x, dst_y,
			src_w, src_h);
	imlib_context_set_blend(1);
	imlib_context_set_color_modifier(NULL);

	return Py_None;
}

PyObject *Image_PyObject__draw_mask(PyObject *self, PyObject *args)
{ 
	int dst_x, dst_y, mask_w, mask_h, dst_w, dst_h;
	Image_PyObject *mask;
	unsigned long xpos, ypos, dst_pos, mask_pos;
	unsigned char *dst_data, *mask_data;

	if (!PyArg_ParseTuple(args, "O!ii", &Image_PyObject_Type, &mask, &dst_x, &dst_y))
		return NULL;

	Py_INCREF(Py_None);

	imlib_context_set_image(((Image_PyObject *)mask)->image);
	mask_w = imlib_image_get_width();
	mask_h = imlib_image_get_height();
	mask_data = (unsigned char *)imlib_image_get_data_for_reading_only();

	imlib_context_set_image(((Image_PyObject *)self)->image);
	dst_w = imlib_image_get_width();
	dst_h = imlib_image_get_height();
	dst_data = (unsigned char *)imlib_image_get_data();

	// Use the passed image as a mask.  Again, no obvious way to do this in
	// Imlib natively.
	for (ypos = 0; ypos < mask_h; ypos++) {
		if (ypos + dst_y >= dst_h) break;
		for (xpos = 0; xpos < mask_w; xpos++) {
			if (xpos + dst_x >= dst_w) break;
			mask_pos = (xpos << 2) + (ypos * mask_w << 2);
			dst_pos = ((dst_x + xpos) << 2) + ((dst_y + ypos) * dst_w << 2);
			
			unsigned char *mask_chunk = &mask_data[mask_pos],
			              *dst_chunk = &dst_data[dst_pos],
			              // Any way to optimize this?
			              avg = (mask_chunk[0] + mask_chunk[1] + mask_chunk[2]) / 3;

			// Blend average (grayscale) pixel from the mask with the alpha channel of the image
			int temp = (dst_chunk[3] * avg) + 0x80;
			dst_chunk[3] = ((temp + (temp >> 8)) >> 8);
			dst_chunk[3] = dst_chunk[3] >> 1;
		}
	}
	imlib_image_put_back_data((DATA32 *)dst_data);
			
	return Py_None;
}

PyObject *Image_PyObject__draw_text(PyObject *self, PyObject *args)
{ 
	int x, y, w, h, advance_w, advance_h, r, g, b, a, descent, inset;
	char *text;
	Font_PyObject *font;

	if (!PyArg_ParseTuple(args, "O!iis(iiii)", &Font_PyObject_Type, &font, &x, &y, &text, &r, &g, &b, &a))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	imlib_context_set_font(((Font_PyObject *)font)->font);
	
	imlib_context_set_color(r, g, b, a);
	//descent = imlib_get_maximum_font_descent();
	//inset = imlib_get_text_inset(text);
//	y = y + descent + inset + 2;
	//printf("TEXT INSET: %d ASC %d  DESC %d\n", imlib_get_text_inset(text), imlib_get_font_ascent(), imlib_get_font_descent());
	imlib_text_draw_with_return_metrics(x, y, text, &w, &h, &advance_w, &advance_h);
	return Py_BuildValue("(llll)", w, h, advance_w, advance_h);
}

PyObject *Image_PyObject__draw_rectangle(PyObject *self, PyObject *args)
{ 
	int x, y, w, h, r, g, b, a, fill = 0;

	if (!PyArg_ParseTuple(args, "iiii(iiii)|i", &x, &y, &w, &h, &r, &g, &b, &a, &fill))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	imlib_image_set_has_alpha(1);
//	imlib_context_set_operation(IMLIB_OP_SUBTRACT);
	imlib_context_set_color(r, g, b, a);
	if (!fill)
		imlib_image_draw_rectangle(x, y, w, h);
	else
		imlib_image_fill_rectangle(x, y, w, h);

//	imlib_image_set_has_alpha(1);
	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *Image_PyObject__draw_ellipse(PyObject *self, PyObject *args)
{ 
	int xc, yc, ea, eb, r, g, b, a, fill = 0;

	if (!PyArg_ParseTuple(args, "iiii(iiii)|i", &xc, &yc, &ea, &eb, &r, &g, &b, &a, &fill))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	imlib_context_set_color(r, g, b, a);
	imlib_context_set_anti_alias(1);
	if (!fill)
		imlib_image_draw_ellipse(xc, yc, ea, eb);
	else
		imlib_image_fill_ellipse(xc, yc, ea, eb);

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *Image_PyObject__copy_rect(PyObject *self, PyObject *args)
{ 
	int src_x, src_y, w, h, dst_x, dst_y;
	if (!PyArg_ParseTuple(args, "(ii)(ii)(ii)", &src_x, &src_y, &w, &h, &dst_x, &dst_y))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	imlib_image_copy_rect(src_x, src_y, w, h, dst_x, dst_y);
	Py_INCREF(Py_None);
	return Py_None;
}


PyObject *Image_PyObject__move_to_shmem(PyObject *self, PyObject *args)
{
	char *shmem_name, *buf, *format = "BGRA";
	unsigned long size, w, h;
	int fd;

	if (!PyArg_ParseTuple(args, "|ss", &format, &shmem_name))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	size = get_raw_bytes_size(format);

	fd = shm_open(shmem_name, O_RDWR|O_CREAT, 0777);
	if (fd == -1) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	ftruncate(fd, size);
	buf = mmap(0, size, PROT_READ|PROT_WRITE, MAP_SHARED, fd, 0);
	if (!buf)
		return NULL;

	get_raw_bytes(format, buf);

	// FIXME: need some error checking here.

	close(fd);
	munmap(buf, size);
	return Py_BuildValue("s", shmem_name);
}

PyObject *Image_PyObject__get_bytes(PyObject *self, PyObject *args)
{
	unsigned char *format = "BGRA", *buffer;
	unsigned long size, w, h;
	PyObject *ret;

	if (!PyArg_ParseTuple(args, "|s", &format))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	size = get_raw_bytes_size(format);
	if (!strcmp(format, "BGRA")) {
		unsigned char *bytes = imlib_image_get_data_for_reading_only();
		// Imlib2 docs say we're not supposed to do this.  It seems to
		// work though. :)
		ret = PyBuffer_FromReadWriteMemory(bytes, size);
		return Py_BuildValue("(Ol)", ret, 0);
	}
	buffer = get_raw_bytes(format, NULL);
	ret = PyBuffer_FromMemory(buffer, size);

	// XXX: WARNING!  This function creates a buffer from memory allocated
	// by get_raw_bytes().  It's the responsibility of the wrapper to
	// free this buffer by calling _Imlib2.free_buffer().
	return Py_BuildValue("(Ol)", ret, buffer);
}

////////////////////////////////////////////////////////////////////////////


PyObject *Image_PyObject__save(PyObject *self, PyObject *args)
{
	unsigned char *filename;

	if (!PyArg_ParseTuple(args, "s", &filename))
		return NULL;

	imlib_context_set_image(((Image_PyObject *)self)->image);
	// TODO: call imlib_save_image_with_error_return
	imlib_save_image(filename);
	Py_INCREF(Py_None);
	return Py_None;
}
PyMethodDef Image_PyObject_methods[] = {
	{ "draw_rectangle", Image_PyObject__draw_rectangle, METH_VARARGS },
	{ "draw_ellipse", Image_PyObject__draw_ellipse, METH_VARARGS },
	{ "draw_text", Image_PyObject__draw_text, METH_VARARGS },
	{ "draw_mask", Image_PyObject__draw_mask, METH_VARARGS },
	{ "clear", Image_PyObject__clear, METH_VARARGS },
	{ "copy_rect", Image_PyObject__copy_rect, METH_VARARGS },
	{ "clone", Image_PyObject__clone, METH_VARARGS },
	{ "scale", Image_PyObject__scale, METH_VARARGS },
	{ "crop", Image_PyObject__crop, METH_VARARGS },
	{ "rotate", Image_PyObject__rotate, METH_VARARGS },
	{ "blend", Image_PyObject__blend, METH_VARARGS },
	{ "move_to_shmem", Image_PyObject__move_to_shmem, METH_VARARGS },
	{ "get_bytes", Image_PyObject__get_bytes, METH_VARARGS },
	{ "save", Image_PyObject__save, METH_VARARGS },
	{ NULL, NULL }
};

PyObject *Image_PyObject__getattr(Image_PyObject *self, char *name)
{
	imlib_context_set_image(self->image);
	if (!strcmp(name, "width"))
		return Py_BuildValue("l", imlib_image_get_width());
	else if (!strcmp(name, "height"))
		return Py_BuildValue("l", imlib_image_get_height());
	else if (!strcmp(name, "format"))
		return Py_BuildValue("s", imlib_image_format());
	else if (!strcmp(name, "mode"))
		return Py_BuildValue("s", "BGRA");
	else if (!strcmp(name, "filename"))
		return Py_BuildValue("s", imlib_image_get_filename());

	return Py_FindMethod(Image_PyObject_methods, (PyObject *)self, name);
}

// vim: ts=4
