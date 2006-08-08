import os
import sys
import kaa.xml
from kaa.strutils import unicode_to_str

class FXD(kaa.xml.Document):

    def __init__(self, filename):
        kaa.xml.Document.__init__(self, filename, 'freevo')
        self._filename = filename
        self._dirname = os.path.dirname(filename)
        
    def parse_content(self, node):
        title = node.getattr('title') or ''
        image = None
        info = {}
        for attr in node:
            if attr.name == 'cover-img' and attr.content:
                image = os.path.join(self._dirname, unicode_to_str(attr.content))
                if not os.path.isfile(image):
                    image = None
                continue
            if attr.name == 'info':
                for i in attr.children:
                    if i.type == 'element' and i.content:
                        info[unicode_to_str(i.name)] = i.content
                continue
        return (node.name, title, image, info, node)
    
    def get_content(self, node=None):
        content = []
        if node == None:
            node = self
        for c in node:
            if c.type == 'element':
                content.append(self.parse_content(c))
        return content

    def get_content_types(self, node=None):
        content = []
        if node == None:
            node = self
        for c in node:
            if c.type == 'element':
                content.append(c.name)
        return content

# doc = FXD(sys.argv[1])
# print doc.get_content()
