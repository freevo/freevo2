/* vf_bmovl.c v0.9.1 - BitMap OVerLay videofilter for MPlayer
 *
 * (C) 2002 Per Wigren <wigren@home.se>
 * Licenced under the GNU General Public License
 *
 * Use MPlayer as a framebuffer to read bitmaps and commands from a FIFO
 * and display them in the window.
 *
 * It understands the following format:
 * COMMAND width height xpos ypos alpha clear
 *
 * Commands are:
 * RGBA32    Followed by WIDTH*HEIGHT of raw RGBA32 data.
 * BGRA32    Followed by WIDTH*HEIGHT of raw BGRA32 data.
 * RGB24     Followed by WIDTH*HEIGHT of raw RGB24 data.
 * ALPHA     Set alpha for area. Values can be -255 to 255.
 *           0 = No change
 * CLEAR     Zero area
 * OPAQUE    Disable all alpha transparency!
 *           Send an ALPHA command with 0's to enable again!
 * HIDE      Hide bitmap
 * SHOW      Show bitmap
 *
 * Arguments are:
 * width, height    Size of image/area
 * xpos, ypos       Start blitting at X/Y position
 * alpha            Set alpha difference. 0 means same as original.
 *                  255 makes everything opaque
 *                  -255 makes everything transparent
 *                  If you set this to -255 you can then send a sequence of
 *                  ALPHA-commands to set the area to -225, -200, -175 etc
 *                  for a nice fade-in-effect! ;)
 * clear            Clear the framebuffer before blitting. 1 means clear.
 *                  If 0, the image will just be blitted on top of the old
 *                  one, so you don't need to send 1,8MB of RGBA32 data
 *                  everytime a small part of the screen is updated.
 *
 * Note that you always have to send all arguments, even if they are not
 * used for a particular command!
 *
 * Arguments for the filter are hidden:opaque:fifo
 * For example 1:0:/tmp/myfifo.fifo will start the filter hidden, transparent
 * and use /tmp/myfifo.fifo as the fifo.
 *
 * If you find bugs, please send me patches! ;)
 *
 * This filter was developed for use in Freevo (http://freevo.sf.net), but
 * anyone is free to use it! ;)
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include "mp_image.h"
#include "vf.h"
#include "img_format.h"

#include "../libvo/fastmemcpy.h"

#define IS_IMG 0x100

#define NONE   0x000
#define RGB24  0x101
#define RGBA32 0x102
#define BGRA32 0x103
#define CLEAR  0x004
#define ALPHA  0x005

#define TRUE  1
#define FALSE 0

#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define MIN(a,b) ((a) < (b) ? (a) : (b))
#define INRANGE(a,b,c)	( ((a) < (b)) ? (b) : ( ((a) > (c)) ? (c) : (a) ) )

#define rgb2y(R,G,B)  (  (0.257 * R) + (0.504 * G) + (0.098 * B) + 16  )
#define rgb2u(R,G,B)  ( -(0.148 * R) - (0.291 * G) + (0.439 * B) + 128 )
#define rgb2v(R,G,B)  (  (0.439 * R) - (0.368 * G) - (0.071 * B) + 128 )

#define DBG(a) (printf("DEBUG: %d\n", a))

struct vf_priv_s {
    int w, h, x1, y1, x2, y2;
	struct {
		unsigned char *y, *u, *v, *a, *oa;
	} bitmap;
    FILE* stream;
    int stream_fd;
	fd_set stream_fdset;
	int opaque, hidden;
};

static int
query_format(struct vf_instance_s* vf, unsigned int fmt){
    if(fmt==IMGFMT_YV12) return VFCAP_CSP_SUPPORTED;
    return 0;
}


static int
config(struct vf_instance_s* vf,
       int width, int height, int d_width, int d_height,
       unsigned int flags, unsigned int outfmt)
{
	vf->priv->bitmap.y  = malloc( width*height );
	vf->priv->bitmap.u  = malloc( width*height/4 );
	vf->priv->bitmap.v  = malloc( width*height/4 );
	vf->priv->bitmap.a  = malloc( width*height );
	vf->priv->bitmap.oa = malloc( width*height );
	if(!( vf->priv->bitmap.y &&
	      vf->priv->bitmap.u &&
		  vf->priv->bitmap.v &&
		  vf->priv->bitmap.a &&
		  vf->priv->bitmap.oa )) {
		fprintf(stderr, "vf_bmovl: Could not allocate memory for bitmap buffer: %s\n", strerror(errno) );
		exit(10);
	}

	// Set default to black...
	memset( vf->priv->bitmap.u, 128, width*height/4 );
	memset( vf->priv->bitmap.v, 128, width*height/4 );

    vf->priv->w  = vf->priv->x1 = width;
    vf->priv->h  = vf->priv->y1 = height;
    vf->priv->y2 = vf->priv->x2 = 0;

    return vf_next_config(vf, width, height, d_width, d_height, flags, outfmt);
}


static int
put_image(struct vf_instance_s* vf, mp_image_t* mpi){
	int buf_x=0, buf_y=0, buf_pos=0;
	int xpos=0, ypos=0, pos=0;
	unsigned char red, green, blue;
	int  alpha;
	mp_image_t* dmpi;

    dmpi = vf_get_image(vf->next, mpi->imgfmt, MP_IMGTYPE_TEMP,
						MP_IMGFLAG_ACCEPT_STRIDE | MP_IMGFLAG_PREFER_ALIGNED_STRIDE,
						mpi->w, mpi->h);

	memcpy( dmpi->planes[0], mpi->planes[0], mpi->stride[0] * mpi->height);
	memcpy( dmpi->planes[1], mpi->planes[1], mpi->stride[1] * mpi->chroma_height);
	memcpy( dmpi->planes[2], mpi->planes[2], mpi->stride[2] * mpi->chroma_height);


    if(vf->priv->stream) {

		struct timeval tv;

		FD_SET( vf->priv->stream_fd, &vf->priv->stream_fdset );
		tv.tv_sec=0; tv.tv_usec=20;

		if( select( vf->priv->stream_fd+1, &vf->priv->stream_fdset, NULL, NULL, &tv ) ) {
			// We've got new data from the FIFO

		    if( feof(vf->priv->stream) ) {
                fprintf(stderr, "\nvf_bmovl: Got feof() on the FIFO\n\n");
		        clearerr(vf->priv->stream);
		    } else if( ferror(vf->priv->stream) ) {
		        fprintf(stderr, "\nvf_bmovl: Error in stream: %s\n", strerror(errno));
		        fprintf(stderr, "vf_bmovl: Closing down...\n\n");
				fclose(vf->priv->stream);
		        vf->priv->stream = NULL;
				vf->priv->hidden = TRUE;
				return vf_next_put_image(vf, dmpi);
		    } else {
				char cmd[1000];
				int  imgw,imgh,imgx,imgy,clear,imgalpha,pxsz,command;
				unsigned char *buffer = NULL;

				fscanf( vf->priv->stream, "%s %d %d %d %d %d %d\n",
                                        cmd, &imgw, &imgh, &imgx, &imgy, &imgalpha, &clear);
//				printf("\nDEBUG: GOT %s %d %d %d %d %d %d\n\n",
//                                        cmd, imgw, imgh, imgx, imgy, imgalpha, clear);

				if     ( strncmp(cmd,"RGBA32",6)==0 ) { pxsz=4; command = RGBA32; }
				else if( strncmp(cmd,"BGRA32",6)==0 ) { pxsz=4; command = BGRA32; }
				else if( strncmp(cmd,"RGB24" ,5)==0 ) { pxsz=3; command = RGB24;  }
				else if( strncmp(cmd,"CLEAR" ,5)==0 ) { pxsz=1; command = CLEAR;  }
				else if( strncmp(cmd,"ALPHA" ,5)==0 ) { pxsz=1; command = ALPHA;  }
				else if( strncmp(cmd,"FLUSH" ,5)==0 ) { return vf_next_put_image(vf, dmpi); }
				else if( strncmp(cmd,"OPAQUE",6)==0 ) {
					vf->priv->opaque=TRUE;
					command = NONE;
				}
				else if( strncmp(cmd,"SHOW",  4)==0 ) {
					vf->priv->hidden=FALSE;
					command = NONE;
				}
				else if( strncmp(cmd,"HIDE",  4)==0 ) {
					vf->priv->hidden=TRUE;
					command = NONE;
				}
				else {
				    fprintf(stderr, "vf_bmovl: Unsupported command: %s. Ignoring.\n", cmd);
				    return vf_next_put_image(vf, dmpi);
				}

				if(command == ALPHA) vf->priv->opaque=FALSE;

				if(command & IS_IMG) {
				    buffer = malloc(imgw*imgh*pxsz +1);
				    if(!buffer) {
				    	fprintf(stderr, "\nvf_bmovl: Couldn't allocate temporary buffer! Skipping...\n\n");
						return vf_next_put_image(vf, dmpi);
				    }
				    fread( buffer, (imgw*pxsz), imgh, vf->priv->stream );
					fscanf( vf->priv->stream, "%c", cmd); // Catch the \n..
					if( ferror(vf->priv->stream) ) {
						printf("\nvf_bmovl: ERROR READING DATA: %s\n\n", strerror(errno));
						exit( 10 );
					}
				}

				if(clear) {
					memset( vf->priv->bitmap.y,   0, vf->priv->w*vf->priv->h );
					memset( vf->priv->bitmap.u, 128, vf->priv->w*vf->priv->h/4 );
					memset( vf->priv->bitmap.v, 128, vf->priv->w*vf->priv->h/4 );
					memset( vf->priv->bitmap.a,   0, vf->priv->w*vf->priv->h );
					memset( vf->priv->bitmap.oa,  0, vf->priv->w*vf->priv->h );
					vf->priv->x1 = dmpi->width;
					vf->priv->y1 = dmpi->height;
					vf->priv->x2 = vf->priv->y2 = 0;
				}

				// Define how much of our bitmap that contains graphics!
				vf->priv->x1 = MAX( 0, MIN(vf->priv->x1, imgx) );
				vf->priv->y1 = MAX( 0, MIN(vf->priv->y1, imgy) );
				vf->priv->x2 = MIN( vf->priv->w, MAX(vf->priv->x2, ( imgx + imgw)) );
				vf->priv->y2 = MIN( vf->priv->h, MAX(vf->priv->y2, ( imgy + imgh)) );
				
				for( buf_y=0 ; (buf_y < imgh) && (buf_y < (vf->priv->h-imgy)) ; buf_y++ ) {
				    for( buf_x=0 ; (buf_x < (imgw*pxsz)) && (buf_x < ((vf->priv->w+imgx)*pxsz)) ; buf_x += pxsz ) {
						if(command & IS_IMG) buf_pos = (buf_y * imgw * pxsz) + buf_x;
						pos = ((buf_y+imgy) * vf->priv->w) + ((buf_x/pxsz)+imgx);

						switch(command) {
							case RGBA32:
								red   = buffer[buf_pos+0];
								green = buffer[buf_pos+1];
								blue  = buffer[buf_pos+2];

								vf->priv->bitmap.y[pos]  = rgb2y(red,green,blue);
								vf->priv->bitmap.a[pos]  = INRANGE((buffer[buf_pos+3]+imgalpha),0,255);
								vf->priv->bitmap.oa[pos] = buffer[buf_pos+3];
								if((buf_y%2) && ((buf_x/pxsz)%2)) {
									pos = ( ((buf_y+imgy)/2) * dmpi->stride[1] ) + (((buf_x/pxsz)+imgx)/2);
									vf->priv->bitmap.u[pos]  = rgb2u(red,green,blue);
									vf->priv->bitmap.v[pos]  = rgb2v(red,green,blue);
								}
								break;
							case BGRA32:
								blue  = buffer[buf_pos+0];
								green = buffer[buf_pos+1];
								red   = buffer[buf_pos+2];

								vf->priv->bitmap.y[pos]  = rgb2y(red,green,blue);
								vf->priv->bitmap.a[pos]  = INRANGE((buffer[buf_pos+3]+imgalpha),0,255);
								vf->priv->bitmap.oa[pos] = buffer[buf_pos+3];
								if((buf_y%2) && ((buf_x/pxsz)%2)) {
									pos = ( ((buf_y+imgy)/2) * dmpi->stride[1] ) + (((buf_x/pxsz)+imgx)/2);
									vf->priv->bitmap.u[pos]  = rgb2u(red,green,blue);
									vf->priv->bitmap.v[pos]  = rgb2v(red,green,blue);
								}
								break;
							case RGB24:
								red   = buffer[buf_pos+0];
								green = buffer[buf_pos+1];
								blue  = buffer[buf_pos+2];

								vf->priv->bitmap.y[pos]  = rgb2y(red,green,blue);
								vf->priv->bitmap.a[pos]  = INRANGE((255+imgalpha),0,255);
								vf->priv->bitmap.oa[pos] = 255;
								if((buf_y%2) && ((buf_x/pxsz)%2)) {
									pos = ( ((buf_y+imgy)/2) * dmpi->stride[1] ) + (((buf_x/pxsz)+imgx)/2);
									vf->priv->bitmap.u[pos]  = rgb2u(red,green,blue);
									vf->priv->bitmap.v[pos]  = rgb2v(red,green,blue);
								}
			    				break;
							case CLEAR:
						        vf->priv->bitmap.y[pos]  = 0;
						        vf->priv->bitmap.a[pos]  = 0;
						        vf->priv->bitmap.oa[pos] = 0;
								if((buf_y%2) && ((buf_x/pxsz)%2)) {
									pos = ( ((buf_y+imgy)/2) * dmpi->stride[1] ) + (((buf_x/pxsz)+imgx)/2);
							        vf->priv->bitmap.u[pos]  = 0;
							        vf->priv->bitmap.v[pos]  = 0;
								}
								break;
							case ALPHA:
								vf->priv->bitmap.a[pos] = INRANGE((vf->priv->bitmap.oa[pos]+imgalpha),0,255);
								break;
							default:
						   		fprintf(stderr, "vf_bmovl: Internal error!\n");
								exit( 10 );
						} // switch
					} // for buf_x
				} // for buf_y
				free (buffer);

				// Recalculate what area contains graphics!
				if( command == CLEAR ) {
					if( (imgx <= vf->priv->x1) && ( (imgw+imgx) >= vf->priv->x2) ) {
						if( (imgy <= vf->priv->y1) && ( (imgy+imgh) >= vf->priv->y1) )
							vf->priv->y1 = imgy+imgh;
						if( (imgy <= vf->priv->y2) && ( (imgy+imgh) >= vf->priv->y2) )
							vf->priv->y2 = imgy;
					}
					if( (imgy <= vf->priv->y1) && ( (imgy+imgh) >= vf->priv->y2) ) {
						if( (imgx <= vf->priv->x1) && ( (imgx+imgw) >= vf->priv->x1) )
							vf->priv->x1 = imgx+imgw;
						if( (imgx <= vf->priv->x2) && ( (imgx+imgw) >= vf->priv->x2) )
							vf->priv->x2 = imgx;
					}
				}
			} // if feof
		} // if select
    } // if stream

	if(vf->priv->hidden) return vf_next_put_image(vf, dmpi);

	if( vf->priv->opaque ) {	// Just copy buffer memory to screen
		for( ypos=vf->priv->y1 ; ypos < vf->priv->y2 ; ypos++ ) {
			memcpy( dmpi->planes[0] + (ypos*dmpi->stride[0]) + vf->priv->x1,
			        vf->priv->bitmap.y + (ypos*vf->priv->w) + vf->priv->x1,
					vf->priv->x2 - vf->priv->x1 );
			if(ypos%2) {
				memcpy( dmpi->planes[1] + ((ypos/2)*dmpi->stride[1]) + (vf->priv->x1/2),
				        vf->priv->bitmap.u + (((ypos/2)*(vf->priv->w)/2)) + (vf->priv->x1/2),
				        (vf->priv->x2 - vf->priv->x1)/2 );
				memcpy( dmpi->planes[2] + ((ypos/2)*dmpi->stride[2]) + (vf->priv->x1/2),
				        vf->priv->bitmap.v + (((ypos/2)*(vf->priv->w)/2)) + (vf->priv->x1/2),
				        (vf->priv->x2 - vf->priv->x1)/2 );

			}
		}
	} else { 
		// Blit the bitmap on the videoscreen, pixel for pixel
	    for( ypos=vf->priv->y1 ; ypos < vf->priv->y2 ; ypos++ ) {
	        for ( xpos=vf->priv->x1 ; xpos < vf->priv->x2 ; xpos++ ) {
				pos = (ypos * dmpi->stride[0]) + xpos;

				alpha = vf->priv->bitmap.a[pos];

				if (alpha == 0) continue; // Completly transparent pixel

				if (alpha == 255) {	// Opaque pixel
					dmpi->planes[0][pos] = vf->priv->bitmap.y[pos];
					if ((ypos%2) && (xpos%2)) {
						pos = ( (ypos/2) * dmpi->stride[1] ) + (xpos/2);
						dmpi->planes[1][pos] = vf->priv->bitmap.u[pos];
						dmpi->planes[2][pos] = vf->priv->bitmap.v[pos];
					}
				} else { // Alphablended pixel
					dmpi->planes[0][pos] = (dmpi->planes[0][pos]*(1.0-(alpha/255.0))) + (vf->priv->bitmap.y[pos]*(alpha/255.0));
					if ((ypos%2) && (xpos%2)) {
						pos = ( (ypos/2) * dmpi->stride[1] ) + (xpos/2);
						dmpi->planes[1][pos] = (dmpi->planes[1][pos]*(1.0-(alpha/255.0))) + (vf->priv->bitmap.u[pos]*(alpha/255.0));
						dmpi->planes[2][pos] = (dmpi->planes[2][pos]*(1.0-(alpha/255.0))) + (vf->priv->bitmap.v[pos]*(alpha/255.0));
					}
			    }
			} // for xpos
		} // for ypos
	} // if !opaque && !hidden
    return vf_next_put_image(vf, dmpi);
} // put_image

static int
open(vf_instance_t* vf, char* args)
{
    char filename[1000];

    vf->config = config;
    vf->put_image = put_image;
    vf->query_format = query_format;
    vf->priv = malloc(sizeof(struct vf_priv_s));

	if( sscanf(args, "%d:%d:%s", &vf->priv->hidden, &vf->priv->opaque, filename) < 3 ) {
        fprintf(stderr, "vf_bmovl: Bad arguments!\n");
		fprintf(stderr, "vf_bmovl: Arguments are 'bool hidden:bool opaque:string fifo'\n");
		exit(5);
    }

    vf->priv->stream = fopen(filename, "r+");
    if(vf->priv->stream) {
		vf->priv->stream_fd = fileno( vf->priv->stream );
		FD_ZERO( &vf->priv->stream_fdset );
    } else {
		fprintf(stderr, "vf_bmovl: Error! Couldn't open FIFO %s: %s\n", filename, strerror(errno));
		vf->priv->stream = NULL;
    }

    return TRUE;
}

vf_info_t vf_info_bmovl = {
    "Read bitmaps from a FIFO and display them in window",
    "bmovl",
    "Per Wigren",
    "",
    open
};
