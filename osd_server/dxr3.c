/*
 * I put this piece of code together by using parts from
 # Michael Hunold osd-code, it showed my the use of fame 
 # and how send the stuff to the dxr3.
 # The RGB2YUV code is from Björn Ståhl's try of an OSD.
 */

#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <assert.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/select.h>
#include <fcntl.h>
#include <time.h>

#include "dxr3.h"

#include <linux/em8300.h>
#include "fame.h"
#define OUTBUF_SIZE 100000

int fd_video = -1;
int fd_control = -1;
char* devname_v = "/dev/em8300_mv-0";
char* devname_c = "/dev/em8300-0";

int xres, yres;
long size;

struct RGB24 {
 uint8 r;
 uint8 g;
 uint8 b;
};

typedef struct RGB24 rgb24; 

static fame_parameters_t fame_params;
static fame_yuv_t fame_yuv;
static fame_context_t *fame_ctx = NULL;
static fame_object_t *fame_obj;

unsigned char *yuv = NULL;
unsigned char *outbuf = NULL;

//uint8 *myfb;

/* RGB(A) result of 2x2 subsampling on a specified region */
/* neither optimized nor beautiful but I still share with him a mothers love */
rgb24 subsample_2x2(uint8* dataptr, int x, int y){
 rgb24 result;
 int r[4], g[4], b[4];

 b[0] = dataptr[(y * xres + x) * 4];
 g[0] = dataptr[(y * xres + x) * 4 + 1];
 r[0] = dataptr[(y * xres + x) * 4 + 2];

 b[1] = dataptr[(y * xres + x + 1) * 4];
 g[1] = dataptr[(y * xres + x + 1) * 4 + 1];
 r[1] = dataptr[(y * xres + x + 1) * 4 + 2];

 b[2] = dataptr[( (y + 1) * xres + x) * 4];
 g[2] = dataptr[( (y + 1) * xres + x) * 4 + 1];
 r[2] = dataptr[( (y + 1) * xres + x) * 4 + 2];

 b[3] = dataptr[( (y + 1) * xres + x + 1) * 4];
 g[3] = dataptr[( (y + 1) * xres + x + 1) * 4 + 1];
 r[3] = dataptr[( (y + 1) * xres + x + 1) * 4 + 2];

 result.r = (r[0] + r[1] + r[2] + r[3]) / 4; /* well, this isn't really a real subsample.. but an average on the individual components works good enough */
 result.g = (g[0] + g[1] + g[2] + g[3]) / 4;
 result.b = (b[0] + b[1] + b[2] + b[3]) / 4;

 return result;
}

/* .. UGLY UGLY UGLY.. feel free to FIXME */
void rgb32_to_yuv12(uint8* dataptr){
	int r, g, b, xpos, ypos, pc_a;
	rgb24 sample;
	float y;
	
	uint8 *ydat = yuv;
	uint8 *udat = yuv+(xres*yres);
	uint8 *vdat = yuv+(xres*yres)+(xres*yres)/2;

	pc_a = 0;


	for (xpos = 0; xpos < xres * yres * 4; xpos+=4){
		b = dataptr[xpos];
		g = dataptr[xpos+1];
		r = dataptr[xpos+2];

		y = (int) (0.257 * r + 0.504 * g + 0.098 * b + 16);
		ydat[pc_a] = y;

		pc_a++;
	}

	pc_a = 0;

/* Pass Two, Cr/Cb from 2x2 subsamples */
	for (ypos=0; ypos < yres/2; ypos++)
		for (xpos=0; xpos < xres/2; xpos++){
			sample = subsample_2x2(dataptr, xpos * 2, ypos * 2);

/* Cr = V, Cb = U */
			udat[ypos*(xres/2)+xpos] = (uint8) ( -(0.148 * sample.r) - 0.291 * sample.g + 0.439 * sample.b + 128);
			vdat[ypos*(xres/2)+xpos] = (uint8) (0.439 * sample.r - 0.368 * sample.g - 0.071 * sample.b + 128);

			pc_a ++;
		};
}

/*void bufscale(uint8 *fb) {
	int z, zz, hy ,hx;
	hx = xres/2;
	hy = yres/2;
	zz = 0;
	printf("Start!");
	for(z = 0;z < hy*4; z+=4) {
			memcpy((uint8 *)myfb+zz,(uint8 *)fb+z,4);
			zz+=4;
			memcpy((uint8 *)myfb+zz,(uint8 *)fb+z,4);
			zz+=4;
		}
		memcpy((uint8 *)myfb+(((y*2)+1)*xres*4),(uint8 *)fb+(y*hx*4),xres*4);
	}
	printf("End!");
}*/

int
dxr3_open (int width, int height)
{
        int fdflags = O_WRONLY;
        int ioval = 0;
        
	em8300_register_t reg;

//	xres = width*2;
//	yres = height*2;
	xres = width;
	yres = height;

	printf("x: %d y: %d\n", xres, yres);


/*	myfb = (uint8*)malloc(xres*yres*4);
        if( NULL == myfb) {
                fprintf(stderr,"myfb: malloc() failed.\n");
                return -1;
        }
*/
	yuv = (unsigned char*)malloc(xres*yres*2);
        if( NULL == yuv) {
                fprintf(stderr,"yuv: malloc() failed.\n");
                return -1;
        }

	// dxr3
        fd_video = open(devname_v, fdflags);
        if (fd_video < 0) {
                return -1;
        }
        fd_control = open(devname_c, fdflags);
        if (fd_control < 0) {
                close(fd_video);
                return -1;
        }

        /* Set the playmode to play (just in case another app has set it to something else) */
        ioval = EM8300_PLAYMODE_PLAY;
        if (ioctl(fd_control, EM8300_IOCTL_SET_PLAYMODE, &ioval) < 0) {
                printf("VO: [dxr3] Unable to set playmode!\n");
                return -1;
        }

        /* Start em8300 prebuffering and sync engine */
        reg.microcode_register = 1;
        reg.reg = 0;
        reg.val = MVCOMMAND_SYNC;
        if (ioctl(fd_control, EM8300_IOCTL_WRITEREG, &reg)) {
                printf("EM8300_IOCTL_WRITEREG\n");
                return -1;
        }
        
        /* Clean buffer by syncing it */
        ioval = EM8300_SUBDEVICE_VIDEO;
        ioctl(fd_control, EM8300_IOCTL_FLUSH, &ioval);

        fsync(fd_video);

        outbuf = (unsigned char*)malloc(100000);
        if( outbuf == yuv) {
                fprintf(stderr,"init_fame(): malloc() failed.\n");
                free(yuv);
                return -1;
        }

        fame_ctx = fame_open();
        if( 0 == fame_ctx) {
                fprintf(stderr,"init_fame(): fame_open() failed.\n");
                return -1;
        }

        fame_obj = fame_get_object(fame_ctx, "motion/pmvfast");
        fame_register(fame_ctx, "motion", fame_obj);
                        
        memset(&fame_params, 0, sizeof(fame_parameters_t));
        fame_params.width = xres;
        fame_params.height = yres;
        fame_params.coding = "I";
        fame_params.quality = 75;
        fame_params.bitrate = 0;
        fame_params.slices_per_frame = 1;
        fame_params.frames_per_sequence = 25;
        fame_params.shape_quality = 100;
        fame_params.search_range = 1;
        fame_params.verbose = 0;
        fame_params.profile = NULL;

        fame_params.frame_rate_num = 25;
        fame_params.frame_rate_den = 1;

        fame_init(fame_ctx, &fame_params, outbuf, OUTBUF_SIZE);

        fame_yuv.w = xres;
        fame_yuv.h = yres;
        fame_yuv.y = yuv;
        fame_yuv.u = fame_yuv.y + (xres*yres);
        fame_yuv.v = fame_yuv.u + (xres*yres)/2;

	memset(yuv,xres*yres*2,0);
        fame_start_frame(fame_ctx, &fame_yuv, NULL);
        size = fame_encode_slice(fame_ctx);
        write(fd_video, outbuf, size);
        fame_end_frame(fame_ctx, NULL);

	return (0);
}

void
dxr3_update (uint8 *pFB)
{
//	bufscale(pFB);
//	rgb32_to_yuv12(myfb);
	rgb32_to_yuv12(pFB);
        fame_start_frame(fame_ctx, &fame_yuv, NULL);
        size = fame_encode_slice(fame_ctx);
        write(fd_video, outbuf, size);
        fame_end_frame(fame_ctx, NULL);
        write(fd_video, outbuf, size);
        printf("Writing Frame: %i\n",(int)(time(NULL)-100000));
}

void
dxr3_close (void)
{
        if(0 != fame_ctx) {
                fame_close(fame_ctx);
        }
        if( 0 != yuv) {
                free(yuv);
        }
        
        close(fd_video);
        close(fd_control);

	return;
}
