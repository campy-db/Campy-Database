import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
from campyTM import campy as ctm
import re

######################################################################################################
#
######################################################################################################
def createIDtriples(df,row,isoTitle):
	idTriple=""
	nmlid=df["NML ID#"][row]
	ldmsid=df["LDMS ID"][row]
	origName=df["Mostly Original Sample Names (might have project prefixes!)"][row] # lol
	sidA=df["Alternate Sample ID"][row]  # Sample id
	sidB=df["Alt. Sample ID"][row]
	sidC=df["C-EnterNet Number"][row]
	cidA=df["Sample Collection ID"][row] # Collection id
	cidB=""
	comment=""

	# Add the nmlID, ldmsID and original sample name
	if not pd.isnull(nmlid) and cn.isGoodVal(nmlid) and nmlid!="0":
		idTriple+=ctm.propTriple(isoTitle,{"hasNMLid":nmlid},"string",True)

	if not pd.isnull(ldmsid) and cn.isGoodVal(ldmsid):
		idTriple+=ctm.propTriple(isoTitle,{"hasLDMSid":ldmsid},"string",True)
	if not pd.isnull(origName) and cn.isGoodVal(origName):
		idTriple+=ctm.propTriple(isoTitle,{"hasOriginalName":origName},"string",True)

	# Add the isolate's many sample ID's. Don't add the ID if it is the same as the isoTitle
	# or other the other IDs before it
	if not pd.isnull(sidA) and cn.isGoodVal(sidA):
		# Sometimes the Alternate ID is the strain name but with an - instead of _. This causes
		# problems with the reified literals. Note even if it is the same as the strain name as
		# some other strains may have the same sample id
		if cn.compare([isoTitle,sidA]):
			sidA=isoTitle

		litAType="int" if cn.isNumber(sidA) else "string" # Some ids are ints
		idTriple+=ctm.propTriple(isoTitle,{"hasSampleID":sidA},litAType,True)

	if not pd.isnull(sidB) and cn.isGoodVal(sidB):
		# The values 'wrong label on tube..' is in this column. We put this in the
		# comments field instead
		if "wrong" in sidB:
			comment=sidB
		else:
			if cn.compare([isoTitle,sidB]):
				sidB=isoTitle
			
			litBType="int" if cn.isNumber(sidB) else "string" # Some ids are ints
			idTriple+=ctm.propTriple(isoTitle,{"hasSampleID":sidB},litBType,True)

	if not pd.isnull(sidC) and cn.isGoodVal(sidC):
		if cn.compare([isoTitle,sidC]):
			sidC=isoTitle

		litCType="int" if cn.isNumber(sidC) else "string" # Some ids are ints
		idTriple+=ctm.propTriple(isoTitle,{"hasSampleID":sidC},litCType,True)

	# Alternate collection id is stored alongside original collection id.
	if not pd.isnull(cidA):
		cidA=cn.cleanInt(cidA)
		if re.search("[aA]lt",cidA) is not None:
			cids=cidA.split(" ")
			cidA=cids[0]
			cidA=cidA[:len(cidA)-1] # Get rid of the semi colon at the end
			cidB=cids[len(cids)-1] # Get the last item in the cids list

			cidB=cn.cleanInt(cidB)
			litCBType="int" if cn.isNumber(cidB) else "string" # Some ids are ints	
			idTriple+=ctm.propTriple(isoTitle,{"hasCollectionID":cidB},"string",True)

		litCAType="int" if cn.isNumber(cidA) else "string" # Some ids are ints			
		idTriple+=ctm.propTriple(isoTitle,{"hasCollectionID":cidA},litCAType,True)

	if comment!="":
		idTriple+=ctm.propTriple(isoTitle,{"hasComment":sidB},"string")

	return idTriple

