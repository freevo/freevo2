#!/usr/bin/env bash

# autogen.sh 
#
# Dirk Meyer  <dmeyer@tzi.de>
# $Id$

for file in `find i18n -name freevo.po`; do
    out=`echo $file | sed 's/\.po$/.mo/'`
    echo generating $out
    msgfmt -o $out $file 2> /dev/null
done

echo
echo generating freevo_howto html files

cd Docs
docbook2html -o howto freevo_howto.sgml 2>&1 | grep -v jade


# end of autogen.sh 
