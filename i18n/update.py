#!/usr/bin/env python

import os
import sys

print 'update pot file'

f = open('freevo.pot')

fxd_strings = []

add = 0
for line in f.readlines():
    if line.find('Manualy added from fxd skin files') > 0:
        add = 1
    if add:
        fxd_strings.append(line)
        
f.close()

os.system('(cd ../src ; find . -name \*.py | xargs xgettext -o ../i18n/freevo.pot)')

f = open('freevo.pot', 'a')
    
for line in fxd_strings:
    f.write(line)

f.close()

print '',
for file in ([ os.path.join('.', fname) for fname in os.listdir('.') ]):
    if os.path.isdir(file) and file.find('CVS') == -1:
        print 'update %s...' % file,
        sys.stdout.flush()
        file = os.path.join(file, 'LC_MESSAGES/freevo.po')
        mo = os.path.splitext(file)[0] + '.mo'
        if len(sys.argv)==1 or sys.argv[1] != '--no-merge':
            os.system('msgmerge --update --backup=off %s ./freevo.pot' % file)
        else:
            print 'done (no merge)'
        os.system('msgfmt -o %s %s' % (mo, file))
        

