import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd	
from campyTM import campy as ctm

######################################################################################################
#
######################################################################################################
def createLabLocTriples(df,row,isoTitle):
	triple = ""
	isoLoc = ""
	isoLocA = df["Isolate Location 1"][row]
	isoLocB = df["Isolate Location 2"][row]

	# As the isolate's physical location
	if not pd.isnull(isoLocA) and cn.isGoodVal(isoLocA):
		isoLoc = isoLocA
		
	if not pd.isnull(isoLocB) and cn.isGoodVal(isoLocB):
		isoLoc = isoLocB
		
	if isoLoc:
		triple += ctm.indTriple(isoLoc, "IsolateLocation")
		triple += ctm.propTriple(isoLoc, {"hasName":isoLoc}, True )
		triple += ctm.propTriple(isoTitle, {"hasIsolateLocation":isoLoc})

	return triple
