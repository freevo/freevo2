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

docbook () {
    echo
    echo generating $1 howto html files

    cd Docs/$1
    docbook2html -o html howto.sgml
    cd ../..
    echo
    echo
}
    
howto() {
    docbook installation
    docbook plugin_writing
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
    howto)
        howto
        ;;
    help)
        echo -n "Usage:   "
        echo $0
        echo "          nodocs     -  Just generate translations"
        echo "          howto      -  Just generate the docbook howto"
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
