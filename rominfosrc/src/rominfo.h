/*
--------------------------------------------------------------------------
 * ROMInfo v1.02 (6 January 2001)
 * Written by Logiqx (http://www.logiqx.com)
 *
 * A simple little utility for identifying emulators that use a
specified ROM
 *
-------------------------------------------------------------------------- 
*/

/* --- Function prototypes --- */

struct crc *load_crcs(int, char **);
unsigned long calc_file_crc32(char *, unsigned long);

int scan_dir(char *, struct crc *);
int scan_dat(char *, struct crc *);

/* --- Size declarations --- */

#define BUFFER_SIZE 1024
#define NAME_LENGTH 80

#define MAX_CRCS 500

#define BLOCK_SIZE 65536

/* --- Structures --- */


struct crc
{
	char *fn;
	unsigned long crc;
};

/* --- Macros --- */

#define CALLOC(PTR, NUMBER, TYPE) \
if (!(PTR=calloc(NUMBER, sizeof(struct TYPE)))) \
{ \
	printf("Not enough memory\n"); \
	errflg++; \
}

#define CFREE(PTR) \
if (PTR) \
{ \
	cfree(PTR);\
}

#define FOPEN(PTR, FN, MODE) \
if (!(PTR=fopen(FN, MODE))) \
{ \
	printf("Error opening %s for mode '%s'\n", FN, MODE); \
	errflg++; \
}

#define FCLOSE(PTR) \
if (PTR) \
{ \
	fclose(PTR); \
	PTR=0; \
}

#define REMOVE_CR_LF(ST) \
while (ST[strlen(ST)-1]==10 || ST[strlen(ST)-1]==13) \
	ST[strlen(ST)-1]='\0';

#define GET_TOKEN(TOKEN, ST_PTR) \
{ \
	int token_idx=0; \
\
	while (*ST_PTR==' ' || *ST_PTR=='	') \
		ST_PTR++; \
\
	if (*ST_PTR=='"') \
	{ \
		ST_PTR++; \
		while (*ST_PTR!='"' && *ST_PTR!='\0') \
		{ \
			TOKEN[token_idx++]=*ST_PTR; \
			ST_PTR++; \
		} \
		TOKEN[token_idx]='\0';  \
		if (*ST_PTR!='\0') \
			ST_PTR++; \
	} \
	else \
	{ \
		while (*ST_PTR!=' ' && *ST_PTR!='	' && *ST_PTR!='\0') \
		{ \
			TOKEN[token_idx++]=*ST_PTR; \
			ST_PTR++; \
		} \
		TOKEN[token_idx]='\0';  \
	} \
}


