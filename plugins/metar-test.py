import pymetar

weather = pymetar.Report()
weather.fetch('CYYZ')
print weather.gettime()
print weather.getcode()
print weather.getreport()

