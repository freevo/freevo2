#!/usr/bin/env python
#
# dagenstv2xmltv v0.81 by Per Wigren <wigren@open-source.nu>
#
# A program to get TV programs from the Swedish site http://www.dagenstv.com
# and save them in a XMLTV-file.
# 
# Yes, it's ugly, but it works!! ;)
#
######################################################
#
# v0.7:  * Initial public release
# v0.8:  * Swapped order of <category> and <desc>
#        * Convert & to &amp;
#        * Remove strange ctrl+G chars that appear in some fields
#          for some very strange reason...
#        * Save xml in unicode, utf-8
# v0.81: * Indention-typo in create_xml: The lists were sorted
#          for every program instead of once when all programs are
#          added.. HUGE speedup!
#        * Added this changelog ;)
# v0.85: * Added DOCTYPE
#        * You are now able to choose which channels to retrieve
#        * Minor bugfixes
#
######################################################


import sys,os,re,urllib,time


# Parse commandline
# FIXME: Use real parsing... :P
try:
	days=int(sys.argv[1])
	lang=sys.argv[2]
	file=sys.argv[3]
except:
	print "Usage:", sys.argv[0], "<days> <lang> <filename> [channel-ids]"
	print "  days         Number of days of data to retrieve"
	print "  lang         sv for Swedish, no for Norvegian"
	print "  filename     Filename of XMLTV .xml-file"
	print "  channel-ids  Comma-separaded list of channel-IDs"
	sys.exit(5)

if not lang in ("sv","no"):
	print "Bad language:", lang
	sys.exit(5)

to_get=None
if len(sys.argv)>4:
	to_get=sys.argv[4].split(",")


# Get a list of dates to fetch
def get_dates(days):
	now=time.mktime(time.localtime())
	temp=[]
	for i in xrange(days):
		temp.append(time.strftime("%Y-%m-%d",time.localtime(now)))
		now += 86400
	return temp
dates=get_dates(days)

def tomorrow(date):
	temp = time.mktime(time.strptime(date,"%Y-%m-%d"))
	return time.strftime("%Y-%m-%d",time.localtime(temp+86400))

# Return URL to retrieve
def url(dat="",cha="",cat=""):
	if lang=="sv": country="se"
	else: country="no"
	return "http://www.dagenstv.com/"+country+"/chart/?dat=%(dat)s&cat=%(cat)s&cha=%(cha)s" % vars()

# Expand HTML entities such as &#225; to latin1
def expand(text):
	def intEnt(m):
		m = int(m.groups(1)[0])
		if m > 255 or m < 64 : return ""
		else: return chr(m)
	def xEnt(m):
		m = int(m.groups(1)[0], 16)
		if m > 255 or m < 64: return ""
		else: return chr(m)
	text = text.replace(" & ", " &amp; ")
	text = text.replace(chr(0x07),"")
	text = re.sub("(&[rl]squo;|&#821[761];)", "'", text)
	text = re.sub("&[rl]dquo;", '"', text)
	text = re.sub("&([aeiou])(grave|acute|circ|tilde|uml|ring);", lambda m: m.groups(1)[0], text)
	text = re.sub(r'&#(\d+);', intEnt, text)
	text = re.sub(r'&#[Xx](\w+);', xEnt, text)
	text = re.sub("&(#169|copy);", "(C)", text)
	text = re.sub("&(mdash|[xX]2014);", "--", text)
	return text

def printinfo(text):
	sys.stdout.write(text+"\n")
	sys.stdout.flush()

def writexml(text):
	fh=open(file,"wb")
	fh.write(text+"\n")
	fh.flush()
	fh.close()

# Get a list of channels and categories
def get_cha_cat():
	cha={}
	cat={}
	in_cha=0 ; in_cat=0

	try:
		html=urllib.urlopen(url()).readlines()
	except:
		return (None,None)

	for line in html:
		line = line.strip()

		if   in_cha==0 and line.find('<select name="cha"')>=0:	in_cha=1
		elif in_cha==1 and line.find('</select')>=0:		in_cha=2
		elif in_cat==0 and line.find('<select name="cat"')>=0:	in_cat=1
		elif in_cat==1 and line.find('</select')>=0:		in_cat=2

		if   in_cha==1:
			try:
				(cha_nr,cha_name) = re.search('<option value="(\d+)">(.*?)</option>',line).groups()
				cha[expand(cha_name)]=cha_nr
			except:
				continue
		elif in_cat==1:
			try:
				(cat_nr,cat_name) = re.search('<option value="(\d+)">(.*?)</option>',line).groups()
				cat[expand(cat_name)]=cat_nr
			except:
				continue
	return (cha,cat)


# Convert date and time to xmltv-format
def xtime(date,stime):
        if int(stime.replace(":","")) < 600:
		date = tomorrow(date)
	temp = date+stime
	return temp.replace("-","").replace(":","")+"00 +0100"

# Parse the channel-page
def parse_channel_data(url,date):
	html=urllib.urlopen(url).readlines()

	programs=[]
	in_cha=0 ; in_name=0 ; in_sv=0 ; in_desc=0 ; count=0

	for line in html:
		line = line.strip()

# Start-time
		if line.find('<td class="charttime"')>=0:	# Start of new channel
			try:
				nstime=re.search('>(\d\d:\d\d)<',line).group(1)
			except:
				print "ERROR, stime:", line
				nstime="99:99"

			if count>0:
				if etime=="": etime=nstime
				programs.append({'name':	expand(name),
						 'start':	xtime(date,stime),
						 'stop':	xtime(date,etime),
						 'desc':	expand(desc),
						 'sv':		sv,
						 'cat':		[]})
			stime=nstime
			etime="" ; name = "" ; sv="" ; desc="" ; cat=""
			count += 1
			in_cha=1 

		if not in_cha: continue

# Name and end-time	
		if line.find('<span class="charteventname"')>=0:	
			in_name=1
			continue
		if in_name:
			if line.find('</span>')>=0 or line.find('<span')>=0:
				in_name=0
				try:
					etime=re.search('\((\d\d:\d\d)\)',line).group(1)
				except:
					pass
			if line.find("<")>=0: name += line[:line.find("<")]
			else: name += line
# Description
		if line.find('<span class="chartdescription"')>=0:
			in_desc=1
			continue
		if in_desc:
			if line.find('</span>')>=0 or line.find('<span')>=0: in_desc=0
			#desc += line[:line.find("<")+1]
			if line.find("<")>=0: desc += line[:line.find("<")]
			else: desc += line
# Showview
		if line.find('<span class="chartshowview"')>=0:
			try:
				sv=re.search('\[(\d+)\]',line).group(1)
			except:
				print "ERROR, sv:", line
	if count>0:
		programs.append({'name':	expand(name),
				 'start':	xtime(date,stime),
				 'stop':	xtime(date,etime),
				 'desc':	expand(desc),
				 'sv':		sv,
				 'cat':		[]})
	return programs


# Parse category-page
def parse_category_data(url):
        html=urllib.urlopen(url).readlines()

        programs=[]
        count=0 ; in_name=0

        for line in html:
                line = line.strip()

		if line.find('<span class="charteventname"')>=0:
			if count>0: programs.append(expand(name))
			count += 1 ; in_name=1 ; name=""
			continue
		if in_name:
			if line.find('</span>')>=0: in_name=0
			name += line[:line.find("<")]
	if count>0: programs.append(expand(name))

	return programs


(cha,cat) = get_cha_cat()
if cha==None:
	print "Error retrieving channels- and categories-information"
	sys.exit(10)

if to_get:
	channels=[]
	for (name,id) in cha.items():
		if id in to_get:
			channels.append(name)
		
		
else:
	channels=cha.keys()

program={}

# Retrieve and parse all pages...
for date in dates:
	for name in channels:
		printinfo( "P "+date+"  "+name )
		for prog in parse_channel_data(url(date,cha[name],""),date):
			program[prog['name']]=prog
			program[prog['name']]['cha']=cha[name]
			program[prog['name']]['date']=date
	for name in cat.keys():
		printinfo( "C "+date+"  "+name )
		for prog in parse_category_data(url(date,"",cat[name])):
			try:
				if not name in program[prog]['cat']:
					program[prog]['cat'].append(name)
			except:
				pass


# Create the xmltv-file
def create_xml(program):

	# Sort by start-time, then program name
	prog_keys=[] ; cha_keys=[]
	for key in program.keys():
		prog_keys.append( (program[key]['start'],key) )
	prog_keys.sort()
	for key in cha.keys():
		cha_keys.append( (key.lower(), key) )
	cha_keys.sort()

	x ='<?xml version="1.0" encoding="ISO-8859-1"?>\n'
	x+='<!DOCTYPE tv SYSTEM "xmltv.dtd">\n'


	x+='<tv generator-info-name="dagenstv2xmltv by Per Wigren - wigren@open-source.nu"'
	x+=' source-info-url="http://www.dagenstv.com" source-info-name="Dagens TV"'
	x+=' source-data-url="http://www.dagenstv.com">\n'
	for key in cha_keys:
		name = key[1]
		id=cha[name]
		x+='  <channel id="'+id+'">\n'
		x+='    <display-name lang="'+lang+'">'+name+'</display-name>\n'
		x+='    <display-name>'+id+'</display-name>\n'
		x+='  </channel>\n'
	x+='\n'
	for key in prog_keys:
		prog = program[key[1]]

		x+='  <programme start="'+prog['start']+'" stop="'+prog['stop']+'"'
		x+=' channel="'+prog['cha']+'"'
		if not prog['sv']=="": x+=' showview="'+prog['sv']+'"'
		x+='>\n'

		x+='    <title lang="'+lang+'">'+prog['name']+'</title>\n'

		if len(prog['desc'])>1:
			x+='    <desc lang="'+lang+'">\n'
			x+='      '+prog['desc']+'\n'
			x+='    </desc>\n'

		if len(prog['cat'])>0:
			for c in prog['cat']:
				x+='    <category lang="'+lang+'">'+c+'</category>\n'
		x+='  </programme>\n'

	x+='</tv>'
	
	return x

# Main program ;-)
writexml( unicode(create_xml(program),'latin-1').encode("iso-8859-1") )

