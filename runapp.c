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
 
#include <fcntl.h>
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
static int check_runtime (void);
static char * get_preload_str (void);


int
main (int ac, char *av[])
{
  sigset_t set;
  int i;
  FILE *fp;
  int ac_idx = 1;               /* Inc. when args are "consumed". Ignore argv[0] */
  char *newav[1000];
  int newac = 0;
  struct stat statbuf;
  char logfile[256];
  char cmd_str[1000];
  char currdir[1000];
  int newprio;
  int got_runtime;


  /* Does the logdir exist? */
  if (!stat (RUNAPP_LOGDIR, &statbuf)) {
    /* XXX Also check that it is writeable for this uid */
    sprintf (logfile, "%s/internal-runapp-%d.log", RUNAPP_LOGDIR, getuid());
  } else {
    /* No, log to the /tmp/freevo dir instead */
    sprintf (logfile, "/tmp/freevo/internal-runapp-%d.log", getuid());
    mkdir ("/tmp/freevo", 0777); /* Make sure the dir exists, ignore errors */
  }
  
  fp = fopen (logfile, "a");
  
  /* Dump some debug info to the logfile */
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
  
  /* Check for the full runtime. */
  got_runtime = check_runtime ();
  fprintf (fp, "runapp: runtime %s\n", got_runtime ? "FOUND" : "NOT FOUND");
  
  /* Add check for Gentoo too, different handling from the runtime */
  /* XXX */

  /* Got a valid commandstring? */
  if (ac < 2) {
    return (0);
  }

  /* Is the first arg the priority setting? */
  if (sscanf (av[ac_idx], "--prio=%d", &newprio) == 1) {
    
    /* Yes, set the process priority */
    runapp_setprio (newprio, fp);

    ac_idx++;                   /* Skip this parameter for the exec() */
  }

  /*
   * Build the new command string (newav)
   */
  
  /* Do we need to use the freevo_loader (ld.so) from the runtime? */
  if (got_runtime) {
    char *pPreloads;

    
    /* Yes, so the executable to start is the freevo_loader.
     * This must be newav[0] */
    newav[newac++] = "./runtime/dll/freevo_loader";
    //newav[newac++] = "--library-path";
    //newav[newac++] = "./runtime/dll";

    pPreloads = get_preload_str();
    fprintf (fp, "runapp: LD_PRELOAD = '%s'\n", pPreloads);

    setenv ("LD_PRELOAD", pPreloads, 1);
    
  }
  
  /* Is the application "python"? Substitute for the runtime python,
   * or from the os.
   * The freevo_loader will be in newav[0] if present
   */
  if (strcmp (av[ac_idx], "python") == 0) {

    if (got_runtime) {
      newav[newac++] = "./runtime/apps/freevo_python";
      ac_idx++;
    } else {
      /* XXX Should have special checks for Red Hat which uses python2 etc */
      newav[newac++] = "python";
      ac_idx++;
    }
  }

  /* Copy the counted argv array to the NULL-terminated newav */
  for (i = ac_idx; i < ac; i++) {
    newav[newac++] = av[ac_idx++];
  }
  
  newav[newac++] = NULL;

  /* Debug */
  for (i = 0; newav[i] != NULL; i++) {
    fprintf (fp, "runapp: newav[%d] = '%s'\n", i, newav[i]);
  }
  
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


/* Is there a runtime here? */
static int
check_runtime (void)
{
  struct stat statbuf;


  /* The freevo startscript must cd to the freevo dir for this to work */
  if ((!stat ("./runtime/dll/freevo_loader", &statbuf)) &&
      (!stat ("./runtime/apps/freevo_python", &statbuf))) {
    return 1;
  } else {
    return 0;
  }
  
}

  
static char *
get_preload_str (void)
{
  static char preload_str[10000];
  int fd;
  int len;
  

  fd = open ("./runtime/preloads", O_RDONLY);

  if (fd < 0) {
    close (fd);
    return ("");
  }

  len = read (fd, preload_str, sizeof (preload_str) - 1);

  if (len < 1) {
    close (fd);
    return ("");
  }

  preload_str[len-1] = 0;         /* Remove the trailing \n */

  return preload_str;

}
