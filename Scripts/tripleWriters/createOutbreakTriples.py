import pandas as pd
import standardT as st
import campyTM as ctm
import re
import cleanCSV as cn


######################################################################################################
#
######################################################################################################
def createOutbreakTriples(df,row,isoTitle):
	obTriple=""
	obA=df["Outbreak"][row]
	obB=df["Source_Specific_2"][row]

	# Some of the values in comlumn 'Outbreak' are just 'outbreak'. In such a case, we know the 
	# isolate is part of an outbreak, we just don't know the outbreak name
	if not pd.isnull(obA) and re.search("[Oo]utbreak",obA) is not None:
		if cn.compare(["outbreak",obA]):
			obTriple=ctm.campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},"bool",True)
		else:
			obTriple+=st.addStandardTrips(isoTitle,"partOfOutbreak",obA,"Outbreak")
			obTriple+=ctm.campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},"bool",True)

	# Source_specific_2 (obB) actually contains the name of the outbreak, maybe
	else:
		if not pd.isnull(obB) and re.search("[Oo]utbreak",obB) is not None:
			obTriple+=st.addStandardTrips(isoTitle,"partOfOutbreak",obB,"Outbreak")

			obTriple=ctm.campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},"bool",True)


	return obTriple