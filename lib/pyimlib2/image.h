#define Image_PyObject_Check(v) ((v)->ob_type == &Image_PyObject_Type)

extern key_t _imlib2_shm_key;
extern int _imlib2_shm_id;
extern char *_imlib2_shm_buf;

extern key_t _imlib2_sem_key;
extern int _imlib2_sem_id;

typedef struct {
	PyObject_HEAD
	Imlib_Image *image;
} Image_PyObject;

extern PyTypeObject Image_PyObject_Type;
void Image_PyObject__dealloc(Image_PyObject *);
PyObject *Image_PyObject__getattr(Image_PyObject *, char *);

