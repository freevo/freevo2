#define Font_PyObject_Check(v) ((v)->ob_type == &Font_PyObject_Type)

typedef struct {
	PyObject_HEAD
	Imlib_Font *font;
} Font_PyObject;

extern PyTypeObject Font_PyObject_Type;
void Font_PyObject__dealloc(Font_PyObject *);
PyObject *Font_PyObject__getattr(Font_PyObject *, char *);
