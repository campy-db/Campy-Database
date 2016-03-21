import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
from Scripts.TripleMaker import TripleMaker as tm
import pandas as pd
from campyTM import campy as ctm
from labTM import lab as ltm

######################################################################################################
# createSeroTriples
######################################################################################################
def createSeroTriples(df,  row,  isoTitle):

	triple = ""
	sero = df["Serotype"][row]

	if not pd.isnull(sero) and cn.isGoodVal(sero):

		sTitle =  "sero_{}".format(isoTitle)

		triple += ltm.indTriple(sTitle, "Serotype_test")

		triple += ltm.propTriple(sTitle, {"foundSerotype":str(sero)}, True, True)

		triple += tm.multiURI((isoTitle,  "hasLabTest",  sTitle),  (ctm.uri,  ctm.uri,  ltm.uri))


	return triple
