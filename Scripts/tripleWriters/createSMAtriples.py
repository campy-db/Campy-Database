import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import cleanCSV as cn
from Scripts.TripleMaker import TripleMaker as tm
import pandas as pd
from campyTM import campy as ctm
from labTM import lab as ltm

######################################################################################################
# createSMAtriples
######################################################################################################
def createSMAtriples(df,  row,  isoTitle):

	sTriple = ""
	pulsovar = df["Pfge Sma I  / Pulsovar"][row]

	if not pd.isnull(pulsovar) and cn.isGoodVal(pulsovar):
		
		sTitle = "sma1_"+isoTitle

		sTriple += ltm.indTriple(sTitle, "SMA1_test")

		sTriple += ltm.propTriple(sTitle, {"foundPulsovar":str(pulsovar)}, True, True)

		sTriple += tm.multiURI((isoTitle,  "hasLab_test",  sTitle),  (ctm.uri,  ctm.uri,  ltm.uri))


	return sTriple
