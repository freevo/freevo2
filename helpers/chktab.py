#!/usr/bin/env python
import sys, os

files = sys.argv[1:]

def scandir(tabfiles, dirname, fnames):

    for fname in fnames:
        if os.path.splitext(fname)[1] != '.py':
            continue

        fullname = dirname + '/' + fname
        print 'Checking file %s' % fullname
        lines = open(fullname).readlines()
        lineno = 1
        tablines = []
        for line in lines:
            if '\t' in line:
                tablines += [lineno]
            lineno += 1

        if tablines:
            tabfiles += [[fullname, tablines]]

    
if __name__ == '__main__':
    tabfiles = []
    os.path.walk('.', scandir, tabfiles)

    print
    
    for rec in tabfiles:
        fullname, tablines = rec[0], rec[1]
        print '%-40s %s' % (fullname, tablines[:25])
