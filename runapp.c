#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/poll.h>
#include <signal.h>


int
main (int ac, char *av[])
{
   sigset_t set;

   
   if (ac < 2) {
      return (0);
   }
   
   /* Set up signals (turn off blocking!) */
   sigemptyset (&set);
   sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);

   /* Overlay the child application */
   execvp (av[1], &(av[1]));

}
