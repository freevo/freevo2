/* This is the TV application for Freevo. It uses Video4Linux1 to overlay the TV
 * frames to the Matrox G400 backend scaler, using very little CPU. It accepts
 * commands on stdin to change channels while it is running.
 */

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

#include "mga_vid.h"
#include "frequencies.h"


#define MGA_PALETTE MGA_VID_FORMAT_YUY2

#define MGA_DST_IMAGE_WIDTH 768 /* XXX Hardcoded values that depend on the size of the FB! */
#define MGA_DST_IMAGE_HEIGHT 576

#define V4L_SRC_IMAGE_PALETTE VIDEO_PALETTE_YUV422
#define V4L_SRC_IMAGE_WIDTH 640
#define V4L_SRC_IMAGE_HEIGHT 480
#define V4L_SRC_IMAGE_DEPTH 16

#define V4L_DST_IMAGE_PALETTE VIDEO_PALETTE_YUV422
#define V4L_DST_IMAGE_WIDTH 640
#define V4L_DST_IMAGE_HEIGHT 480
#define V4L_DST_IMAGE_DEPTH 16

/* This is the _physical_ address of the MGA G400 Back-End-Scaler framebuffer.
 * It is needed for the Video4Linux1 direct video overlay to the framebuffer.
 */
#define MGA_VID_ADDR mga_vid_besbase_addr


int mga_fd;
mga_vid_config_t config;
uint32_t mga_vid_besbase_addr;

int v4l1_init (void);
int mga_setup (void);
void get_channels (int fd, int channels, int audios);
void set_input (int fd, char *norm, char *input, float freq);
float get_freq (char *name, char *channel);


int
main (int ac, char *av[])
{
  int fd, arg;
  char input[200], norm[200], std[200], chan[200];
  float freq;
  sigset_t set;
  

  /* If this program is started as a child to another task, one or
   * more signals might be blocked!
   * Unblock all signals except SIGUSR1 (used for threading) just to make sure. */
  sigemptyset (&set);
  sigaddset (&set, 32);
  sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);
        
  if (mga_setup ()) {
     printf ("Couldn't set up the MGA G400 graphics board.\n");
     exit (1);
  }

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

        if (!strcmp (chan, "fine_plus")) {
           freq += 1.0/16.0;
        } else if (!strcmp (chan, "fine_minus")) {
           freq -= 1.0/16.0;
        } else {
           freq = get_freq (std, chan);
        }

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


int
v4l1_init (void)
{
  struct video_capability vidcap;
  struct video_picture vidpic;
  struct video_buffer vidbuf;
  struct video_window vidwin;
  struct video_capture vidsubcap;
  int fd;

  
  fd = open ("/dev/video", O_RDWR);

  if (!fd) {
    fprintf (stderr, "v4l12_to_mga: Couldn't open /dev/video! errno=%d\n",
             errno);
    exit (1);
  }
    
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

  vidbuf.base = (void *) MGA_VID_ADDR;
  vidbuf.width = V4L_DST_IMAGE_WIDTH;
  vidbuf.height = V4L_DST_IMAGE_HEIGHT;
  vidbuf.depth = V4L_DST_IMAGE_DEPTH;
  vidbuf.bytesperline = V4L_DST_IMAGE_WIDTH*(V4L_DST_IMAGE_DEPTH/8);

  printf ("set vidbuf: %d\n", ioctl (fd, VIDIOCSFBUF, &vidbuf));
  printf ("Errno = %d\n", errno);

  ioctl (fd, VIDIOCGFBUF, &vidbuf);

  printf ("\nVidbuf:\n");
  printf ("base:         0x%08x\n", (unsigned int) vidbuf.base);
  printf ("width:        %3d\n", vidbuf.width);
  printf ("height:       %3d\n", vidbuf.height);
  printf ("depth:        %2d\n", vidbuf.depth);
  printf ("bytesperline: %5d\n", vidbuf.bytesperline);

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

int
mga_setup (void)
{
   
   mga_fd = open ("/dev/mga_vid",O_RDWR);

   if (mga_fd == -1) {
      printf ("Couldn't open driver\n");
      return (-1);
   }

   config.version = MGA_VID_VERSION;
   config.src_width = V4L_DST_IMAGE_WIDTH;
   config.src_height= V4L_DST_IMAGE_HEIGHT;
   config.dest_width = MGA_DST_IMAGE_WIDTH;
   config.dest_height = MGA_DST_IMAGE_HEIGHT;
   config.x_org = 0;
   config.y_org = 0;
   config.colkey_on = 0;
   config.format = MGA_PALETTE;
   config.frame_size=V4L_DST_IMAGE_WIDTH*V4L_DST_IMAGE_HEIGHT*(V4L_DST_IMAGE_DEPTH / 8);
   config.num_frames=1;

   if (ioctl (mga_fd, MGA_VID_CONFIG, &config)) {
      perror ("Error in config ioctl");
      return (-1);
   }

   if (ioctl (mga_fd, MGA_VID_GET_BESADDR, &mga_vid_besbase_addr) == 0) {
      printf ("BES addr = 0x%08x\n", mga_vid_besbase_addr);
   } else {
      printf ("ioctl failed, errno = %d.\n", errno);
      return (-1);
   }

   /* Done */
   return (0);
   
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
