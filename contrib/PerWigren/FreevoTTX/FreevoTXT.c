/*
 * Teletext handler for use in Freevo
 * by Per Wigren <wigren@open-source.nu>
 *
 * FIXME: Get version from commandline. Display error-text if bad version.
 * FIXME: Lock mutex everytime a global variable is accessed
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <libzvbi.h>

#include <X11/Xlib.h>
#include <Imlib2.h>

#define DEBUG 0
#define DBG(a) printf("DEBUG: %d\n",a);

#define ERROR strerror(errno)


#define		NOTHING			0
#define		HEADER			(1 << 1)
#define		BODY			(1 << 2)
#define		PAGE			(BODY|HEADER)

#define		FORCE_BODY		((1 << 16) | BODY)
#define		FORCE_HEADER	((1 << 17) | HEADER)
#define		FORCE_PAGE		(FORCE_BODY|FORCE_HEADER)


#include <linux/videodev.h>
#define		BTTV_VERSION			_IOR('v' , BASE_VIDIOCPRIVATE+6, int)
#define		CALC_VERSION(b,c,d)	(((b) << 16) + ((c) << 8) + (d))

vbi_capture*		cap;
vbi_raw_decoder*	par;
vbi_decoder*		vbi;
int					src_w, src_h;

vbi_bool			QUIT = FALSE;

int					fifo_in, fifo_out;

char				pgtxt[6];
char				timetxt[8]="HH:MM:XX";
vbi_pgno			pgno   = 0x100;
vbi_pgno			atpage = 0x100;
vbi_page			header;

int					updated = PAGE;
int					show    = PAGE;

int					reveal = FALSE;
int					hold = FALSE;
int					flash = TRUE;
int					body_flash = TRUE;
int					flash_on = TRUE;
int					seethrough = TRUE;
int					searching = TRUE;

int					header_alpha = 220, body_alpha = 175;
unsigned int		size_x=0, size_y=0;
int					zoompos=0;

vbi_rgba*			canvas_ttx;

pthread_mutex_t		mutex;



static void
sendstr(char *str) {
	if(DEBUG) printf("Sending: %s", str);
	write(fifo_out, str, strlen(str));
}

static void
quit(int err_num) {
	QUIT = TRUE;
	sendstr("HIDE\n");
	vbi_capture_delete(cap);
	exit(err_num);
}


static int
clear_page(int what) {
	int y=0,h=0;
	char str[50];

	switch(what) {
		case PAGE:
			y=0;
			h=size_y;
			break;
		case BODY:
			y=(int)(size_y*0.04);
			h=(int)((size_y*24)*0.04);
			break;
		case HEADER:
			y=0;
			h=(int)(size_y*0.04);
			break;
		default:
			fprintf(stderr,"Internal error: clear_page\n");
	}
	sprintf(str, "CLEAR %d %d 0 %d\n", size_x, h, y);
	sendstr(str);
}


static void
scale_rgba(void *old_data, void *new_data, int old_w, int old_h, int new_w, int new_h) {
	Imlib_Image image, scaled_image;

	image = imlib_create_image_using_data( old_w, old_h, old_data );
	imlib_context_set_image(image);
	imlib_context_set_anti_alias(1);
	imlib_image_set_has_alpha(1);

	scaled_image = imlib_create_cropped_scaled_image(0,0, old_w, old_h, new_w, new_h);
	imlib_context_set_image(scaled_image);

	memcpy( new_data, imlib_image_get_data(), new_w*4*new_h );
	
	imlib_free_image();
	imlib_context_set_image(image);
	imlib_free_image();
}


static int
blit_page(vbi_page *pg, int startrow, int endrow, int startcol, int endcol) {
	unsigned char *scaled_canvas;
	double scaleval_y = 10.0/250.0;
	double scaleval_x = 12.0/492.0;
	int   old_w=0, old_h=0, new_w=0, new_h=0, new_x, new_y=0, bufpos=0;
	char  str[50];

	vbi_draw_vt_page_region( pg, VBI_PIXFMT_RGBA32_LE, canvas_ttx,
	                         -1, startcol, startrow, (endcol-startcol), (endrow-startrow),
	                         reveal, (flash_on & flash) );

	old_w = (endcol-startcol) * 12;
	old_h = (endrow-startrow) * 10;
	new_w = ((endcol-startcol) * size_x * scaleval_x);
	new_x = startcol * size_x * scaleval_x;

	switch(zoompos) {
		case 0:		// Normal
			new_h = ((endrow-startrow) * size_y * scaleval_y);
			new_y = startrow * size_y * scaleval_y;
			bufpos = 0;
			break;
		case 1:		// Zoomed, top half
			scaleval_y *= 2;
			if(pg->rows > 1) {  // Body
				old_h = old_h/2 + 5;
				new_h =((pg->rows - startrow) * size_y * scaleval_y) / 2.0;
			} else {  // Header
				new_h = (pg->rows - startrow) * size_y * scaleval_y;
			}
			new_y = startrow * size_y * scaleval_y;
			bufpos = 0;
			break;
		case 2:		// Zoomed, bottom half
			scaleval_y *= 2;
			if(pg->rows > 1) {  // Body
				old_h = old_h/2 + 5;
				new_h = ((pg->rows - startrow) * size_y * scaleval_y) / 2.0;
				bufpos = (old_h-15)*old_w;
			} else {  // Header
				new_h = (pg->rows - startrow) * size_y * scaleval_y; // /2.0?
			}
			new_y = startrow * size_y * scaleval_y;
			break;
		default:
			fprintf(stderr, "Internal error: zoompos = %d\n", zoompos);
	}


	// Set all black pixels to transparent if seethrough
	if(seethrough) {
		int i, alpha=0;

		if     (startrow==0) alpha = header_alpha;
		else if(startrow==1) alpha = body_alpha;
		for( i=0; i < old_w*old_h; i++ )
			if( !(canvas_ttx[i] & 0x00FFFFFF) )	{ canvas_ttx[i] = (alpha << 24); }
	}

	// fprintf(stderr, "\nDEBUG: ow:%d oh:%d nw:%d nh:%d nx:%d ny:%d\n\n",
	//	old_w, old_h, new_w, new_h, new_x, new_y);

	scaled_canvas = malloc( new_w * new_h * 4 );
	scale_rgba( canvas_ttx + bufpos, scaled_canvas, old_w, old_h, new_w, new_h );

	sprintf(str, "RGBA32 %d %d %d %d 0 0\n", new_w, new_h, new_x, new_y);
	sendstr(str);
	write(fifo_out, scaled_canvas, new_w*new_h*4 );

	free(scaled_canvas);

	return TRUE;
}



static void
update_body(void)
{
	static vbi_page	body;
	vbi_page		new_body;
	int i;

	if(DEBUG) fprintf(stderr, "update_body()\n");

	updated ^= BODY;

	if( vbi_is_cached(vbi, pgno, VBI_ANY_SUBNO) ) searching=FALSE;

	if(!(show & BODY)) return;	// We're not supposed to show the body...

	if(updated & FORCE_BODY)	// Forced update.. for example changed alpha
		updated ^= FORCE_BODY;
	else {

		if(hold) return;

		if(! vbi_fetch_vt_page(vbi, &new_body, pgno, VBI_ANY_SUBNO, VBI_WST_LEVEL_3p5, 25, FALSE) )
			return;	// Could not fetch page

		// Compare with old page
		if( memcmp( &body.text[new_body.columns+1],
		            &new_body.text[new_body.columns+1],
					(sizeof(new_body.text)-new_body.columns-1)*sizeof(vbi_char) ) == 0 ) {
			// Not updated...
			vbi_unref_page(&new_body);
			return;
		}
		// Check if anything on the body is flashing
		body_flash=FALSE;
		for(i=41; i<(41*25) && !body_flash; i++) {
			if(new_body.text[i].flash) body_flash=TRUE;
		}
	
		vbi_unref_page(&body);
		body = new_body;
	}
	
	blit_page(&body, 1, 25, 0, body.columns);
}



static void
update_header(void)
{
	int i;
	vbi_page		new_header;
	int 			pagetofetch;

	if(DEBUG) fprintf(stderr, "update_header()\n");

	updated ^= HEADER;

	if(!(show & HEADER)) { updated ^= FORCE_HEADER; return;	}

	if(searching) pagetofetch = atpage;
	else pagetofetch = pgno;

	if(updated & FORCE_HEADER) {
		if(DEBUG) fprintf(stderr, "Header forced!\n");
		updated ^= FORCE_HEADER;
	} else {

		if(DEBUG) fprintf(stderr, "Trying to get new header!\n");
		if(! vbi_fetch_vt_page(vbi, &new_header, pagetofetch, VBI_ANY_SUBNO, VBI_WST_LEVEL_3p5, 1, FALSE) )
			{ printf("XXXXXXXXXXXXXXX\n"); return;	}// Could not fetch header for page

		if(DEBUG) fprintf(stderr, "Got new header!\n");

		// Compare with old header
#define STARTCOL (sizeof(pgtxt)+1)
#define LENGTH   ((new_header.columns-sizeof(timetxt)-1) - STARTCOL)
		if( memcmp( &header.text[STARTCOL],
		            &new_header.text[STARTCOL],
					(LENGTH)*sizeof(vbi_char) ) == 0 ) {
			// Header is not updated
			if(DEBUG) fprintf(stderr, "Header not updated!\n");
			vbi_unref_page(&new_header);
			return;
		}
		if(DEBUG) fprintf(stderr, "Header IS updated!\n");
		vbi_unref_page(&header);
		header = new_header;
	}

	for( i=0; i < 7; i++) {
		switch(i) {
			case 1:
			case 2:
			case 3:
				header.text[i].unicode = pgtxt[i-1];
				header.text[i].foreground = 2;
				break;
			case 5:
				if(hold) {
					header.text[i].unicode = 'H';
					header.text[i].foreground = 1;
					header.text[i].flash = 1;
				} else header.text[i].unicode = ' ';
				break;
			case 6:
				if(reveal) {
					header.text[i].unicode = 'R';
					header.text[i].foreground = 6;
				} else header.text[i].unicode = ' ';
				break;
			default:
				header.text[i].unicode = ' ';
				break;
		}
	}
	for( i=32; i <= 41; i++) {
		switch(i-32) {
			case 8:
				header.text[i].unicode = ' ';
				break;
			case 5:
				header.text[i].flash = 1;
			default:
				header.text[i].unicode = timetxt[i-32];
				break;
		}
	}

	blit_page(&header, 0, 1, 0, 41 );
}


static void
pgadd(int diff) {
	int  dec, nhex;
	char tmp[10];

	sprintf(tmp, "%x", pgno);
	dec = strtol(tmp,NULL,10);
	dec += diff;
	sprintf(tmp, "%d", dec);
	nhex = strtol(tmp,NULL,16);

	printf("old = %x/%d, new = %x/%d\n", pgno, pgno, nhex, nhex);

	if( (nhex < 0x100) || (nhex > 0x999) ) return;
	else { printf("pgno = new = '%s'\n", tmp);
			pgno = strtol(tmp,NULL,16);
	}
}

static void
cmd_page(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_page: %s\n", arg);

	if		( strncmp(arg, "NEXT", 4)==0 ) pgadd(1);
	else if ( strncmp(arg, "PREV", 4)==0 ) pgadd(-1);
	else if ( (strtol(arg,NULL,16) < 0x100) | (strtol(arg,NULL,16) > 0x999) ) {
		printf("Bad argument for PAGE: %s\n", arg);
		printf("Valid arguments are NEXT, PREV or a number between 100 and 999!\n");
		return;
	} else pgno = strtol(arg,NULL,16);

	printf("DEBUG: pgno = %03x\n", pgno);

	sprintf( pgtxt, "%03x", pgno);

	searching = TRUE;
	updated |= BODY;
}

static void
cmd_button(char *arg) {
	static char page[3]="   ";
	static int  pos=0;
	char		num;

	if(DEBUG) printf("DEBUG: in cmd_button: %s\n", arg);

	num = arg[0];

	if( (num < '0') || (num > '9') ) {
		printf("Bad argument for BUTTON: %s\n", arg);
		printf("Not a number!");
		return;
	}
	
	if( (pos==0) & (num=='0') ) {
		printf("The first number has to be 1-9!\n");
		return;
	}

	page[pos] = num;
	pos++;

	strncpy( pgtxt, page, 3 );

	if( pos==3 ) {
		pos=0;
		cmd_page(page);
		strncpy( page, "   ", 3);
	} else {
		updated |= FORCE_HEADER;
	}
}

static void
cmd_reveal(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_reveal: %s\n", arg);

	if		( strncmp(arg, "ON",     2)==0 )	reveal = TRUE;
	else if	( strncmp(arg, "OFF",    3)==0 )	reveal = FALSE;
	else if	( strncmp(arg, "TOOGLE", 6)==0 )	{ if(reveal) reveal=FALSE; else reveal=TRUE; }
	else {
		printf("Bad argument for REVEAL: %s\n", arg);
		printf("Valid arguments are: ON, OFF, TOGGLE\n");
		return;
	}
	
	if(reveal)	pgtxt[5]='R';
	else		pgtxt[5]=' ';

	updated |= FORCE_BODY;
}

static void
cmd_hold(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_hold: %s\n", arg);

	if		( strncmp(arg, "ON",     2)==0 )	hold = TRUE;
	else if	( strncmp(arg, "OFF",    3)==0 )	hold = FALSE;
	else if	( strncmp(arg, "TOOGLE", 6)==0 )	{ if(hold) hold=FALSE; else hold=TRUE; }
	else {
		printf("Bad argument for HOLD: %s\n", arg);
		printf("Valid arguments are: ON, OFF, TOGGLE\n");
		return;
	}

	if(hold)	pgtxt[6]='H';
	else		pgtxt[6]=' ';

	updated |= FORCE_HEADER;
}

static void
cmd_alpha(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_alpha: %s\n", arg);
	
	if		( strncmp(arg, "ON",     2)==0 ) seethrough = TRUE;
	else if	( strncmp(arg, "OFF",    3)==0 ) seethrough = FALSE;
	else if ( strncmp(arg, "TOGGLE", 6)==0 ) { if(seethrough) seethrough=FALSE; else seethrough=TRUE; }
	else if ( arg[0]=='H' ) {
		if( (atoi(arg+1) >= 0) && (atoi(arg+1) <= 255) )	header_alpha = atoi(arg+1);
	}
	else if ( arg[0]=='B' ) {
		if( (atoi(arg+1) >= 0) && (atoi(arg+1) <= 255) )	body_alpha = atoi(arg+1);
	}
	else {
		printf("Bad argument for ALPHA: %s\n", arg);
		printf("Valid arguments are: ON, OFF, TOGGLE, H<num>, B<num>\n");
		return;
	}

	if(seethrough)
		sendstr("ALPHA 0 0 0 0 0\n");
	else
		sendstr("OPAQUE\n");
}

static void
cmd_show(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_show: %s\n", arg);

	if		( strncmp(arg, "BODY",   4)==0 )	{ show |= BODY;   updated |= FORCE_BODY; }
	else if	( strncmp(arg, "HEADER", 6)==0 )	{ show |= HEADER; updated |= FORCE_HEADER; }
	else if	( strncmp(arg, "PAGE",   4)==0 )	{ show |= PAGE;   updated |= FORCE_PAGE; }
	else {
		printf("Bad argument for SHOW: %s\n", arg);
		printf("Valid arguments are: BODY, HEADER, PAGE\n");
	}
}

static void
cmd_hide(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_hide: %s\n", arg);

	if		( strncmp(arg, "BODY",   4)==0 )	{ show ^= BODY;   clear_page(BODY); }
	else if	( strncmp(arg, "HEADER", 6)==0 )	{ show ^= HEADER; clear_page(HEADER); }
	else if ( strncmp(arg, "PAGE",   4)==0 )	{ show ^= PAGE;   clear_page(PAGE); }
	else {
		printf("Bad argument for HIDE: %s\n", arg);
		printf("Valid arguments are: BODY, HEADER, PAGE\n");
	}
}

static void
cmd_flash(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_flash: %s\n", arg);

	if		( strncmp(arg, "ON",     2)==0 )	flash = TRUE;
	else if	( strncmp(arg, "OFF",    3)==0 )	flash = FALSE;
	else if	( strncmp(arg, "TOOGLE", 6)==0 )	{ if(flash) flash=FALSE; else flash=TRUE; }
	else {
		printf("Bad argument for FLASH: %s\n", arg);
		printf("Valid arguments are: ON, OFF, TOGGLE\n");
		return;
	}

	updated = FORCE_PAGE;
}

static void
cmd_zoom(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_zoom: %s\n", arg);

	if		( strncmp(arg, "NORMAL", 6)==0 )	zoompos=0;
	else if	( strncmp(arg, "TOP",    3)==0 )	zoompos=1;
	else if	( strncmp(arg, "BOTTOM", 6)==0 )	zoompos=2;
	else if ( strncmp(arg, "NEXT",   4)==0 ) { zoompos++; if(zoompos > 2) zoompos=0; }
	else {
		printf("Bad argument for ZOOM: %s\n", arg);
		printf("Valid arguments are: NORMAL, TOP, BOTTOM, NEXT\n");
		return;
	}

	updated = FORCE_PAGE;
}


static void
cmd_quit(char *arg) {
	if(DEBUG) printf("DEBUG: in cmd_quit: %s\n", arg);

	QUIT = TRUE;
}



static void
ttx_handler(vbi_event* ev, void *unused) {
	pthread_mutex_lock(&mutex);
		if(searching) {
			atpage = ev->ev.ttx_page.pgno;
			updated |= HEADER;
		}

		if( ev->ev.ttx_page.header_update ) {
			printf("DEBUG: got header_update..\n");
			updated |= HEADER;
		}
		if( ev->ev.ttx_page.pgno == pgno ) {
			printf("DEBUG: UPDATE BODY!!\n");
			searching = FALSE;
			updated |= PAGE;
		}	
	pthread_mutex_unlock(&mutex);
	return;
}



static void*
vbi_fetch_thread(void* unused) {
	int					lines;
	double				timestamp;
	struct timeval		tv;
	uint8_t				*raw;
	vbi_sliced			*sliced;

	tv.tv_sec=5; tv.tv_usec=0;	// Timeout for VBI device

	raw = malloc(src_w * src_h);
	sliced = malloc(sizeof(vbi_sliced) * src_h);

	if(!(raw && sliced)) {
		fprintf(stderr, "Couldn't allocate memory for buffers: %s\n", ERROR);
		QUIT = TRUE;
	}

	while(!QUIT) {
		switch( vbi_capture_read(cap, raw, sliced, &lines, &timestamp, &tv) ) {
			case -1:
				fprintf(stderr, "VBI read error: %s\n", ERROR);
				quit(EXIT_FAILURE);
			case 0:
				fprintf(stderr, "VBI read timeout\n");
				quit(EXIT_FAILURE);
			case 1:
				break;
		}
		vbi_decode(vbi, sliced, lines, timestamp);
	}
	free(raw);
	free(sliced);
	
	return unused;	// Is there a better way to get rid of this warning?
}



static int
_read_cmd(int fd, char *cmd, char *args) {
	int done=FALSE, pos=0;
	char tmp;

	while(!done) {
		if(! read( fd, &tmp, 1 ) ) return FALSE;
		if( (tmp>='A' && tmp<='Z') || (tmp>='0' && tmp<='9') )
			cmd[pos]=tmp;
		else if(tmp == ' ') {
			cmd[pos]='\0';
			done=TRUE;
		}
		else if(tmp == '\n') {
			cmd[pos]='\0';
			args[0]='\0';
			return TRUE;
		}
		if(pos++>20) {
			cmd[0]='\0';
			return TRUE;
		}
	}
	done=FALSE; pos=0;
	while(!done) {
		if(! read( fd, &tmp, 1 ) ) return FALSE;
		if( (tmp >= ' ') && (pos<100) ) args[pos]=tmp;
		else {
			args[pos]='\0';
			done=TRUE;
		}
		pos++;
	}
	return TRUE;
}




static void
mainloop(void) {
	char cmd[1000];
	char arg[1000];
	int update_what = 0;
	struct tm tm;
	time_t now;

	while(!QUIT) {
		int got_data=FALSE;

		if(now != time(NULL)) {
			now=time(NULL);
			if(flash_on) flash_on=FALSE;
			else flash_on=TRUE;
			tm = *(localtime(&now));
			strftime(timetxt, 10, "%H:%M:%S", &tm);
			updated |= FORCE_HEADER;
			if(body_flash) updated |= FORCE_BODY;
		}
		
		
		if( ioctl( fifo_in, FIONREAD, &got_data) ) {
			fprintf(stderr, "ioctl() error in input-FIFO: %s\n", ERROR);
			quit(EXIT_FAILURE);
		} else if(got_data) {
			// Yeah! We've got some input! ;-)

			// fscanf(fifo_in, "%s %s\n", cmd, arg);

			_read_cmd(fifo_in, cmd, arg);
			
			fprintf(stderr, "DEBUG: Got command \"%s\" with arg \"%s\"!\n", cmd, arg);

			if      ( strncmp(cmd, "BUTTON",	6)==0 ) cmd_button(arg);
			else if ( strncmp(cmd, "PAGE",		4)==0 ) cmd_page(arg);
			else if ( strncmp(cmd, "REVEAL",	6)==0 ) cmd_reveal(arg);
			else if ( strncmp(cmd, "HOLD",		4)==0 ) cmd_hold(arg);
			else if ( strncmp(cmd, "ALPHA",		5)==0 ) cmd_alpha(arg);
			else if ( strncmp(cmd, "SHOW",		4)==0 ) cmd_show(arg);
			else if ( strncmp(cmd, "HIDE",		4)==0 ) cmd_hide(arg);
			else if ( strncmp(cmd, "UPD",		3)==0 ) ; // FIXME
			else if ( strncmp(cmd, "FLASH",     5)==0 ) cmd_flash(arg);
			else if ( strncmp(cmd, "ZOOM",      4)==0 ) cmd_zoom(arg);
			else if ( strncmp(cmd, "QUIT",		4)==0 ) cmd_quit(arg);
			else
				fprintf(stderr, "Unknown command \"%s\"!\n", cmd);
		}

		pthread_mutex_lock(&mutex);
			update_what = updated;
		pthread_mutex_unlock(&mutex);

		if ( update_what & HEADER ) update_header();
		if ( update_what & BODY   ) update_body();
 
		usleep(20000);		// Sleep for a fraction of a second ;)
	}
}






int
main(int argc, char **argv)
{
	char		*errstr;
	pthread_t	t_fetch;
	unsigned int bttv_version;

	unsigned int services = VBI_SLICED_VBI_525 | VBI_SLICED_VBI_625 |
	                        VBI_SLICED_TELETEXT_B | VBI_SLICED_CAPTION_525 |
	                        VBI_SLICED_CAPTION_625 | VBI_SLICED_VPS |
	                        VBI_SLICED_WSS_625 | VBI_SLICED_WSS_CPR1204;

	if(argc < 6) {
		printf("Usage: freevo_teletext <vbi-device> <startpage> <input-fifo> <output-fifo> <x> <y>\n");
		quit(0);
	}

	if(! (fifo_in = open(argv[3], O_RDWR)) ) {
		if( (mkfifo(argv[3], 0600) < 0 ) ) {
			fprintf(stderr, "Error opening input-FIFO %s: %s\n", argv[3], strerror(errno));
			quit(EXIT_FAILURE);
		} else fifo_in = open(argv[3], O_RDWR);
	}
	if(! (fifo_out = open(argv[4], O_RDWR|O_APPEND)) ) {
		fprintf(stderr, "Error opening output-FIFO %s: %s\n", argv[4], strerror(errno));
		quit(EXIT_FAILURE);
	}

	pgno = strtol(argv[2], NULL, 16);
	if( (pgno<0x100) || (pgno>0x999) ) pgno=0x100;
	sprintf(pgtxt, "%03x   ", pgno);

	size_x = atoi(argv[5]);
	size_y = atoi(argv[6]);

	// Init VBI
	vbi = vbi_decoder_new();
	vbi_event_handler_register(vbi, VBI_EVENT_TTX_PAGE, ttx_handler, NULL);

	// Init VBI-device
	cap = vbi_capture_v4l2_new(argv[1], 5, &services, -1, &errstr, TRUE);
	if(!cap) {
		cap = vbi_capture_v4l_new(argv[1],
		                          625 /* scanning.. FIXME: Is this always 625? */,
		                          &services, -1, &errstr, TRUE);
	}
	if(!cap) {
		fprintf(stderr, "Can't open device %s: %s!\n", argv[1], errstr);
		quit(EXIT_FAILURE);
	}

	bttv_version = ioctl( vbi_capture_fd(cap), BTTV_VERSION, 0 );
	printf("BTTV-driver version: %d.%d.%d\n", ( bttv_version >> 16 ) & 0xff,
                                              ( bttv_version >>  8 ) & 0xff,
	                                          ( bttv_version >>  0 ) & 0xff );

	par = vbi_capture_parameters(cap);
	src_w = par->bytes_per_line;
	src_h = par->count[0] + par->count[1];


	// Allocate canvas for graphics
	canvas_ttx = malloc( sizeof(vbi_rgba)*(41*25*12*10) );
	if(!canvas_ttx) {
		fprintf(stderr, "Failed to allocate canvas: %s\n", ERROR);
		quit(EXIT_FAILURE);
	}

	if( pthread_mutex_init(&mutex, NULL) < 0 ) {
		fprintf(stderr, "Couldn't create mutex; %s\n", ERROR);
		quit(EXIT_FAILURE);
	}

	if( pthread_create( &t_fetch, NULL, vbi_fetch_thread, NULL) != 0 ) {
		fprintf(stderr, "Couldn't create fetch-thread: %s\n", ERROR);
		quit(EXIT_FAILURE);
	}

	mainloop();

	pthread_join(t_fetch, NULL);
	pthread_mutex_destroy(&mutex);
	close(fifo_in);
	close(fifo_out);
	free(canvas_ttx);

	quit(EXIT_SUCCESS);
	return TRUE;
}
