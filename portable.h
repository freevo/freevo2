#ifndef _FREEVO_PORTABLE_H_
#define _FREEVO_PORTABLE_H_

typedef unsigned char uint8;
typedef unsigned short int uint16;
typedef unsigned int uint32;
typedef int int32;
typedef float float32;

#define OK 0
#define ERROR -1

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define ARRAY_LENGTH(a)  (sizeof(a)/sizeof(a[0]))

#define DBG(str, args...) {                                                   \
  char tmp[100000] ;                                                          \
  sprintf (tmp, str, ## args);                                                \
  printf ("%s:%s():%d: %s\n", __FILE__, __FUNCTION__, __LINE__, tmp);         \
}

#define EXIT(str, args...) {                                                  \
  char tmp[100000] ;                                                          \
  sprintf (tmp, str, ## args);                                                \
  printf ("%s:%s():%d: %s\n", __FILE__, __FUNCTION__, __LINE__, tmp);         \
  exit (1);                                                                   \
}


#endif /* _FREEVO_PORTABLE_H_ */
