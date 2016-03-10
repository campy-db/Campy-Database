import pandas as pd
import campyTM as ctm
import re
import cleanCSV as cn

######################################################################################################
#
######################################################################################################
def createIDtriples(df,row,isoTitle):
	isoTriple=""
	nmlid=df["NML ID#"][row]
	ldmsid=df["LDMS ID"][row]
	origName=df["Mostly Original Sample Names (might have project prefixes!)"][row] # lol
	isoLocA=df["Isolate Location 1"][row]
	isoLocB=df["Isolate Location 2"][row]
	isoLoc=""
	sidA=df["Alternate Sample ID"][row]  # Sample id
	sidB=df["Alt. Sample ID"][row]
	sidC=df["C-EnterNet Number"][row]
	cidA=df["Sample Collection ID"][row] # Collection id
	cidB=""
	dateAdded=df["Date Added to Database"][row]

	# Add the nmlID, ldmsID and original sample name
	if not pd.isnull(nmlid) and cn.isGoodVal(nmlid) and nmlid!="0":
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasNMLid":nmlid},"string",True)

	if not pd.isnull(ldmsid) and cn.isGoodVal(ldmsid):
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasLDMSid":ldmsid},"string",True)
	if not pd.isnull(origName) and cn.isGoodVal(origName):
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasOriginalName":origName},"string",True)

	# As the isolate's physical location
	if not pd.isnull(isoLocA) and cn.isGoodVal(isoLocA):
		isoLoc=isoLocA
	if not pd.isnull(isoLocB) and cn.isGoodVal(isoLocB):
		isoLoc=isoLocB
	if isoLoc!="":
		isoTriple+=ctm.campy.indTriple(isoLoc,"IsolateLocation")
		isoTriple+=ctm.campy.propTriple(isoLoc,{"hasName":isoLoc},"string")
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasIsolateLocation":isoLoc})

	# Add the isolate's many sample ID's. Don't add the ID if it is the same as the isoTitle
	# or other the other IDs before it
	if not pd.isnull(sidA) and cn.isGoodVal(sidA):
		# Sometimes the Alternate ID is the strain name but with an - instead of _. This causes
		# problems with the reified literals. Note even if it is the same as the strain name as
		# some other strains may have the same sample id
		if cn.compare([isoTitle,sidA]):
			sidA=isoTitle

		litAType="int" if cn.isNumber(sidA) else "string" # Some ids are ints
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasSampleID":sidA},litAType,True)

	if not pd.isnull(sidB) and cn.isGoodVal(sidB):
		if cn.compare([isoTitle,sidB]):
			sidB=isoTitle
		
		litBType="int" if cn.isNumber(sidB) else "string" # Some ids are ints
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasSampleID":sidB},litBType,True)

	if not pd.isnull(sidC) and cn.isGoodVal(sidC):
		if cn.compare([isoTitle,sidC]):
			sidC=isoTitle

		litCType="int" if cn.isNumber(sidC) else "string" # Some ids are ints
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasSampleID":sidC},litCType,True)

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
			isoTriple+=ctm.campy.propTriple(isoTitle,{"hasCollectionID":cidB},"string",True)

		litCAType="int" if cn.isNumber(cidA) else "string" # Some ids are ints			
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasCollectionID":cidA},litCAType,True)

	if not pd.isnull(dateAdded):
		dateAdded=cn.convertDate(dateAdded)
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasDateAdded":dateAdded},"string",True)

	return isoTriple
