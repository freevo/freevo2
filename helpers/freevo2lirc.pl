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


open (FILE, "/etc/lircd.conf") or die "Can't open file: /etc/lircd.conf";
$in = 0;
while (<FILE>) {
  if ($in && (/^[ \t]*([^ \t]*)[ \t]*0x[0-9a-f]/)) {
    $keys{$1} = uc($1)
  }
  $in = 1 if (/begin codes/i);
}
close FILE;

$filename = $ARGV[0];

open (FILE, $filename) or die "Can't open file: $filename";


$in = 0;
while (<FILE>) {
  $in = 0 if (/}/i);
  $in = 1 if (/RC_CMDS *=/i);
  if ($in && (/:/)) {
    ($lircd_code,$freevo_code) = split(/:/,$_);
    $lircd_code =~ s/\'//g;
    $freevo_code =~ s/\'//g;
    $freevo_code =~ s/,//;
    $lircd_code =~ s/^\s*//;
    $lircd_code =~ s/ *$//;
    $freevo_code =~ s/^\s*//;
    
    chomp($lircd_code);
    chomp($freevo_code);
    $keys{$lircd_code} = $freevo_code;
  }
}

foreach $key (sort(keys(%keys))) {
  print "begin\n";
  print "    prog = freevo\n";
  print "    button = $key\n";
  print "    config = $keys{$key}\n";
  print "end\n";
}

