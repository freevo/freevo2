# -*- python -*-

import sys, time

from www.base import HTMLResource, FreevoResource
import config
import util
import record.client

class IndexResource(FreevoResource):
    def _render(self, request):
        fv = HTMLResource()
        fv.printHeader(_('Welcome'), 'styles/main.css',selected=_('Home'))
        fv.res += '<div id="contentmain">\n'
        
        fv.res += '<br/><br/><h2>'+( _('Freevo Web Status as of %s') % \
                time.strftime('%B %d ' + config.TV_TIMEFORMAT, time.localtime()) ) +'</h2>'

        if record.client.server:
            fv.res += '<p class="normal">'\
                      +_('The recording server is up and running.')+'</p>\n'
        else:
            fv.res += '<p class="alert"><b>'+_('Notice')+'</b>: ' \
                      +_('The recording server is down.')+'</p>\n'

#         else:

#         listexpire = tv_util.when_listings_expire()
#         if listexpire == 1:
#             fv.res += '<p class="alert"><b>'+_('Notice')+'</b>: '+_('Your listings expire in 1 hour.')+'</p>\n'
#         elif listexpire < 12:
#             fv.res += '<p class="alert"><b>'+_('Notice')+'</b>: '+( _('Your listings expire in %s hours.') % listexpire ) +'</p>\n'
#         else:
#             fv.res += '<p class="normal">'+_('Your listings are up to date.')+'</p>\n'

#         (got_schedule, recordings) = tv.record_client.getScheduledRecordings()
#         if got_schedule:
#             progl = recordings.getProgramList().values()
#             f = lambda a, b: cmp(a.start, b.start)
#             progl.sort(f)
#             for prog in progl:
#                 try:
#                     if prog.isRecording == TRUE:
#                         fv.res += '<p class="alert">'+_('Now Recording %s.')+'</p>\n' % prog.title
# 	                break
#                 except:
#                     pass
#             num_sched_progs = len(progl)
#             if num_sched_progs == 1:
#                 fv.res += '<p class="normal">'+_('One program scheduled to record.')+'</p>\n'
#             elif num_sched_progs > 0:
#                 fv.res += '<p class="normal">'+(_('%i programs scheduled to record.') % num_sched_progs )+'</p>\n'
#             else:
#                 fv.res += '<p class="normal">'+_('No programs scheduled to record.')+'</p>\n'
#         else:
#             fv.res += '<p class="normal">'+_('No programs scheduled to record.')+'</p>\n'

        diskfree = _('%i of %i Mb free in %s')  % ( (( util.freespace(config.TV_RECORD_DIR) / 1024) / 1024), ((util.totalspace(config.TV_RECORD_DIR) /1024) /1024), config.TV_RECORD_DIR)
        fv.res += '<p class="normal">' + diskfree + '</p>\n'
        fv.res += '</div>'
        fv.printSearchForm()
        fv.printLinks()
        fv.printFooter()

        return String( fv.res )
    

resource = IndexResource()

