#!/usr/bin/perl
#
#
# This is a fairly dumb program. It doesn't understand the complete freevo_config.py file, 
# just the actual remote lines, so you have to cut and paste the lines BETWEEN RC_CMDS = { and
# the closing brace. 
#
# Since the assumption is that you'd only need to run it once or so, I'm not going to spend
# too much time on it...
# 
# Usage: freevo2lirc.pl <infile> > <lircrc>
#


$filename = $ARGV[0];

open (FILE, $filename) or die "Can't open file: $filename";

while (<FILE>)
	{
	($lircd_code,$freevo_code) = split(/:/,$_);
	$lircd_code =~ s/\'//g;
	$freevo_code =~ s/\'//g;
	$freevo_code =~ s/,//;
	$lircd_code =~ s/^\s*//;
	$freevo_code =~ s/^\s*//;
	
	chomp($lircd_code);
	chomp($freevo_code);
	print "begin\n";
	print "    prog = freevo\n";
	print "    button = $lircd_code\n";
	print "    config =  $freevo_code\n";
	print "end\n";
	print "\n";
	}

