#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <linux/kd.h>
#include <linux/vt.h>
#include <linux/fb.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>   
#include <time.h>
#include <sys/types.h>
#include <errno.h>

#include "fb.h"


struct {
  int xres, yres, vxres, vyres, xoffset, yoffset;
  int linelen;
  int fbsize;
  int fd;
  uint8 *pfb;
} fbinfo;

static struct fb_var_screeninfo fb_var;
static struct fb_fix_screeninfo fb_fix;
static int fb_mem_offset;
uint8 *fb_mem;
static int fb_size = 0;

static void tty_disable (void);
static void tty_enable (void);


void
fb_setpixel (uint16 x, uint16 y, uint32 color)
{

  *((uint32 *) &(fbinfo.pfb[y*fbinfo.linelen+x*4])) = color;
  
}


void
fb_clearscreen (uint32 color)
{
   int i;
   uint32 *p;
   

   for (i = 0; i < (fbinfo.fbsize / 4); i++) {
      p = (uint32 *) fbinfo.pfb;
      p[i] = color;
   }
  
}


int
fb_open (void)
{

  tty_disable ();
  
  fbinfo.fd = open ("/dev/fb0", O_RDWR);
  
  if (fbinfo.fd < 0) {
    perror ("Open fb");
    exit (1);
  }

  if (ioctl (fbinfo.fd, FBIOGET_FSCREENINFO, &fb_fix) != 0) {
    perror ("ioctl fix");
    exit (1);
  }

  if (ioctl (fbinfo.fd, FBIOGET_VSCREENINFO, &fb_var) != 0) {
    perror ("ioctl var");
    exit (1);
  }

  fb_var.xoffset = 0;
  fb_var.yoffset = 0;
  
  if (ioctl (fbinfo.fd, FBIOPUT_VSCREENINFO, &fb_var) != 0) {
    perror ("ioctl set var");
    exit (1);
  }

  if (ioctl (fbinfo.fd, FBIOGET_VSCREENINFO, &fb_var) != 0) {
    perror ("ioctl var");
    exit (1);
  }

  fbinfo.xres = fb_var.xres;
  fbinfo.yres = fb_var.yres;
  fbinfo.vxres = fb_var.xres_virtual;
  fbinfo.vyres = fb_var.yres_virtual;
  fbinfo.xoffset = fb_var.xoffset;
  fbinfo.yoffset = fb_var.yoffset;
  fbinfo.linelen = fb_fix.line_length;

  printf ("FB: xres=%d, yres=%d, linelen=%d\n", fbinfo.xres, fbinfo.yres,
          fbinfo.linelen);
  
  /*  fbinfo.fbsize = fb_fix.smem_len; */
  fb_size = fbinfo.fbsize = fbinfo.linelen * fbinfo.yres;
  
  fbinfo.pfb = mmap ((void *) NULL, fb_size * 4,
                     PROT_READ | PROT_WRITE, MAP_SHARED, fbinfo.fd, 0);

  fb_mem_offset = 0;
  fb_mem = (unsigned char *) fbinfo.pfb;

  close (fbinfo.fd);
  
  if (fbinfo.pfb == (uint8 *) MAP_FAILED) {
    perror ("mmap");
    exit (1);
  }

  fb_clearscreen (0); 
  
  return (0);

}


int
fb_close (void)
{

  tty_enable ();

  return (0);
}


static void
tty_disable (void)
{
  int tty;


  tty = open ("/dev/tty0", O_RDWR);
  if(tty < 0) {
    perror("Error can't open /dev/tty0");
    exit (1);
  }

  if(ioctl (tty, KDSETMODE, KD_GRAPHICS) == -1) {
    perror("Error setting graphics mode for tty");
    close(tty);
    exit (1);
  }
  
  close(tty);

}


static void
tty_enable (void)
{
  int tty;
  
  tty = open ("/dev/tty0", O_RDWR);
  if(tty < 0) {
    perror("Error can't open /dev/tty0");
    exit (1);
  }

  if(ioctl (tty, KDSETMODE, KD_TEXT) == -1) {
    perror("Error setting text mode for tty");
    close(tty);
    exit (1);
  }
  
  close(tty);

}

