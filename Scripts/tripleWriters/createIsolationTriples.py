import pandas as pd
import campyTM as ctm
import re
import cleanCSV as cn

######################################################################################################
#
######################################################################################################
def createIsolationTriples(df,row,isoTitle):
	isoTriple=""
	media=df["Media"][row]
	# Don't include colony morph for now.
	# colonyMorph=df["colony morph"][row]
	dilution=df["Dilution"][row]
	glycStock=df["No glycerol stock"][row]
	hipO=df["HipO"][row]
	treatment=df["Treatment"][row]
	technique=df["technique"][row]
	sourceSpec=df["Source_Specific_2"][row] # For whatever reason source specific 2 has media info in
											# it. Just one though: K and Cefex

	# For whatever reason there's just a dash as one of the media values. We'll ignore it for now.
	if not pd.isnull(media) and media!="-" and "#N/A" not in media:
		# We'll standardize all media to be uppercase and some have spaces but others don't. eg
		# there's the value '10% B' and '10%B'. That's no good.
		media=media.upper().replace(" ","")
		
		# Grab k and cefex from source specific 2
		if not pd.isnull(sourceSpec) and re.search("[Cc]efex",sourceSpec) is not None:
			media="K and CEFEX" # SUBJECT TO CHANGE

		isoTriple+=ctm.campy.propTriple(isoTitle,{"grownOn":media},"string",True)

	if not pd.isnull(dilution):
		# Again there are some values that have spaces and others that don't. 
		# We'll get rid of the spaces 
		dilution=dilution.replace(" ","")
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasDilution":dilution},"string",True)

	# The values in the csv are 1 or 0. 1 meaning it is true there is no glyc stock. This
	# is confusing. So in the ontology we have 'hasGlycStock' and we interpret 1 in the csv as false
	if not pd.isnull(glycStock) and cn.isGoodVal(glycStock):
		glycStock=cn.cleanInt(glycStock) # Sometimes ints are converted to floats in the csv
		glycStock="false" if "1" in glycStock else "true"
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasGlycStock":glycStock},"bool",True)

	if not pd.isnull(hipO) and cn.isGoodVal(hipO):
		hipO=cn.cleanInt(hipO)

		if "1" in hipO:
			hipO="true"; litType="bool"
		else:
			if "?" in hipO: 
				hipO="unknown"; litType="string"
			else:
				hipO="false"; litType="bool"

		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasHipO":hipO},litType,True)

	# For whatever reason the value 'Treatment' is in the column 'Treatment'. We'll ignore it 
	# for now. 
	if not pd.isnull(treatment) and "Treatment" not in treatment and cn.isGoodVal(treatment):
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasTreatment":treatment},"string",True)

	# The - also showed up in technique. We'll ignore it.
	if not pd.isnull(technique) and technique!="-":
		# Values enrichment, ENRICH and enrich are found in this col. We'll standardize it to enrich
		if "enrich" in technique.lower():
			technique="enrich"

		# Some values have spaces and others don't. eg '24AE' and '24 AE'. We'll get rid of
		# spaces.
		technique=technique.replace(" ","")

		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasTechnique":technique},"string",True)
			
	return isoTriple