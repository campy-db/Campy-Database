from campyTM import campy as ctm

######################################################################################################
#
######################################################################################################
def addStandardTrips(isoTitle,prop,title,tClass):
	triple=ctm.indTriple(title,tClass)
	triple+=ctm.propTriple(isoTitle,{prop:title})
	triple+=ctm.propTriple(title,{"hasName":title},"string")

	return triple