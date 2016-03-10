import campyTM as ctm

######################################################################################################
#
######################################################################################################
def addStandardTrips(isoTitle,prop,title,tClass):
	triple=ctm.campy.indTriple(title,tClass)
	triple+=ctm.campy.propTriple(isoTitle,{prop:title})
	triple+=ctm.campy.propTriple(title,{"hasName":title},"string")

	return triple