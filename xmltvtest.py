import xmltv
import time,re

programs = xmltv.read_programmes(open('/tmp/TV.xml'))
nowtime = time.strftime('%Y%m%d%H.... %Z')

for program in programs:
	if re.match(nowtime,program['start']):
		print '%s: %s' % (program['channel'],program['title'])



