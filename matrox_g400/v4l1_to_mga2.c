/* This is a test of picture-in-picture using only one videocard.
 * It is not used yet by Freevo... */

/*
 *
 * RUN AS ROOT! NEEDED FOR MMIO STUFF ETC....
 *
 * XXX Doesn't work when compiled with -O2 for some reason. Tried
 * XXX -fvolatile, didn't solve it.
 */

#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/videodev.h>
#include <sys/errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <inttypes.h>
#include <signal.h>
#include <sys/time.h>
#include <string.h>

#include "mga_vid.h"
#include "frequencies.h"
#include "fb.h"


#define V4L_SRC_IMAGE_PALETTE VIDEO_PALETTE_YUV422
#define V4L_SRC_IMAGE_WIDTH 640
#define V4L_SRC_IMAGE_HEIGHT 480
#define V4L_SRC_IMAGE_DEPTH 16

#define V4L_DST_IMAGE_PALETTE VIDEO_PALETTE_YUV422
#define V4L_DST_IMAGE_WIDTH 640
#define V4L_DST_IMAGE_HEIGHT 480
#define V4L_DST_IMAGE_DEPTH 16

/* XXX This is an ugly hack that hardcodes the kernel address that the
 * video4linux driver is given to put the captured frames at.
 * Hopefully this entire program can be dropped as soon as
 * the mplayer tv stuff works
 */

extern int errno;

int mga_fd;
mga_vid_config_t config;
uint8_t *mga_vid_base;
uint32_t is_g400;

int is_tuned (int fd);
int v4l1_init (void);
void mga_setup (void);
void get_channels (int fd, int channels, int audios);
void set_input (int fd, char *norm, char *input, float freq);
float get_freq (char *name, char *channel);
void get_frame (void);
void get_frame2 (void);


void
print_ts (void)
{
   struct timeval tv;

   
   gettimeofday (&tv, (struct timezone *) NULL);

   printf ("%7d.%03d\n", tv.tv_sec, tv.tv_usec / 1000);
   
}


int
main (int ac, char *av[])
{
  int fd, arg;
  char input[200], norm[200], std[200], chan[200];
  float freq;
  sigset_t set;
  int i;
  

  /* If this program is started as a child to another task, one or
   * more signals might be blocked!
   * Unblock all signals except SIGUSR1 (used for threading) just to make sure. */
  sigemptyset (&set);
  sigaddset (&set, 32);
  sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);

  fb_open ();

  /*  for (i = 0; i < 800*600*4; i++) fb_mem[i] = i & 0xff; */
  
  get_frame2 ();
  
  exit (0);





  
  fd = v4l1_init ();

  if (ac == 2) {
     if (sscanf (av[1], "%s %s %s %s", norm, input, std, chan) == 4) {
        printf ("Got start args %s %s %s %s\n", norm, input, std, chan);
        freq = get_freq (std, chan);

        if (freq != 0.0) {
           printf ("Got freq %6.2f MHz\n", freq);
           set_input (fd, norm, input, freq);
        } else {
           printf ("Couldn't find %s %s in the table!\n",
                   std, chan);
        }
     } else {
        printf ("Cannot decode start args!\n");
     }
  } else {     
     set_input (fd, "ntsc", "composite1", 0.0);
  }

  arg = 1;
  ioctl (fd, VIDIOCCAPTURE, &arg);

  /* Just wait until the process is killed */
  while (1) {


     printf ("Waiting for input ([ntsc|pal|secam] [composite1|television] "
             "[us-bcast|us-cable|europe-west|...] channelname)...\n");
     if (fscanf (stdin, "%s %s %s %s", norm, input, std, chan) == 4) {
        printf ("Got %s %s %s %s\n", norm, input, std, chan);
        freq = get_freq (std, chan);
        if (freq != 0.0) {
           printf ("Got freq %6.2f MHz\n", freq);
           set_input (fd, norm, input, freq);
        } else {
           printf ("Couldn't find %s %s in the table!\n",
                   std, chan);
        }
     } else {
        printf ("Cannot decode input, try again!\n");
     }
  }
  
  arg = 0;
  ioctl (fd, VIDIOCCAPTURE, &arg);

  ioctl (mga_fd, MGA_VID_OFF, 0);
  close (mga_fd);

  exit (0);
  
}


/*

  struct video_window:  Where to place the captured frame

 */

#if 0
struct video_window
{
	__u32	x,y;			/* Position of window */
	__u32	width,height;		/* Its size */
	__u32	chromakey;
	__u32	flags;
	struct	video_clip *clips;	/* Set only */
	int	clipcount;
#define VIDEO_WINDOW_INTERLACE	1
#define VIDEO_WINDOW_CHROMAKEY	16	/* Overlay by chromakey */
#define VIDEO_CLIP_BITMAP	-1
/* bitmap is 1024x625, a '1' bit represents a clipped pixel */
#define VIDEO_CLIPMAP_SIZE	(128 * 625)
};

struct video_capture
{
	__u32 	x,y;			/* Offsets into image */
	__u32	width, height;		/* Area to capture */
	__u16	decimation;		/* Decimation divder */
	__u16	flags;			/* Flags for capture */
#define VIDEO_CAPTURE_ODD		0	/* Temporal */
#define VIDEO_CAPTURE_EVEN		1
};

struct video_buffer
{
	void	*base;
	int	height,width;
	int	depth;
	int	bytesperline;
};


struct video_mmap
{
	unsigned	int frame;		/* Frame (0 - n) for double buffer */
	int		height,width;
	unsigned	int format;		/* should be VIDEO_PALETTE_* */
};


struct video_mbuf
{
	int	size;		/* Total memory to map */
	int	frames;		/* Frames */
	int	offsets[VIDEO_MAX_FRAME];
};
	
#endif


void
get_frame (void)
{
   struct video_mbuf vmb;	// mmap buffers
   unsigned char *mmbuf;	// memory map buffer
   struct video_mmap mm;	// temp buffer
   int res;
   int frame;
   struct video_window vwin;
   int fd;
   struct video_picture vidpic;
   int i, j;
   uint32 *p, *s, *d;
   float freqs[2];
   int ctr = 0, sel = 0, discard = 0;
   
  
   fd = open ("/dev/video0", O_RDWR);

   vidpic.brightness = 32768;
   vidpic.hue = 32768;
   vidpic.colour = 32768;
   vidpic.contrast = 32768;
   vidpic.whiteness = 32768;
   vidpic.depth = 4;
   vidpic.palette = VIDEO_PALETTE_RGB32;
   
   printf ("set vidpic: %d\n", ioctl (fd, VIDIOCSPICT, &vidpic));
   
   vwin.x = 0;
   vwin.y = 0;
   vwin.flags = 0;
   vwin.width = 640;
   vwin.height = 480;
   vwin.clips = NULL;
   vwin.clipcount = 0;
   
   if (ioctl(fd, VIDIOCSWIN, &vwin)) {
      perror("v4l1 core init - set window");
      goto error1;
   }
   
   if (ioctl (fd, VIDIOCGMBUF, &vmb) != 0) {
      perror ("v4l1 core init - could not request buffers");
      goto error1;
   }
   
   if (vmb.frames == 0) {
      fprintf (stderr, "v4l1 core init - could not get any buffers\n");
      goto error1;
   }
   
   mmbuf = (unsigned char *) mmap (NULL, vmb.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
   
   if ((int) mmbuf == -1) {
      perror ("v4l1 core init - mmap failed");
      goto error1;
   }
   
#define ROWS 240
#define COLS 320

   freqs[0] = get_freq ("us-cable", "2");
   freqs[1] = get_freq ("us-cable", "5");
   
   mm.frame = 0;
   mm.width = COLS;
   mm.height = ROWS;
   mm.format = VIDEO_PALETTE_RGB32;
   
   printf ("mcap = %d\n", ioctl (fd, VIDIOCMCAPTURE, &mm));
   mm.frame = 1;
   printf ("mcap = %d\n", ioctl (fd, VIDIOCMCAPTURE, &mm));

   frame = 0;
   while (1) {
      
      /*  printf ("Waiting for sync\n"); */
      res = ioctl (fd, VIDIOCSYNC, &frame);
      
      if (res < 0 && errno == EINTR) continue;

      printf ("disc = %d, ctr = %d\n", discard, ctr);
      
      switch (ctr++) {
         case 1:
            sel = 0;
            printf ("Switched channel to %d...\n", sel);
            set_input (fd, "ntsc", "television", freqs[sel]);
            discard = 2;
            break;
            
         case 60:
            sel = 1;
            printf ("Switched channel to %d\n", sel);
            set_input (fd, "ntsc", "television", freqs[sel]);
            discard = 2;
            break;
            
         case 62:
            ctr = 0;
            break;
      }
      
      /*  print_ts(); */
      if (!discard) {
         printf ("DISPLAY   %d\n", sel);
         for (i = 0; i < ROWS; i++) {
            bcopy (&(mmbuf[vmb.offsets[frame] + i*COLS*4]),
                   &(fb_mem[(i + sel*ROWS) * 768*4]), COLS*4);
         }
      } else {
         printf ("DISCARD   %d\n", sel);
         discard--;
      }
   
      /*  printf ("Got sync\n"); */
      mm.frame = frame;
      ioctl (fd, VIDIOCMCAPTURE, &mm);
      frame = (frame+1) % 2;

   }

   printf ("done, res = %d\n", res);
   
   /* The data is in mmbuf[vmb.offsets[frame]] */
   bcopy (&(mmbuf[vmb.offsets[0]]), fb_mem, 640*480*4);

   p = (uint32 *) &(mmbuf[vmb.offsets[0]]);
#if 0
   for (i = 0; i < 480; i++) {
      bcopy (&(mmbuf[vmb.offsets[0] + i*640*4]), &(fb_mem[i * 800*4]), 640*4);
   }
#endif

   close (fd);
   
   return;
   
 error1:
   exit (1);
}


void
get_frame2 (void)
{
   struct video_mbuf vmb;	// mmap buffers
   unsigned char *mmbuf;	// memory map buffer
   struct video_mmap mm;	// temp buffer
   int res;
   int frame;
   struct video_window vwin;
   int fd;
   struct video_picture vidpic;
   int i, j;
   uint32 *p, *s, *d;
   float freqs[2];
   int ctr = 0, sel = 0, discard = 0;
   int row;
   
  
   fd = open ("/dev/video0", O_RDWR);

   vidpic.brightness = 32768;
   vidpic.hue = 32768;
   vidpic.colour = 32768;
   vidpic.contrast = 32768;
   vidpic.whiteness = 32768;
   vidpic.depth = 4;
   vidpic.palette = VIDEO_PALETTE_RGB32;
   
   printf ("set vidpic: %d\n", ioctl (fd, VIDIOCSPICT, &vidpic));
   
   vwin.x = 0;
   vwin.y = 0;
   vwin.flags = 0;
   vwin.width = 768;
   vwin.height = 576;
   vwin.clips = NULL;
   vwin.clipcount = 0;
   
   if (ioctl(fd, VIDIOCSWIN, &vwin)) {
      perror("v4l1 core init - set window");
      goto error1;
   }
   
   if (ioctl (fd, VIDIOCGMBUF, &vmb) != 0) {
      perror ("v4l1 core init - could not request buffers");
      goto error1;
   }
   
   if (vmb.frames == 0) {
      fprintf (stderr, "v4l1 core init - could not get any buffers\n");
      goto error1;
   }
   
   mmbuf = (unsigned char *) mmap (NULL, vmb.size, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
   
   if ((int) mmbuf == -1) {
      perror ("v4l1 core init - mmap failed");
      goto error1;
   }
   
#define COLS 768
#define ROWS 288

   mm.frame = 0;
   mm.width = COLS;
   mm.height = ROWS;
   mm.format = VIDEO_PALETTE_RGB32;
   
   printf ("mcap = %d\n", ioctl (fd, VIDIOCMCAPTURE, &mm));
   mm.frame = 1;
   printf ("mcap = %d\n", ioctl (fd, VIDIOCMCAPTURE, &mm));

   frame = 0;
   while (1) {
      
      /*  printf ("Waiting for sync\n"); */
      res = ioctl (fd, VIDIOCSYNC, &frame);
      
      if (res < 0 && errno == EINTR) continue;

      for (i = 0; i < ROWS; i++) {
         row = i*2;
         bcopy (&(mmbuf[vmb.offsets[frame] + i*COLS*4]),
                &(fb_mem[row * 768*4]), COLS*4);
         row = i*2+1;
         bcopy (&(mmbuf[vmb.offsets[frame] + i*COLS*4]),
                &(fb_mem[row * 768*4]), COLS*4);
      }
   
      mm.frame = frame;
      ioctl (fd, VIDIOCMCAPTURE, &mm);
      frame = (frame+1) % 2;

   }

   printf ("done, res = %d\n", res);
   
   close (fd);
   
   return;
   
 error1:
   exit (1);
}


int
v4l1_init (void)
{
  struct video_capability vidcap;
  struct video_picture vidpic;
  struct video_buffer vidbuf;
  struct video_window vidwin;
  struct video_capture vidsubcap;
  int fd;

  
  fd = open ("/dev/video0", O_RDWR);

  ioctl (fd, VIDIOCGCAP, &vidcap);

  printf ("Vidcap:\n");
  printf ("Name:      %s\n", vidcap.name);
  printf ("type:      0x%08x\n", vidcap.type);
  printf ("channels:  %d\n", vidcap.channels);
  printf ("audios:    %d\n", vidcap.audios);
  printf ("maxwidth:  %d\n", vidcap.maxwidth);
  printf ("maxheight: %d\n", vidcap.maxheight);
  printf ("minwidth:  %d\n", vidcap.minwidth);
  printf ("minheight: %d\n", vidcap.minheight);

  /* -------------------------------------------------- */

  vidpic.brightness = 32768;
  vidpic.hue = 32768;
  vidpic.colour = 32768;
  vidpic.contrast = 32768;
  vidpic.whiteness = 32768;
  vidpic.depth = V4L_SRC_IMAGE_DEPTH;
  vidpic.palette = V4L_SRC_IMAGE_PALETTE;

  printf ("set vidpic: %d\n", ioctl (fd, VIDIOCSPICT, &vidpic));

  ioctl (fd, VIDIOCGPICT, &vidpic);

  printf ("\nVidpic:\n");
  printf ("bright:   %5d\n", vidpic.brightness);
  printf ("hue:      %5d\n", vidpic.hue);
  printf ("color:    %5d\n", vidpic.colour);
  printf ("contrast: %5d\n", vidpic.contrast);
  printf ("white:    %5d\n", vidpic.whiteness);
  printf ("depth:    %d\n", vidpic.depth);
  printf ("palette:  %d\n", vidpic.palette);

  /* -------------------------------------------------- */

  vidwin.x = 0;
  vidwin.y = 0;
  vidwin.width = V4L_SRC_IMAGE_WIDTH;
  vidwin.height = V4L_SRC_IMAGE_HEIGHT;
  vidwin.flags = 0;
  vidwin.chromakey = 0;
  vidwin.clips = 0;
  vidwin.clipcount = 0;

  printf ("set vidwin: %d\n", ioctl (fd, VIDIOCSWIN, &vidwin));
  printf ("Errno = %d\n", errno);

  ioctl (fd, VIDIOCGWIN, &vidwin);

  printf ("\nVidwin:\n");
  printf ("x:         %d\n", (unsigned int) vidwin.x);
  printf ("y:         %d\n", (unsigned int) vidwin.y);
  printf ("width:     %d\n", (unsigned int) vidwin.width);
  printf ("height:    %d\n", (unsigned int) vidwin.height);
  printf ("flags:     %d\n", (unsigned int) vidwin.flags);
  printf ("chromakey: %d\n", (unsigned int) vidwin.chromakey);
  printf ("clips:     %d\n", (unsigned int) vidwin.clips);
  printf ("clipcount: %d\n", (unsigned int) vidwin.clipcount);

  return (fd);
  
}



void
get_channels (int fd, int channels, int audios)
{
   struct video_channel vidchan;
   struct video_audio vidaudio;
   struct video_tuner vidtuner;
   int i, res;

   
   for (i = 0; i < channels; i++) {
      memset (&vidchan, 0, sizeof (vidchan));
      vidchan.channel = i;
      res = ioctl (fd, VIDIOCGCHAN, &vidchan);
      printf ("\nGet channel res = %d\n", res);
      printf ("Channel:  %d\n", vidchan.channel);
      printf ("Name:     %s\n", vidchan.name);
      printf ("Tuners:   %d\n", vidchan.tuners);
      printf ("Flags:    %d\n", vidchan.flags);
      printf ("Type:     %d\n", vidchan.type);
      printf ("Norm:     %d\n", vidchan.norm);
   }
   
   for (i = 0; i < audios; i++) {
      memset (&vidaudio, 0, sizeof (vidaudio));
      res = ioctl (fd, VIDIOCGAUDIO, &vidaudio);
      printf ("\nGet audio res = %d\n", res);
      printf ("Channel:  %d\n", vidaudio.audio);
      printf ("Name:     %s\n", vidaudio.name);
      printf ("Volume:   %d\n", vidaudio.volume);
      printf ("Bass:     %d\n", vidaudio.bass);
      printf ("Treble:   %d\n", vidaudio.treble);
      printf ("Flags:    0x%02x\n", vidaudio.flags);
      printf ("Mode:     0x%02x\n", vidaudio.mode);
      printf ("Balance:  %d\n", vidaudio.balance);
      printf ("Step:     %d\n", vidaudio.step);
   }
   
   memset (&vidtuner, 0, sizeof (vidtuner));
   res = ioctl (fd, VIDIOCGTUNER, &vidtuner);
   printf ("\nGet tuner res = %d\n", res);
   printf ("Tuner:     %d\n", vidtuner.tuner);
   printf ("Name:      %s\n", vidtuner.name);
   printf ("Range low: %d\n", vidtuner.rangelow);
   printf ("Range hi:  %d\n", vidtuner.rangehigh);
   printf ("Flags:    0x%03x\n", vidtuner.flags);
   printf ("Mode:     0x%02x\n", vidtuner.mode);
   printf ("Signal:   %d\n", vidtuner.signal);
   
}


int
is_tuned (int fd)
{
   struct video_tuner vidtuner;
   int res;

   memset (&vidtuner, 0, sizeof (vidtuner));
   res = ioctl (fd, VIDIOCGTUNER, &vidtuner);
   printf ("\nGet tuner res = %d\n", res);
   printf ("Tuner:     %d\n", vidtuner.tuner);
   printf ("Name:      %s\n", vidtuner.name);
   printf ("Range low: %d\n", vidtuner.rangelow);
   printf ("Range hi:  %d\n", vidtuner.rangehigh);
   printf ("Flags:    0x%03x\n", vidtuner.flags);
   printf ("Mode:     0x%02x\n", vidtuner.mode);
   printf ("Signal:   %d\n", vidtuner.signal);

   return (vidtuner.signal);
   
}


void
set_input (int fd, char *norm, char *input, float freq)
{
   struct video_channel chan;
   struct video_audio vidaudio;
   int i = 0;

   
   memset (&vidaudio, 0, sizeof (vidaudio));
   vidaudio.volume = 0xffff;
   
   ioctl (fd, VIDIOCSAUDIO, &vidaudio);
   
   do {
      chan.channel = i;
      
      if (ioctl (fd, VIDIOCGCHAN, &chan)) {
         fprintf (stderr, "Unknown input '%s'\n", input);
         goto error1;
      }
      
      if (strcasecmp (chan.name, input) == 0)
         break;
      
      i++;
      
   }  while (i > 0);
   
   if (strcasecmp (norm, "PAL") == 0) {
      chan.norm = VIDEO_MODE_PAL;
   } else if (strcasecmp (norm, "NTSC") == 0) { 
      chan.norm = VIDEO_MODE_NTSC;
   } else if (strcasecmp (norm, "SECAM") == 0) { 
      chan.norm = VIDEO_MODE_SECAM;
   } else {
      fprintf (stderr, "Unknown norm '%s'\n", norm);
      goto error1; 
   }
   
   if (ioctl (fd, VIDIOCSCHAN, &chan)) {
      perror("v4l1 core init - could not set input");
      goto error1;
   }
   
   if (freq > 0) {
      unsigned long i = (unsigned long) (freq * 16.0);

      
      if (ioctl (fd, VIDIOCSFREQ, &i)) {
         perror ("Could not set frequency");
         goto error1;
      }
   }

   return;
   
 error1:
   exit (1);
   
}


float
get_freq (char *name, char *channel)
{
   int i, j;
   float freq = 0.0;
   

   i = 0;
   while (chanlists[i].name != (char *) NULL) {

      /* printf ("Searching for %s: got %s\n", name, chanlists[i].name); *7
      
      /* Do the names match? */
      if (strcasecmp (chanlists[i].name, name) == 0) {
         /* Yep, try to find the channel */
         for (j = 0; j < chanlists[i].count; j++) {

            /* printf ("Searching for %s: got %s\n", channel,
               chanlists[i].list[j].name); */
      
            if (strcasecmp (chanlists[i].list[j].name, channel) == 0) {
               /* printf ("Channel frequency = %d kHz\n",
                  chanlists[i].list[j].freq); */
               
               freq = ((float) chanlists[i].list[j].freq) / 1000.0;
               return (freq);
            }
         }
         printf ("Couldn't find channel %s for the broadcast standard %s in "
                 "the table!\n", channel, name);
         return (0.0);
      }

      i++;

   }

   printf ("Couldn't find broadcast standard %s in the table!\n",
           name);

   return (0.0);

}
