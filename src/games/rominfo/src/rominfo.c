/*
--------------------------------------------------------------------------
 * ROMInfo - Written by Logiqx (http://www.logiqx.com)
 *
 * A simple little utility for identifying emulators that use a specified ROM
 *
 *
 * Modded 2002 for Freevo
-------------------------------------------------------------------------- 
*/

#define ROMINFO_VERSION "v1.03freevo"
#define ROMINFO_DATE "22 August 2002"

/* --- The standard includes --- */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
#include <sys/stat.h>

#include "mame/unzip.h"
#include "rominfo.h"

int main(int argc, char **argv)
{
	struct crc *crcs=0;
	char dir[BUFFER_SIZE];
	int errflg = 0;

	if (argc<2)
	{
		printf("Usage: %s rom.zip\n\n", basename(argv[0]));
		errflg++;
	}

	if (strchr(argv[0], '/'))
	{
		strcpy(dir, argv[0]);
		*strrchr(dir, '/')='\0';
		chdir(dir);
	}

	if (!errflg)
	{
		if (crcs=load_crcs(argc, argv))
		{
			if (crcs[0].crc)
				errflg=scan_dir("rominfodats", crcs);
			else
				printf("ERROR: Not a valid rom\n");
			free_crcs(crcs);
		}
	}
	return(errflg);
}

/*
--------------------------------------------------------------------------
 * Read CRCs from ZIP file
 *
-------------------------------------------------------------------------- 
*/

struct crc *load_crcs(int argc, char **argv)
{
	ZIP *zip;
	struct zipent *zipent;
	struct stat buf;

	struct crc *crcs=0;
	int num_crcs=0;
	int errflg=0;
	int i;

	CALLOC(crcs, MAX_CRCS+1, crc)

	for (i=1; !errflg && i<argc; i++)
	{
		if (stat(argv[i], &buf) == 0)
		{
			if (strstr(argv[i], ".zip"))
			{
				/* --- Treat as a ZIP --- */
				if (zip=openzip(argv[i]))
				{
					while ((!errflg) && (zipent=readzip(zip)))
					{
						if (num_crcs<MAX_CRCS)
						{
							crcs[num_crcs].fn=argv[i];
							crcs[num_crcs++].crc=zipent->crc32;
						}
						else
						{
							printf("Too many files in ZIP - max=%d\n", MAX_CRCS);
							errflg++;
						}
					}
					closezip(zip);
				}
				else {
					errflg++;
				}
			}
			else {
				errflg++;
			}
		}
		else {
			errflg++;
		}
	}
	return(crcs);
}

int free_crcs(struct crc *crcs)
{
	CFREE(crcs)
}

/*
--------------------------------------------------------------------------
 * CRC32 calculation of individual file - uses zlib
 *
-------------------------------------------------------------------------- 
*/

unsigned long calc_file_crc32(char *fn, unsigned long fs)
{
	FILE *in;
	unsigned char buf[BLOCK_SIZE];
	unsigned long crc;
	unsigned long i=fs;
	int errflg=0;

	FOPEN(in, fn, "rb")
	crc = crc32(0, NULL, 0);

	while (!errflg && i)
	{
		if (i>=BLOCK_SIZE)
		{
			fread(buf, BLOCK_SIZE, 1, in);
			crc = crc32(crc, buf, BLOCK_SIZE);
			i-=BLOCK_SIZE;
		}
		else
		{
			fread(buf, i, 1, in);
			crc = crc32(crc, buf, i);
			i=0;
		}
	}

	FCLOSE(in)
	return(crc);
}

/*
--------------------------------------------------------------------------
 * Inidividual Directory scan
 *
-------------------------------------------------------------------------- 
*/

int scan_dir(char *dir, struct crc *crcs)
{
	DIR *dirp;                                    
	struct dirent *direntp;                       
	struct stat buf;

	char fn[BUFFER_SIZE+1];
	if (!(dirp=opendir(dir)))
	{
		printf("Error: unable to read %s\n", dir);
	}

	while (dirp && ((direntp = readdir(dirp)) != NULL))
	{
		sprintf(fn, "%s/%s", dir, direntp->d_name);
		if (stat(fn, &buf) == 0)
		{
			if (!(buf.st_mode & S_IFDIR))
			{
				if (strstr(fn, ".dat"))
				{
					scan_dat(fn, crcs);
				}
			}
			else
			{
				if (fn[strlen(fn)-1]!='.')	/* Don't try . or .. entries */
					scan_dir(fn, crcs);
			}
		}
		else
		{
			printf("Error getting attributes of %s\n", direntp->d_name);
		}
	}

	if (dirp)
	{
		closedir(dirp);                               
	}

	return(0);                                   
}

/*
--------------------------------------------------------------------------
 * Dat scan - Tokenised parser code ripped from CAESAR
 *
-------------------------------------------------------------------------- 
*/

int scan_dat(char *fn, struct crc *crcs)
{
	FILE *in;

	char st[BUFFER_SIZE], token[BUFFER_SIZE];
	char *st_ptr;

	char emu[NAME_LENGTH+1];
	char game[NAME_LENGTH+1];
	char rom[NAME_LENGTH+1];
	char description[NAME_LENGTH+1];
	char manufacturer[NAME_LENGTH+1];
	char year[NAME_LENGTH+1];

	char guessgame[NAME_LENGTH+1];
	char guessrom[NAME_LENGTH+1];
	char guessdescription[NAME_LENGTH+1];
	char guessmanufacturer[NAME_LENGTH+1];
	char guessyear[NAME_LENGTH+1];
	
	unsigned long rom_crc;
	int partialmatch=0;
	int fullmatch=0;
	int printed_fn=0;
	int rom_fn=0;
	int printed_game=0;
	int i, errflg=0;

	strcpy(emu, strrchr(fn, '/')+1);
	*strrchr(emu, '.')='\0';

	FOPEN(in, fn, "r")

	while (!errflg && fgets(st, BUFFER_SIZE, in))
	{
		REMOVE_CR_LF(st)

		st_ptr=st;
		GET_TOKEN(token, st_ptr)

		if (!strcmp(token, "name"))
		{
			GET_TOKEN(game, st_ptr)
			if (printed_game)
			{
				if (printed_fn == rom_fn-1) {
					fullmatch = 1;
					break; // from the while loop we found a match so why search more?
				} else if (printed_fn) {
					if (printed_fn > partialmatch) {
						strcpy(guessgame,game);
						strcpy(guessdescription,description);
						strcpy(guessmanufacturer,manufacturer);
						strcpy(guessyear,year);
						partialmatch = printed_fn;
					}
				}
				printed_fn = 0;
			}
			printed_game=0;
		}

		if (!strcmp(token, "description"))
			GET_TOKEN(description, st_ptr)

		if (!strcmp(token, "year"))
			GET_TOKEN(year, st_ptr)

		if (!strcmp(token, "manufacturer"))
			GET_TOKEN(manufacturer, st_ptr)

		if (!strcmp(token, "rom"))
		{
			st_ptr=st;

			GET_TOKEN(token, st_ptr) /* skip rom token */
			GET_TOKEN(token, st_ptr) /* skip bracket */
			GET_TOKEN(token, st_ptr)

			while (*token)
			{
				if (!strcmp(token, "name"))
					GET_TOKEN(rom, st_ptr)

				if (!strcmp(token, "merge")) {
					GET_TOKEN(token, st_ptr)
					token[0]='\0';
				}

				if (!strcmp(token, "size")) {
					GET_TOKEN(token, st_ptr)
					token[0]='\0';
				}

				if (!strcmp(token, "crc") || !strcmp(token, "crc32"))
				{
					GET_TOKEN(token, st_ptr)
					sscanf(token, "%08lx", &rom_crc);
					rom_fn=0;
					for (i=0; i<MAX_CRCS && crcs[i].crc; i++)
					{
						rom_fn++;
						if (rom_crc==crcs[i].crc)
						{
							if (!printed_game) {
								printed_game++;
							}

							if (crcs[i].fn) {
								printed_fn++;
							}
						}
					}
				}

				GET_TOKEN(token, st_ptr)
			}
		}
	}
	FCLOSE(in)
	if (fullmatch) {
		printf("KNOWN: There was a full match\n\n");
		printf("GAME:         %s\n", game);
		printf("DESCRIPTION:  %s\n", description);
		printf("MANUFACTURER: %s\n", manufacturer);
		printf("YEAR:         %s\n", year);
	} else if (partialmatch) {
		printf("PARTIAL: There was a partial match\n\n");
		printf("GAME:         %s\n", guessgame);
		printf("DESCRIPTION:  %s\n", guessdescription);
		printf("MANUFACTURER: %s\n", guessmanufacturer);
		printf("YEAR:         %s\n", guessyear);
	}
}
