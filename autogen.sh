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
cd ..


wiki=src/www/htdocs/help/wiki

echo
echo getting some wiki pages
rm -rf $wiki
mkdir $wiki

for file in FxdFiles SkinInfo; do
    wget http://freevo.sourceforge.net/cgi-bin/moin.cgi/DocumentationPage_2f$file \
	-O $wiki/$file.html
done

wget http://freevo.sourceforge.net/cgi-bin/moin.cgi/FrequentlyAskedQuestions \
    -O $wiki/faq.html

exit 0

# end of autogen.sh 
