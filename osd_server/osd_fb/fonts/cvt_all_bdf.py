import sys, os

lines_raw = open('allfonts.txt').readlines()

lines = map(lambda l: l.strip(), lines_raw)

for line in lines:
    attr = line.split('-')[1:]

    # Adobe, Sony, etc
    foundry = attr[0]
    # Courier
    family = attr[1]
    # bold, medium, regular, demibold
    weight = attr[2]
    # Roman, Italic, Oblique, Rev Italic, Rev Obl, OTher
    slant = attr[3]
    setwidth = attr[4]
    # Serif, Sans Serif
    addstyle = attr[5]
    pixelsize = int(attr[6])
    pointsize = attr[7]
    resx = attr[8]
    resy = attr[9]
    # Prop, Mono, Charcell
    spacing = attr[10]
    avgwidth = attr[11]
    # ISO8859
    charset_registry = attr[12]
    # 1 western europe
    charset_encoding = attr[13]

    print '%d %s-%s' % (pixelsize, charset_registry, charset_encoding)
    
    if pixelsize >= 24 and charset_registry == 'iso8859' and charset_encoding == '1':
        print 'Converting %s' % line
        os.system('fstobdf -fn "%s" > tmp' % line)
        os.system('python ../bdftoc.py tmp > font%s' % line)
        os.system('rm tmp')
    
# -adobe-helvetica-bold-r-normal--34-240-100-100-p-182-iso8859-1
