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
#include <string.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <sched.h>

extern int errno;

static void runapp_setprio (int newprio, FILE *fp);


int
main (int ac, char *av[])
{
  sigset_t set;
  int i;
  FILE *fp;
  char *newav[ac];
  struct stat statbuf;
  char logfile[256];
  char cmd_str[1000];
  char currdir[1000];
  int newprio;
  int first_arg;
  
  
  /* Does the logdir exist? */
  if (!stat (RUNAPP_LOGDIR, &statbuf)) {
    sprintf (logfile, "%s/internal-runapp-%d.log", RUNAPP_LOGDIR, getuid());
  } else {
    /* No, log to the /tmp/freevo dir instead */
    sprintf (logfile, "/tmp/freevo/internal-runapp-%d.log", getuid());
    mkdir ("/tmp/freevo", 0777); /* Make sure the dir exists, ignore errors */
  }
  
  fp = fopen (logfile, "a");

  
  fprintf (fp, "PATH = %s\n", getenv ("PATH"));
  fprintf (fp, "CWD = %s\n", getcwd (currdir, sizeof (currdir)));
  
  cmd_str[0] = 0;
  
  for (i = 0; i < ac; i++) {
    char tmp[256];


    sprintf (tmp, "%s ", av[i]);
    strcat (cmd_str, tmp);
    
    fprintf (fp, "runapp: av[%d] = '%s'\n", i, av[i]);
  }

  fprintf (fp, "Command: '%s'\n", cmd_str);
  
  fflush (fp);
  
  if (ac < 2) {
    return (0);
  }

  /* Is the first arg the priority setting? */
  if (sscanf (av[1], "--prio=%d", &newprio) == 1) {
    
    /* Yes, set the process priority */
    runapp_setprio (newprio, fp);

    first_arg = 2;
  } else {
    first_arg = 1;
  }
    
  /* Copy the counted argv array to the NULL-terminated newav */
  for (i = first_arg; i < ac; i++) {
    newav[i-first_arg] = av[i];
  }
  
  newav[ac-first_arg] = NULL;
  
  /* Set up signals (turn off blocking!) */
  sigemptyset (&set);
  sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);

  fflush (fp);
  
  /* Overlay the child application */
  execvp (newav[0], newav);
  
  fprintf (fp, "runapp: failed! errno = %d\n", errno);
  
  fclose (fp);

  exit (0);
  
}


static void
runapp_setprio (int newprio, FILE *fp)
{
  int res;
  int do_setprio = 0;

  
#if 0 /* Using the realtime scheduler can lock up the system... */
  if (newprio <= -21) {
    struct sched_param sp;

    
    fprintf (fp, "runapp: Trying to set realtime priority\n");
    
    /* Try to max out the priority */
    sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
    
    if (sched_setscheduler (0, SCHED_FIFO, &sp) != 0) {
      sp.sched_priority = sched_get_priority_max (SCHED_RR);
      if (sched_setscheduler (0, SCHED_RR, &sp) != 0) {
        sp.sched_priority = sched_get_priority_max (SCHED_OTHER);
        if (sched_setscheduler (0, SCHED_OTHER, &sp) != 0) {
          fprintf (fp, "runapp: Could not get any realtime priority\n");
          fprintf (fp, "runapp: This is not a serious problem, but capture quality under high\n");
          fprintf (fp, "runapp: load could be improved by running as root.\n");
          do_setprio = 1;
        } else {
          fprintf (fp, "runapp: Got other realtime scheduler (%d)\n", sp.sched_priority);
        }
      } else {
        fprintf (fp, "runapp: Got Round Robin scheduler (%d)\n", sp.sched_priority);
      }
    } else {
      fprintf (fp, "runapp: Got FIFO scheduler (%d)\n", sp.sched_priority);
    }
	
  } else {
    do_setprio = 1;
  }
#else
  do_setprio = 1;
#endif
  
  if (do_setprio) {
    /* Use regular setpriority */
    res = setpriority (PRIO_PROCESS, 0, newprio);
    
    if (res) {
      fprintf (fp, "runapp: setprio() failed, errno=%d\n", errno);
    } else {
      fprintf (fp, "runapp: set new prio to %d\n", newprio);
    }

  }

  /* Done */
  return;
  
}
