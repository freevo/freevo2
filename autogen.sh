#!/usr/bin/env bash

# autogen.sh 
#
# Dirk Meyer  <dmeyer@tzi.de>
# $Id$

gen_i18n() {
    for file in `find i18n -name freevo.po`; do
     out=`echo $file | sed 's/\.po$/.mo/'`
     echo generating $out
     msgfmt -o $out $file 2> /dev/null
    done
}

howto() {
    echo
    echo generating freevo_howto html files

    cd Docs
    docbook2html -o howto freevo_howto.sgml

    echo
    echo
    echo generating plugin writing howto html files
    cd plugin_writing
    docbook2html -o html howto.sgml

    cd ../..
}

wiki() {
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
}

# Main
case "$1" in
    nodocs)
        gen_i18n
        ;;
    nodocbook)
        gen_i18n
        wiki
        ;;
    help)
        echo -n "Usage:   "
        echo $0
        echo "          nodocs     -  Just generate translations"
        echo "          nodocbook  -  Fetch Wiki but do not make howto"
        echo "          <default>  -  Generate translations, fetch wiki and generate Howto"
        ;;
    *)
        gen_i18n
        howto
        wiki
        ;;
esac


# end of autogen.sh 
