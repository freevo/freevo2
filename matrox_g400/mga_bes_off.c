/*
 *
 * RUN AS ROOT! NEEDED FOR MMIO STUFF ETC....
 *
 */

#include <stdio.h>
#include <sys/ioctl.h>
#include <fcntl.h>

#include "mga_vid.h"


int
main (int ac, char *av[])
{
   int mga_fd;
   

   mga_fd = open ("/dev/mga_vid", O_RDWR);

   if (mga_fd == -1) {
      fprintf (stderr, "Couldn't open driver\n");
      exit (1);
   }

  ioctl (mga_fd, MGA_VID_OFF, 0);

  close (mga_fd);

  exit (0);
  
}
