#define X_DISPLAY_MISSING
#include <Imlib2.h>
#include <string.h>


/* RGB to YUV conversion tables pulled from speedy.c in tvtime.  Here
 * are the copyright notices on that file:
 *
 *   Copyright (c) 2002, 2003 Billy Biggs <vektor@dumbterm.net>.
 *   Copyright (C) 2001 Matthew J. Marjanovic <maddog@mir.com>
 *
 * Lookup tables is not that much faster than doing the (integer)
 * arithmetic in the inner loop (7% by my calculations), but it is
 * presumably more correct and hey, 7% isn't that bad. :)
 */

#define rgb2y(R,G,B) ( (Y_R[ r ] + Y_G[ g ] + Y_B[ b ]) >> FP_BITS )
#define rgb2u(R,G,B) ( (U_R[ r ] + U_G[ g ] + U_B[ b ]) >> FP_BITS )
#define rgb2v(R,G,B) ( (V_R[ r ] + V_G[ g ] + V_B[ b ]) >> FP_BITS )
#define FP_BITS 18
static int Y_R[256], Y_G[256], Y_B[256],
           U_R[256], U_G[256], U_B[256],
           V_R[256], V_G[256], V_B[256];


static int 
myround(double n)
{
	if (n >= 0) return (int)(n + 0.5);
	else return (int)(n - 0.5);
}

void
init_rgb2yuv_tables()
{
	int i;
	for (i = 0; i < 256; i++) {
		Y_R[i] = myround(0.299 * (double)i * 219.0 / 255.0 * (double)(1<<FP_BITS));
		Y_G[i] = myround(0.587 * (double)i * 219.0 / 255.0 * (double)(1<<FP_BITS));
		Y_B[i] = myround((0.114 * (double)i * 219.0 / 255.0 * (double)(1<<FP_BITS)) + (double)(1<<(FP_BITS-1)) + (16.0 * (double)(1<<FP_BITS)));
                                                                                
		U_R[i] = myround(-0.168736 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS));
		U_G[i] = myround(-0.331264 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS));
		U_B[i] = myround((0.500 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS)) + (double)(1<<(FP_BITS-1)) + (128.0 * (double)(1<<FP_BITS))); 

		V_R[i] = myround(0.500 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS));
		V_G[i] = myround(-0.418688 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS));
		V_B[i] = myround((-0.081312 * (double)i * 224.0 / 255.0 * (double)(1<<FP_BITS)) + (double)(1<<(FP_BITS-1)) + (128.0 * (double)(1<<FP_BITS))); 
	}

}

// End of code ripped off from speedy.c :)
///////////////////////////////////////////////////////////////////////

unsigned int
get_raw_bytes_size(char *format)
{
	unsigned int w = imlib_image_get_width(),
	             h = imlib_image_get_height();
	
	if (!strcmp(format, "YV12A"))
		return w * h * 2 + ((w * h / 4) * 2);
	else if (!strcmp(format, "YV12"))
		return w * h + ((w * h / 4) * 2);
	else 
		// assume combination of RGBA or RGB
		return w * h * strlen(format);
}


unsigned char *
convert_raw_rgba_bytes(char *from_format, char *to_format,
                  unsigned char *from_buf, unsigned char *to_buf,
                  int w, int h)
{
	int from_bpp, to_bpp, i;
	unsigned char fr, fb, fg, fa, tr, tb, tg, ta, *from_ptr, *to_ptr;
	from_bpp = strlen(from_format);
	to_bpp = strlen(to_format);

	if (to_buf == 0)
		to_buf = (unsigned char *)malloc(w*h*to_bpp);


#define LOOP_START \
	for (from_ptr = from_buf, to_ptr = to_buf; from_ptr < from_buf + w*h*from_bpp; from_ptr += from_bpp)


	// FIXME: pointless code duplication follows.

	/* Hard code the common cases of BGRA -> RGB/A.  This is pretty much
	 * as fast as memcpy.  I don't think it gets much faster without
	 * MMX.
	 */
	if (!strcmp(from_format, "BGRA") && !strcmp(to_format, "RGB")) {
		LOOP_START {
			*(to_ptr++) = *(from_ptr + 2); *(to_ptr++) = *(from_ptr + 1);
			*(to_ptr++) = *(from_ptr + 0);
		}
	return to_buf;
	} 
	if (!strcmp(from_format, "BGRA") && !strcmp(to_format, "RGBA")) {
		LOOP_START {
			*(to_ptr++) = *(from_ptr + 2); *(to_ptr++) = *(from_ptr + 1);
			*(to_ptr++) = *(from_ptr + 0); *(to_ptr++) = *(from_ptr + 3);
		}
	return to_buf;
	} 


	for (i = 0; i < to_bpp; i ++) {
		if (to_format[i] == 'R') tr = i;
		else if (to_format[i] == 'G') tg = i;
		else if (to_format[i] == 'B') tb = i;
		else if (to_format[i] == 'A') ta = i;
	}
	for (i = 0; i < from_bpp; i ++) {
		if (from_format[i] == 'R') fr = i;
		else if (from_format[i] == 'G') fg = i;
		else if (from_format[i] == 'B') fb = i;
		else if (from_format[i] == 'A') fa = i;
	}

	LOOP_START {
		*(to_ptr + tr) = *(from_ptr + fr);
		*(to_ptr + tg) = *(from_ptr + fg);
		*(to_ptr + tb) = *(from_ptr + fb);
		if (to_bpp == 4) 
			*(to_ptr + ta) = (from_bpp==4)?*(from_ptr + fa):255;

		to_ptr += to_bpp;
	} 
	return to_buf;
}


/* Convert the imlib data (which is BGRA) to planar YV12 plus an
   8bpp alpha plane.  This function is ugly but it should be
   reasonably tight.
*/
unsigned char *_get_yv12_image(int w, int h, unsigned char *srcbuf,
                               unsigned char *dstbuf)
{
	unsigned char *src_ptr, *y_ptr, *u_ptr, *v_ptr, *a_ptr;
	unsigned char r, g, b, a, Ar, Ab, Ag;
	int pos;

	y_ptr = dstbuf;	        pos = w * h;
	u_ptr = dstbuf + pos;   pos += (w * h) / 4;
	v_ptr = dstbuf + pos;   pos += (w * h) / 4;
	a_ptr = dstbuf + pos;

	int stride = w*4;
	// Calculate luma plane
	for (src_ptr = srcbuf; src_ptr < srcbuf + stride*h;) {
		b = *(src_ptr++); g = *(src_ptr++); r = *(src_ptr++);
		*(y_ptr++) = rgb2y(r, g, b);
		*(a_ptr++) = *(src_ptr++);
	}

	/* Calculate chroma planes.
	 * This macro nonsense is to handle the case where the image's
	 * width is odd.  We don't want to put the if (image is odd)
	 * comparison in the inner loop since that's pointlessly slow.
	 * Given a block of 2x2 pixels:
	 *    A  B
     *    C  D
     * We calculate the chroma values by averaging the RGB values between
	 * A and C.  This follows MPEG2 spec, and it may not be correct in
	 * all cases but it's a good default.
	 */
 
#define YV12_LOOP(expr) { \
	for (src_ptr = srcbuf + stride; src_ptr < srcbuf-4+stride*h; src_ptr+=4) { \
		Ab = *(src_ptr-stride); Ag = *(src_ptr-stride+1);  \
		Ar = *(src_ptr-stride+2); \
		b = *(src_ptr++); g = *(src_ptr++); r = *(src_ptr++); src_ptr++; \
		r=(r+Ar)>>1; g = (g+Ag)>>1; b = (b+Ab)>>1; \
		*(u_ptr++) = rgb2u(r, g, b); \
		*(v_ptr++) = rgb2v(r, g, b); \
		expr; \
	} }

	if (w & 1)
		YV12_LOOP( if ( (src_ptr-srcbuf) % stride == 0)
				src_ptr += stride+4 )
	else
		YV12_LOOP( if ( ((src_ptr+4)-srcbuf) % stride == 0) src_ptr += stride; )
	return dstbuf;
}


unsigned char *
get_raw_bytes(char *format, unsigned char *dstbuf)
{
	unsigned int w, h, bufsize;
	unsigned char *srcbuf;

	w = imlib_image_get_width(),
	h = imlib_image_get_height(),
	bufsize = get_raw_bytes_size(format);

	imlib_image_set_has_alpha(1);
	srcbuf = (unsigned char *)imlib_image_get_data_for_reading_only();
	if (dstbuf == 0)
		dstbuf = (unsigned char *)malloc(bufsize);
	
	if (!strcmp(format, "YV12A"))
		_get_yv12_image(w, h, srcbuf, dstbuf);
	else if (!strcmp(format, "BGRA"))  {
		memcpy(dstbuf, srcbuf, bufsize);
	}
	else
		dstbuf = convert_raw_rgba_bytes("BGRA", format, srcbuf, dstbuf, w, h);
	return dstbuf;
}

// vim: ts=4
