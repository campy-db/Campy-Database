# -*- coding: latin-1 -*-
import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
from campyTM import campy as ctm
import re
import standardT as st

######################################################################################################
# createLocTriples
# Gets all the info of where we got the isolate sample. 
# NOTE - Right now all values in the column Region_L1 are assumed to be health authorities. This is
#	     incorrect. Some are municipalities. This must be fixed!!!!
# We can find the watershed and the body of water the isolate came from in column Sample Source. The
# only bodies of water are the Sumas and Salmon river.
######################################################################################################
def createLocTriples(df,row,isoTitle):
	locTriple = ""
	country = df["Country"][row]
	subNat = df["Province/State"][row]
	city = df["City"][row]
	hAuthority = df["Region_L1"][row]
	samplingSite = df["Region_L2"][row]
	samplingSite2 = df["Source_Specific_2"][row] # Petting zoo is in this col, and we consider it to be
										       # a sampling site.
	c_netSite = df["C-EnterNet Site"][row]
	fncSite = df["FNC Sentinel Site"][row]
	lng = df["Longitude"][row]
	lat = df["Latitude"][row]

	# Need this for the body of water location and watersheds.
	water = df["Sample Type 2"][row]

	# If water is the sample source, there could be a body of water name, or watershed name in 
	# the Sample Source column.
	if not pd.isnull(water) and "Water" in water:
		
		bodyOfWater = df["Sample Source"][row]
		
		if not pd.isnull(bodyOfWater):
			
			bodyOfWater = cn.remPrefix(bodyOfWater, 2)

			if "Watershed" in bodyOfWater:
				locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", bodyOfWater, "Watershed")
				
			else:
				# The word river is also in the watershed values, eg oldman river watershed. So 
				# if the value does not contain watershed but does contain river, it is considered a 
				# body of water.
				# The sumas and salmon rivers are the only bodies of water..right now
				if re.search("[Rr]iver",bodyOfWater) is not None:
					locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", bodyOfWater, "BodyOfWater")

	# SamplingSite is a real mess. Has a lot of redundant information. Also, some of them
	# have city info (Fort Macleod) that isn't repeated in the City column. Note Fort Macleod 
	# is also the name of the health authority 
	if not pd.isnull(samplingSite) and cn.isGoodVal(samplingSite):
		
		if "Mcleod" in samplingSite or "Macleod" in samplingSite:
			
			city = "Fort Macleod"
			samplingSite = samplingSite.replace("Mcleod", "Macleod") # It's spelt wrong in the csv
			samplingSite = samplingSite.replace("Ft.", "Fort") # It's also abbreviated sometimes

		# The é and ô is � in the csv, and for whatever reason � counts as 3 characters
		samplingSite = re.sub("Mont...r...gie","Montérégie",samplingSite)
		samplingSite = re.sub("H...pital","Hôpital",samplingSite)

		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", samplingSite, "SamplingSite")

	if not pd.isnull(country) and cn.isGoodVal(country):
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", country, "Country")

	if not pd.isnull(subNat) and cn.isGoodVal(subNat):
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", subNat, "SubNational")

	if not pd.isnull(city) and cn.isGoodVal(city):
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", city, "City")

	if not pd.isnull(hAuthority) and cn.isGoodVal(hAuthority):
		
		hAuthority = cn.remPrefix(hAuthority,3)
		
		# Sometimes watersheds are here. If they are, they are also in the Sample Source
		# column, and we've already handled that. Note that a watershed is not a 
		# health authority
		if re.search("[Ww]atershed",hAuthority) is None: 

			# Montérégie is in the csv and the é is all screwed up its � in the csv, and
			# for whatever reason � counts as 3 characters
			hAuthority = re.sub("Mont...r...gie","Montérégie",hAuthority)

			locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", hAuthority, "HealthAuthority")

	if not pd.isnull(samplingSite2) and ("Petting Zoo" in samplingSite2):
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", samplingSite2, "SamplingSite")

	if not pd.isnull(c_netSite) and cn.isGoodVal(c_netSite):
		
		c_netSite = cn.cleanInt(c_netSite) # Some of there are numbers
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", c_netSite, "C_EnterNetSite")

	if not pd.isnull(fncSite) and cn.isGoodVal(fncSite):
		locTriple += st.addStandardTrips(isoTitle, "hasSourceLocation", fncSite, "FNCSentinelSite")

	# Have to convert lat and long to signed decimal format
	if not pd.isnull(lng) and cn.isGoodVal(lng):
		if not pd.isnull(lat) and cn.isGoodVal(lat): # lat is never nan when long is and vice versa
		
			lat = cn.convertGPS(lat)
			lng = cn.convertGPS(lng)

			locTriple+= ctm.propTriple(isoTitle,{"hasLatitude":lat}, True, True)
			locTriple+= ctm.propTriple(isoTitle,{"hasLongitude":lng}, True, True)


	return locTriple

