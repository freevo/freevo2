#ifndef _FREEVO_PORTABLE_H_
#define _FREEVO_PORTABLE_H_

typedef unsigned char uint8;
typedef unsigned short int uint16;
typedef unsigned int uint32;
typedef int int32;
typedef float float32;

#define OK 0
#define ERROR -1

#define ARRAY_LENGTH(a)  (sizeof(a)/sizeof(a[0]))

#endif /* _FREEVO_PORTABLE_H_ */
