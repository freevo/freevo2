#
# config.py - Handle the configuration file init.
#
# Try to find the freevo_config.py config file in the following places:
# 1) ~/.freevo/freevo_config.py       The user's private config
# 2) /etc/freevo/freevo_config.py     Systemwide config
# 3) ./freevo_config.py               Defaults from the freevo dist
#
# Customize freevo_config.py from the freevo dist and copy it to one of the
# other places where it will not get overwritten by new checkouts/installs
# of freevo.
#
# The format of freevo_config.py might change, in that case you'll have to
# update your customized version.
#
# $Id$
#

import sys, os

cfgfilepath = [ '/etc/freevo',
                os.path.expanduser('~/.freevo'),
                '.'
                ]

found = 0
for dir in cfgfilepath:
    cfgfilename = dir + '/freevo_config.py'
    if os.path.isfile(cfgfilename):
        print 'Loading cfg: %s' % cfgfilename
        execfile(cfgfilename, globals(), locals())
        found = 1
        break
    else:
        print '%s not found' % cfgfilename

if not found:
    # This is a fatal error, the freevo_config.py file must be loaded!
    print 'Freevo: Fatal error, cannot find freevo_config.py. Looked in the following dirs:'
    for dir in cfgfilepath:
        print ' '*5 + dir

    raise 'Cannot find freevo_config.py'
