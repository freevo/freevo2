# Find all the dynamic link library dependencies for the executables and libs
# in distfreevobin (which is produced by the Installer app).
# Then copy them into distfreevobin to make the runtime completely
# standalone. This includes libc etc for now.

import sys, os


def query_dlls():
    # Generate a list of all dependencies in /tmp/dllcopy.txt using 'ldd'
    files = os.listdir('distfreevo_rt')
    deps = []
    for file in files:
        if file.find('.so') != -1:
            print 'Checking %-30s' % file,
            os.system('ldd distfreevo_rt/%s > /tmp/dllcopy.txt' % file)

            # Read the list from the file
            dep_lines = open('/tmp/dllcopy.txt').readlines()
            num_deps = 0
            for dep in dep_lines:
                if dep.find('statically linked') != -1:
                    continue
                
                if dep.find('not found') != -1:
                    print 'FATAL: Cannot find dll: %s!' % dep
                    sys.exit(1)
                    
                try:
                    dll = dep.split()[2].replace('\n', '').replace('\t', '')
                except IndexError:
                    print 'Parsing failed on "%s"' % dep
                    sys.exit(1)
                    
                if dll not in deps:
                    deps += [dll]

                num_deps += 1

            if num_deps:
                print '%2s deps' % num_deps
            else:
                print ' static'

    return deps
    
if __name__ == '__main__':
    deps = query_dlls()

    for dep in deps:
        fname = os.path.basename(dep)
        print 'Copying %s' % fname
        os.system('cp %s distfreevo_rt/%s' % (dep, fname))

    fd = open('distfreevo_rt/preloads', 'w')

    print 'Generating preloads def'
    
    for dep in deps:
        # ld-linux must not be preloaded
        if dep.find('ld-linux') != -1:
            continue
        fname = os.path.basename(dep)
        fd.write('freevo_rt/%s ' % fname)
    fd.write('\n')
        
    
