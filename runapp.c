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
#include <time.h>
#include <errno.h>
#include <linux/a.out.h>


#define LOG(str, args...) {                                             \
  static char tmp1[1000];                                               \
  static char tmp2[1000];                                               \
  sprintf (tmp1, str, ## args);                                         \
  sprintf (tmp2, "runapp: %s\n", tmp1);                                 \
  log_write (tmp2);                                                     \
}                                                                       

static FILE *log_fp = (FILE *) NULL;

static void runapp_setprio (int newprio);
static int check_runtime (void);
static char * get_preload_str (char *pFilename);
static void log_init (void);
static void log_close (void);
static void log_write (char *pBuf);


int
main (int ac, char *av[])
{
  sigset_t set;
  int i;
  int ac_idx = 1;               /* Inc. when args are "consumed". Ignore argv[0] */
  char *newav[1000];
  int newac = 0;
  char cmd_str[1000];
  char currdir[1000];
  int newprio;
  int got_runtime;
  int static_linked = 0;
  int use_preloads = 0;         /* Full runtime preloads */
  struct exec exec;
  FILE *fp;

  

  /* Set the umask to be ugo+rwx XXX security implications? */
  umask (0);
  
  /* Initialize the logfile stuff. Needed for the LOG() macro */
  log_init ();
  
  /* Dump some debug info to the logfile */
  LOG ("PATH = %s", getenv ("PATH"));
  LOG ("CWD = %s", getcwd (currdir, sizeof (currdir)));
  
  cmd_str[0] = 0;
  
  for (i = 0; i < ac; i++) {
    char tmp[256];


    sprintf (tmp, "%s ", av[i]);
    strcat (cmd_str, tmp);
    
    LOG ("av[%d] = '%s'", i, av[i]);
  }

  LOG ("Command: '%s'", cmd_str);
  
  /* Check for the full runtime. */
  got_runtime = check_runtime ();
  LOG ("runtime %s", got_runtime ? "FOUND" : "NOT FOUND");
  
  /* Got a valid commandstring? */
  if (ac < 2) {
    return (0);
  }

  /* Is the first arg the priority setting? */
  if (sscanf (av[ac_idx], "--prio=%d", &newprio) == 1) {
    
    /* Yes, set the process priority */
    runapp_setprio (newprio);

    ac_idx++;                   /* Skip this parameter for the exec() */

    /* Do we have any further args? */
    if (ac_idx >= ac) {
      LOG ("Malformed command line, exiting");
      exit (1);
    }
    
  }

  /*
   * Build the new command string (newav)
   */


  /* Make sure LD_PRELOAD is not set unless necessary */
  unsetenv ("LD_PRELOAD");
  
  /* Is the application "python"? Substitute for the runtime python,
   * or from the os.
   */
  if (strcmp (av[ac_idx], "python") == 0) {

    if (got_runtime) {
      /* Must use the runtime freevo_loader+freevo_python+preloads */
      
      newav[newac++] = "./runtime/dll/freevo_loader";
      newav[newac++] = "./runtime/apps/freevo_python";
      use_preloads = 1;
      ac_idx++;                 /* Consume av[] == python */

      LOG ("Using the runtime Python+loader");
      
    } else {
      /* XXX Should have special checks for Red Hat which uses python2 etc */
      newav[newac++] = "python";
      ac_idx++;   /* Consume av[] == python */

      /* Check if the python target is src/main.py, in which case
       * Gentoo preloads are used if present */
      if ((ac_idx < ac) && (strstr (av[ac_idx], "src/main.py") != (char *) NULL)) {
        use_preloads = 1;
      }
    }

  } else {

    /* No, it is a regular app. Check if it is in the runtime */
    if (strstr (av[ac_idx], "runtime/apps/") != (char *) NULL) {

      /* lets see is this app is staticly linked */
      /* this check is taken from lddlibc4.c of glibc-2.2.5 */

      /* First see whether this is really an a.out binary.  */
      fp = fopen (av[ac_idx], "rb");
      if (fp == NULL) {
        LOG ("cannot open `%s'", av[1]);
        exit (1);
      }

      /* Read the program header.  */
      if (fread (&exec, sizeof exec, 1, fp) < 1) {
        LOG ("cannot read header from `%s'", av[1]);
      }
      /* Test for the magic numbers.  */
      else if (N_MAGIC (exec) != ZMAGIC && N_MAGIC (exec) != QMAGIC
         && N_MAGIC (exec) != OMAGIC) {
        LOG ("Looks like a staticly linked executable");
        static_linked = 1;
      }

      /* We don't need the file open anymore.  */
      fclose (fp);

      if(!static_linked) {
        /* Yes, so the executable to start is the freevo_loader. */
        newav[newac++] = "./runtime/dll/freevo_loader";
        use_preloads = 1;

        LOG ("Runtime app, must use preloads"); 
      }
      else {
        /* Just a plain old app. It will be copied to newav[] below */
        LOG ("Static app, no preloads"); 
      }
    } else {
      /* Just a plain old app. It will be copied to newav[] below */
      LOG ("Regular app, no preloads"); 
    }

  }
  
  /* Check if LD_PRELOAD needs to be set to the full runtime preloads */
  if (use_preloads && !static_linked) {
    char *pPreloads;

    
    pPreloads = get_preload_str ("./runtime/preloads");
    LOG ("Setting LD_PRELOAD = '%s'", pPreloads);

    setenv ("LD_LIBRARY_PATH", "./runtime/dll", 1);
    setenv ("LD_PRELOAD", pPreloads, 1);
    
  }
  
  /* Copy the counted argv array to the NULL-terminated newav */
  for (i = ac_idx; i < ac; i++) {
    newav[newac++] = av[ac_idx++];
  }
  
  newav[newac++] = NULL;

  /* Debug */
  for (i = 0; newav[i] != NULL; i++) {
    LOG ("newav[%d] = '%s'", i, newav[i]);
  }
  
  /* Set up signals (turn off blocking!) */
  sigemptyset (&set);
  sigprocmask (SIG_SETMASK, &set, (sigset_t *) NULL);

  /* Must close all open file descriptors except std*, otherwise the exec-ed
   * app will get them! */
  log_close ();
  
  /* Overlay the child application */
  execvp (newav[0], newav);
  
  LOG ("failed! errno = %d", errno);
  
  exit (0);
  
}


static void
runapp_setprio (int newprio)
{
  int res;
  int do_setprio = 0;

  
#if 0 /* Using the realtime scheduler can lock up the system... */
  if (newprio <= -21) {
    struct sched_param sp;

    
    LOG ("Trying to set realtime priority\n");
    
    /* Try to max out the priority */
    sp.sched_priority = sched_get_priority_max(SCHED_FIFO);
    
    if (sched_setscheduler (0, SCHED_FIFO, &sp) != 0) {
      sp.sched_priority = sched_get_priority_max (SCHED_RR);
      if (sched_setscheduler (0, SCHED_RR, &sp) != 0) {
        sp.sched_priority = sched_get_priority_max (SCHED_OTHER);
        if (sched_setscheduler (0, SCHED_OTHER, &sp) != 0) {
          LOG ("Could not get any realtime priority\n");
          LOG ("This is not a serious problem, but capture quality under high\n");
          LOG ("load could be improved by running as root.\n");
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
      LOG ("setprio() failed, errno=%d\n", errno);
    } else {
      LOG ("set new prio to %d\n", newprio);
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
get_preload_str (char *pFilename)
{
  static char preload_str[10000];
  int fd;
  int len;
  

  LOG ("Reading LD_PRELOAD from file '%s'", pFilename);
  
  fd = open (pFilename, O_RDONLY);

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


static void
log_init (void)
{
  char logfile[256];
  time_t t;

  
  /* Can we log to the logdir (e.g. /var/log/freevo)? */
  sprintf (logfile, "%s/internal-runapp-%d.log", RUNAPP_LOGDIR, getuid());
  log_fp = fopen (logfile, "a");

  if (log_fp == (FILE *) NULL) {
    /* Nope, try /tmp/freevo instead */
    mkdir ("/tmp/freevo", 0777); /* Make sure the dir exists, ignore errors */
    sprintf (logfile, "/tmp/freevo/internal-runapp-%d.log", getuid());

    /* If this returns NULL, there is no other option. Just discard the logs... */
    log_fp = fopen (logfile, "a"); 

  }

  LOG ("\n\n***********************************************************\n");
  t = time ((time_t *) NULL);
  LOG ("Started on %s", ctime (&t));
}


static void
log_write (char *pBuf)
{
  if (log_fp == (FILE *) NULL) {
    return;
  }

  fprintf (log_fp, pBuf);
  fflush (log_fp);

  /* Done */
  return;
    
}


static void
log_close (void)
{
  if (log_fp != (FILE *) NULL) {
    fclose (log_fp);
  }

}

