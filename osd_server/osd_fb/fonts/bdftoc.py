#!/usr/bin/env python

import sys, os

# Set this to 1 for debug output
DEBUG = 1

class FontSize:

    def __init__(self):
        self.points = 0
        self.x_res = 0
        self.y_res = 0

    def __str__(self):
        str = 'Points %s, res = %sx%s' % (self.points,
                                          self.x_res, self.y_res)
        return str

    
class BoundingBox:

    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = 0
        self.y = 0
        
    def __str__(self):
        str = 'Bounding box: size %sx%s, offset %s,%s' % (self.width,
                                                          self.height,
                                                          self.x, self.y)
        return str


def bits_to_str(bitline, numbits):
    total_width = numbits + ((8 - (numbits % 8)) % 8)
    pad = total_width - numbits

    #s = 'numbits = %2d, totw = %2d, pad = %2d  ' % (numbits, total_width, pad)
    s = ''
    for i in range(total_width - pad):
        if bitline & (1 << (total_width - i - 1)):
            s += '*'
        else:
            s += '.'

    return s
    

def bits_to_bytes(bitline, numbits):
    num_bytes = (numbits + 7) >> 3

    bytes = []
    for i in range(num_bytes):
        sl = (num_bytes - i - 1) * 8
        byte = bitline
        byte = (byte & (0xffL << sl)) >> sl
        #print 'Iter %d, val = 0x%010x, mask = 0x%010x, res = 0x%02x' % (i, bitline,
        # (0xffL << sl), byte)
        bytes  += [byte]

    #print
    return bytes
    

class FontChar:

    def __init__(self):
        self.name = ''
        self.encoding = 0
        self.width = 0
        self.bbox = BoundingBox()
        self.bitmap = []

    def __str__(self):
        slist = []
        
        s = 'Name: %s' % self.name
        slist += [s]

        s = 'Encoding: %s' % self.encoding
        slist += [s]

        s = 'Width: %s' % self.width
        slist += [s]

        s = self.bbox.__str__()
        slist += [s]

        s = 'Bitmap:'
        slist += [s]

        for bit_line in self.bitmap:
            bit_string = bits_to_str(bit_line, self.bbox.width)
            s = '\t%010x %s' % (bit_line, bit_string)
            slist += [s]
            
        str = '\n'.join(slist)
        return str
         
        
class BDF:

    def __init__(self):
        self.filename = ''
        self.name = ''
        self.size = FontSize()
        self.bbox = BoundingBox()
        self.properties = []
        self.numchars = 0
        self.fontchars = []
        pass


    def __str__(self):
        slist = []
        
        s = 'Name: "%s"' % self.name
        slist += [s]

        s = 'Num chars: %s' % self.numchars
        slist += [s]

        s = self.size.__str__()
        slist += [s]

        s = self.bbox.__str__()
        slist += [s]

        s = 'Properties:'
        slist += [s]

        for prop in self.properties:
            s = '\t%-20s %s' % (prop[0], prop[1])
            slist += [s]
            
        s = 'Characters:'
        slist += [s]

        for fontchar in self.fontchars:
            s = fontchar.__str__()
            slist += [s]
            slist += ['\n']
            
        str = '\n'.join(slist)
        return str
    

def bdf_parse(fp, filename):
    bdf = BDF()

    bdf.filename = filename
    
    # Get the startfont tag
    line = fp.readline().strip()
    assert line == 'STARTFONT 2.1', line

    # Skip past the comments and parse the FONT tag
    while 1:
        line = fp.readline().strip()

        if line[0:4] == 'FONT':
            bdf.name = line[5:]
            break

    # Parse the SIZE tag
    line = fp.readline().strip().split(' ')
    assert line[0] == 'SIZE', line
    bdf.size.points = int(line[1])
    bdf.size.x_res = int(line[2])
    bdf.size.y_res = int(line[3])
    
    # Parse the FONTBOUNDINGBOX tag
    line = fp.readline().strip().split(' ')
    assert line[0] == 'FONTBOUNDINGBOX', line
    bdf.bbox.width = int(line[1])
    bdf.bbox.height = int(line[2])
    bdf.bbox.x = int(line[3])
    bdf.bbox.y = int(line[4])

    # Skip past the comments and parse the PROPERTIES tag
    while 1:
        line = fp.readline().strip().split(' ')

        if line[0] == 'STARTPROPERTIES':
            props = []
            numprops = int(line[1])
            break

    # Parse the properties
    for propnum in range(numprops):
        line = fp.readline().strip()
        attr_start = line.find(' ')
        prop_name = line[0:attr_start]
        prop_attr = line[attr_start+1:]
        prop = (prop_name, prop_attr)
        props += [prop]
    bdf.properties = props
    line = fp.readline().strip().split(' ')
    assert line[0] == 'ENDPROPERTIES', line
        
    # Parse the characters
    line = fp.readline().strip().split(' ')
    assert line[0] == 'CHARS', line
    props = []
    numchars = int(line[1])
    bdf.numchars = numchars
    for charnum in range(numchars):
        fontchar = FontChar()

        line = fp.readline().strip().split(' ')
        assert line[0] == 'STARTCHAR', line
        fontchar.name = line[1]
        
        line = fp.readline().strip().split(' ')
        assert line[0] == 'ENCODING', line
        fontchar.encoding = int(line[1])

        fp.readline() # Skip SWIDTH
        line = fp.readline().strip().split(' ')
        assert line[0] == 'DWIDTH', line
        fontchar.width = int(line[1])

        line = fp.readline().strip().split(' ')
        assert line[0] == 'BBX', line
        fontchar.bbox.width = int(line[1])
        fontchar.bbox.height = int(line[2])
        fontchar.bbox.x = int(line[3])
        fontchar.bbox.y = int(line[4])

        # Parse the character bitmap
        line = fp.readline().strip()
        if line.split(' ')[0] == 'ATTRIBUTES':
            line = fp.readline().strip()
        assert line == 'BITMAP', line

        fontchar.bitmap = []
        for i in range(fontchar.bbox.height):
            bits = long(fp.readline().strip(), 16)
            fontchar.bitmap += [bits]

        line = fp.readline().strip()
        assert line == 'ENDCHAR', line

        bdf.fontchars += [fontchar]

    # End of the BDF file
    line = fp.readline().strip()
    assert line == 'ENDFONT', line

    # Done, return the BDF object
    return bdf


'''
typedef struct {
   /* width = DWIDTH from BDF */
   int32 dwidth;
   int32 width, height, x, y;
   uint8 *pBitmap;
} fontchar_t;


typedef struct {
   int32 width, height, x, y;
   fontchar_t *pFontchars[256];
} font_t;
'''


def bdf_to_include(fp, bdf):

    fp.write('/* Font filename: "%s" */\n' % bdf.filename)
    fp.write('/* Font name: "%s" */\n\n' % bdf.name)
    
    encodings = []
    for fontchar in bdf.fontchars:
        encodings += [fontchar.encoding]
        s = 'uint8 bitmap_%s[] = {\n\t' % fontchar.encoding
        
        for bitline in fontchar.bitmap:
            bitmap_bytes = bits_to_bytes(bitline, fontchar.bbox.width)
            for byte in bitmap_bytes:
                s += '0x%02x, ' % byte
            s += '  /*   ' + bits_to_str(bitline, fontchar.bbox.width) + '   */'
            s += '\n\t'
        s += '};\n'
        fp.write(s)
        
        s = 'fontchar_t fontchar_%s = { ' % fontchar.encoding
        s += '%s, ' % fontchar.width
        s += '%s, %s, ' % (fontchar.bbox.width, fontchar.bbox.height)
        s += '%s, %s, ' % (fontchar.bbox.x, fontchar.bbox.y)
        s += 'bitmap_%s' % fontchar.encoding

        s += ' };\n \n \n'
        fp.write(s)

    # The main struct
    w = bdf.bbox.width
    h = bdf.bbox.height
    x = bdf.bbox.x
    y = bdf.bbox.y
    s = 'font_t fontdata = { %s, %s, %s, %s, {\n' % (w, h, x, y)

    # Encodings
    for i in range(256):
        if i in encodings:
            s += '\t\t&fontchar_%s,\n' % i
        else:
            s += '\t\t(fontchar_t *) NULL,\n'
    s += '\t}\n'
    fp.write(s)

    s = '};\n'
    fp.write(s)


def selftest():

    bytes = bits_to_bytes(0xFFL, 8); res = [0xff]
    assert bytes == res, (bytes, res)

    bytes = bits_to_bytes(0xFFL, 16); res = [0x00, 0xff]
    assert bytes == res, (bytes, res)

    bytes = bits_to_bytes(0x0102L, 16); res = [0x01, 0x02]
    assert bytes == res, (bytes, res)

    bytes = bits_to_bytes(0x010203L, 24); res = [0x01, 0x02, 0x03]
    assert bytes == res, (bytes, res)

    bytes = bits_to_bytes(0x12345678L, 32); res = [0x12, 0x34, 0x56, 0x78]
    assert bytes == res, (bytes, res)

    bytes = bits_to_bytes(0x123456789AL, 40); res = [0x12, 0x34, 0x56, 0x78, 0x9A]
    assert bytes == res, (bytes, res)

    
    
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print '%s: Usage: %s <filename.bdf>' % (sys.argv[0], sys.argv[0])
        sys.exit(1)
        
    filename = sys.argv[1]

    infp = open(filename, 'r')

    bdf = bdf_parse(infp, filename)

    outfilename = (filename.split('/')[-1]).split('.')[0] + '.h'

    outfp = open(outfilename, 'w')

    bdf_to_include(outfp, bdf)

