import sys
import getopt
import mcomm

def usage():
    print '-p file'
    print '-s'
    sys.exit(0)
    
try:
    opts, args = getopt.getopt(sys.argv[1:], 'p:sh')
except getopt.GetoptError:
    usage()

if len(opts) != 1:
    usage()

cmd, arg = opts[0]

if cmd == '-h':
    usage()

freevo = mcomm.find('freevo')

if not freevo:
    print 'freevo not running'
    sys.exit(0)

try:
    if cmd == '-p':
        print freevo.play(arg)
    if cmd == '-s':
        print freevo.stop()
except mcomm.MException, e:
    print e
