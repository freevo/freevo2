/*
 * runapp.c - start a child app with signals enabled.
 *
 * The motivation for this simple application is that Python threads
 * disables pretty much all signals. This leads to problems when spawning
 * external children processes which will also have their signals disabled,
 * and that's bad for many reasons.
 *
 * $Id$
 */
 
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/poll.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>

extern int errno;


int
main (int ac, char *av[])
{
   sigset_t set;
   int i;
   FILE *fp;
   char *newav[ac];
   struct stat statbuf;
   char logfile[256];
   

   /* Does the logdir exist? */
   if (!stat (RUNAPP_LOGDIR, &statbuf)) {
     sprintf (logfile, "%s/internal-runapp.log", RUNAPP_LOGDIR);
   } else {
     /* No, log to the /tmp/freevo dir instead */
     sprintf (logfile, "/tmp/freevo/internal-runapp.log");
     mkdir ("/tmp/freevo", 0777); /* Make sure the dir exists, ignore errors */
   }
   
   fp = fopen (logfile, "a");

   fprintf (fp, "PATH = %s\n", getenv ("PATH"));
   
   for (i = 0; i < ac; i++) {
      fprintf (fp, "runapp: av[%d] = '%s'\n", i, av[i]);
   }

   fflush (fp);
   
   if (ac < 2) {
      return (0);
   }
   
   /* Copy the counted argv array to the NULL-terminated newav */
   for (i = 1; i < ac; i++) {
      newav[i-1] = av[i];
   }

   newav[ac-1] = NULL;

   /* Set up signals (turn off blocking!) */
   sigemptyset (&set);
   sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);

   /* Overlay the child application */
   execvp (newav[0], newav);

   fprintf (fp, "runapp: failed! errno = %d\n", errno);
   
   fclose (fp);
}
