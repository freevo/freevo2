//#include "fb.c"
// This small program unlocks the VT so that SDL 
// with fbcon or directfb can use it. 

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/kd.h>

static void
tty_enable (void)
{
  int tty;
  
  tty = open ("/dev/tty0", O_RDWR);
  if(tty < 0) 
  {
    perror("Error can't open /dev/tty0");
    exit (1);
  }

  if(ioctl (tty, KDSETMODE, KD_TEXT) == -1) 
  {
    perror("Error setting text mode for tty");
    close(tty);
    exit (1);
  }
  
  close(tty);
}

int 
main (void) 
{
	tty_enable();
	return 0;
}
