# python imports
import sys
import os
import re

# freevo imports
import config
import util

# www imports
from base import HTMLResource, FreevoResource

re_link = re.compile('(href *= *")([^:]*?.html)"')

class DocResource(FreevoResource):
    def replace_link(self, reg):
        href, url = reg.groups()
        url = os.path.join(os.path.dirname(self.page), url)
        url = os.path.normpath(url)
        return '%sdoc?file=%s"' % (href, url)


    def _render(self, request):
        if request.query.has_key('file'):
            self.page = request.query['file']
        else:
            self.page = 'Index.html'

        fv = HTMLResource()
        fv.printHeader(_('Documentation'), None, selected=_('Doc'))
        header = fv.res.split('</head>')
        fv.res = header[0] + '''
        <link rel="stylesheet" type="text/css" charset="utf-8"
        media="all" href="modern/css/common.css">
        <link rel="stylesheet" type="text/css" charset="utf-8" media="screen"
        href="modern/css/screen.css">
        <link rel="stylesheet" type="text/css" charset="utf-8" media="print"
        href="modern/css/print.css">
        <link rel="stylesheet" type="text/css" charset="utf-8"
        href="modern/css/freevo.css">
        ''' + header[1]

        fv.res += '<p>&nbsp;</p>\n'

        src = os.path.join(config.DOC_DIR, 'html/%s' % self.page)
        src = open(src)
        p = False
        for line in src.readlines():
            if line.find('<!-- start page -->') > 0:
                p = True
            if p:
                line = re_link.sub(self.replace_link, line)
                fv.res += line
            if line.find('<!-- end page -->') > 0:
                p = False
        src.close()
        fv.printLinks()
        fv.printFooter()

        return String( fv.res )


# init the resource
resource = DocResource()
