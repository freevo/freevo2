/* Code taken from epsilon (http://www.enlightenment.org) */
#include <png.h>

#define X_DISPLAY_MISSING
#include <Imlib2.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdlib.h>

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

int _png_write (const char *file, DATA32 * ptr, int tw, int th, int sw,
		int sh, char *imformat, int mtime, char *uri)
{
  FILE *fp = NULL;
  // Big enough to hold 64 bit integer plus NULL.
  char mtimebuf[21], widthbuf[21], heightbuf[21];
  int i, j, k, has_alpha = 1, ret = 0;

  png_infop info_ptr;
  png_color_8 sig_bit;
  png_structp png_ptr;
  png_text text_ptr[5];
  png_bytep row_ptr, row_data = NULL;

  if ((fp = fopen (file, "wb"))) {
      if (!
	  (png_ptr =
	   png_create_write_struct (PNG_LIBPNG_VER_STRING, NULL, NULL, NULL)))
	{
	  ret = 1;
	}
      if (!(info_ptr = png_create_info_struct (png_ptr)))
	{
	  png_destroy_write_struct (&png_ptr, (png_infopp) NULL);
	  ret = 1;
	}
      if (setjmp (png_ptr->jmpbuf))
	{
	  png_destroy_write_struct (&png_ptr, &info_ptr);
	  ret = 1;
	}

      png_init_io (png_ptr, fp);

      /* setup tags here */
      text_ptr[0].key = "Thumb::URI";
      text_ptr[0].text = uri;
      text_ptr[0].compression = PNG_TEXT_COMPRESSION_NONE;

      snprintf (mtimebuf, sizeof(mtimebuf), "%d", mtime);
      text_ptr[1].key = "Thumb::MTime";
      text_ptr[1].text = mtimebuf;
      text_ptr[1].compression = PNG_TEXT_COMPRESSION_NONE;

      snprintf (widthbuf, sizeof(widthbuf), "%d", sw);
      text_ptr[2].key = "Thumb::Image::Width";
      text_ptr[2].text = widthbuf;
      text_ptr[2].compression = PNG_TEXT_COMPRESSION_NONE;

      snprintf (heightbuf, sizeof(heightbuf), "%d", sh);
      text_ptr[3].key = "Thumb::Image::Height";
      text_ptr[3].text = heightbuf;
      text_ptr[3].compression = PNG_TEXT_COMPRESSION_NONE;

      text_ptr[4].key = "Thumb::Mimetype";
      text_ptr[4].text = imformat;
      text_ptr[4].compression = PNG_TEXT_COMPRESSION_NONE;

      png_set_text (png_ptr, info_ptr, text_ptr, 5);

      if (has_alpha) {
	  png_set_IHDR (png_ptr, info_ptr, tw, th, 8,
			PNG_COLOR_TYPE_RGB_ALPHA, PNG_INTERLACE_NONE,
			PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
#ifdef WORDS_BIGENDIAN
	  png_set_swap_alpha (png_ptr);
#else
	  png_set_bgr (png_ptr);
#endif
      } else {
	  png_set_IHDR (png_ptr, info_ptr, tw, th, 8,
			PNG_COLOR_TYPE_RGB, PNG_INTERLACE_NONE,
			PNG_COMPRESSION_TYPE_BASE, PNG_FILTER_TYPE_BASE);
	  row_data = (png_bytep) malloc (tw * 3 * sizeof (char));
      }

      sig_bit.red = 8;
      sig_bit.green = 8;
      sig_bit.blue = 8;
      sig_bit.alpha = 8;
      png_set_sBIT (png_ptr, info_ptr, &sig_bit);

      png_set_compression_level (png_ptr, 9);	/* 0?? ### */
      png_write_info (png_ptr, info_ptr);
      png_set_shift (png_ptr, &sig_bit);
      png_set_packing (png_ptr);

      for (i = 0; i < th; i++)
	{
	  if (has_alpha)
	    row_ptr = (png_bytep) ptr;
	  else
	    {
	      for (j = 0, k = 0; j < tw; k++)
		{
		  row_data[j++] = (ptr[k] >> 16) & 0xff;
		  row_data[j++] = (ptr[k] >> 8) & 0xff;
		  row_data[j++] = (ptr[k]) & 0xff;
		}
	      row_ptr = (png_bytep) row_data;
	    }
	  png_write_row (png_ptr, row_ptr);
	  ptr += tw;
	}

      png_write_end (png_ptr, info_ptr);
      png_destroy_write_struct (&png_ptr, &info_ptr);
      png_destroy_info_struct (png_ptr, &info_ptr);

      ret = 1;
  }
  else
      printf ("pyimlib2: Unable to open \"%s\" for writing\n", file);

  fflush (fp);
  if (fp)
      fclose (fp);
  if (row_data)
      free (row_data);

  return (ret);
}
