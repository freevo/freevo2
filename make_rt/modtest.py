import sys, os

if __name__ == '__main__':
    fd = open('sysmodules.py', 'a')
    
    if len(sys.argv) != 2:
        # Internal error, make sure the user notices
        fd.write('Gack! modtest.py failed on %s!\n' % sys.argv)
        sys.exit()
        
    sysmod = sys.argv[1]

    try:
        exec('import %s' % sysmod)
        # If we get here the module imported OK
        fd.write('import %s\n' % sysmod)
    except:
        pass
