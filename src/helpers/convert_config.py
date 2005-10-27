import sys
import os
import re
import util

change_map = {
    'SKIN_XML_FILE': 'GUI_XML_FILE',
    'SKIN_DEFAULT_XML_FILE': 'GUI_DEFAULT_XML_FILE',
    'SKIN_FORCE_TEXTVIEW_STYLE': 'GUI_FORCE_TEXTVIEW_STYLE',
    'SKIN_MEDIAMENU_FORCE_TEXTVIEW': 'GUI_MEDIAMENU_FORCE_TEXTVIEW',
    'OSD_DEFAULT_FONTNAME': 'GUI_FONT_DEFAULT_NAME',
    'OSD_DEFAULT_FONTSIZE': 'GUI_FONT_DEFAULT_SIZE',
    'OSD_EXTRA_FONT_PATH': 'GUI_FONT_PATH',
    'OSD_FONT_ALIASES': 'GUI_FONT_ALIASES',
    'OSD_BUSYICON_TIMER': 'GUI_BUSYICON_TIMER',
    'OSD_OVERSCAN_X': 'GUI_OVERSCAN_X',
    'OSD_OVERSCAN_Y': 'GUI_OVERSCAN_Y',
    'OSD_STOP_WHEN_PLAYING': 'GUI_STOP_WHEN_PLAYING',
    'OSD_DISPLAY': 'GUI_DISPLAY',
    'OSD_BACKGROUND_VIDEO': 'GUI_BACKGROUND_VIDEO',
    'OSD_FADE_STEPS': 'GUI_FADE_STEPS',
    }

def help():
    print 'convert local_conf.py to use the new variable names'
    print 'usage: convert_config local_conf.py [ -w ]'
    print
    print 'if -w is given the local_conf.py wil be rewritten, without the'
    print 'option the script will only print the changes.'
    print
    print 'Developer may use the option -s (without local_conf) to scan for'
    print 'files which use the deleted variables'
    print
    sys.exit(0)




seperator = ' #=[]{}().:,\n+'

def change(file, print_name=False, write_output=False):
    if file.find('convert_config.py') >= 0:
        return
    
    out = None
    try:
        cfg = open(file)
    except Exception, e:
        print e
        help()

    debug = True
    if len(sys.argv) == 3 and sys.argv[2] == '-w':
        debug = False
        
    data = cfg.readlines()
    cfg.close()

    if write_output:
        print 'write output file %s' % file
        out = open(file, 'w')

    found = False
    for line in data:
        for var in change_map:
            if line.find(var) >= 0 and \
               (line.startswith(var) or line[line.find(var)-1] in seperator) \
               and line[line.find(var)+len(var)] in seperator:
                found = True
                if print_name and debug:
                    print '**** %s **** ' % file
                    print_name = False
                if out:
                    line = line.replace(var, change_map[var])
                elif debug:
                    print 'changing line:'
                    print line[:-1]
                    print line[:-1].replace(var, change_map[var])
                    print
        if out:
            out.write(line)

    if out:
        out.close()

    if found and not write_output and len(sys.argv) == 3 and \
           sys.argv[2] == '-w':
        change(file, False, True)


if len(sys.argv) <= 3 and sys.argv[1] == '-s':
    print 'searching for files using old style variables'
    # s = ''
    # for var in change_map:
    #     s += '|%s' % var
    # s = '(%s)' % s[1:]
    # pipe = 'xargs egrep \'%s\' | grep -v helpers/convert_config' % s
    # os.system('find . -name \*.py | %s' % pipe)
    # os.system('find . -name \*.rpy | %s' % pipe)
    # print
    # print
    # print 'starting scanning all files in detail:'
    for f in [ 'freevo_config.py', 'local_conf.py','local_conf.py.example' ] +\
            util.match_files_recursively('src', [ 'py' ]):
        change(f, print_name=True)
    sys.exit(0)
    
    
change(sys.argv[1])
