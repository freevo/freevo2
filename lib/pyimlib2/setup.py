from distutils.core import setup, Extension
setup(name="_Imlib2", version="0.0.7", 
	ext_modules=[ 
		Extension("_Imlib2module", 
			["imlib2.c", "image.c", "font.c", "rawformats.c",
			 "display.c"],
			library_dirs=["/usr/X11R6/lib"],
			libraries=["Imlib2", "rt", "X11"])
	],
	py_modules=["Imlib2"]
)

# vim: ts=4
