import pymetar

sky_conditions = [
					('partly cloudy','PART CLOUD'),
					('mostly cloudy','MOST CLOUD'),
					('mostly clear','MOST CLEAR'),
					('clear','CLEAR'),
					('overcast','OVERCAST')
				]


weather = pymetar.Report()
weather.fetch('CYYZ')
print weather.gettime()
print weather.getcode()
print weather.getreport()

