#include "fb.c"
// This small program unlocks the VT so that SDL 
// with fbcon or directfb can use it. 


int main (void)
{
	tty_enable();
	return 0;
}
