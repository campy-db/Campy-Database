import pandas as pd
import campyTM as ctm
import re
import cleanCSV as cn

######################################################################################################
# createRefTriples
# Handles the reference strains. Most don't have source info, but some have just a little bit. There
# are only animal and human sources so we just worry about those. THIS COULD CHANGE.
######################################################################################################
def createRefTriples(df,row,isoTitle):
	rTriple=""
	source=df["Source_Specific_2"][row]
	animalID=df["Animal ID"][row]
	ref=df["Dataset ID_1"][row]

	if not pd.isnull(ref):
		# Not all strains are reference strains. The column dataset id_1 says whether
		# a strain is a reference strain or not
		if re.search("[Rr]eference[ -_][Ss]train",ref) is not None:

			rTriple=ctm.campy.propTriple(isoTitle,{"isReferenceStrain":"true"},"bool",True)

			if not pd.isnull(source) and cn.isGoodVal(source):
				if re.search("[Hh]uman",source) is not None:
					title="patient_"+isoTitle # Use the human naming convention
					sClass="Patient"
				else: # It's an animal source
					source=cn.remPrefix(source,2)
					sClass=source
					if not pd.isnull(animalID):
						title=cn.cleanInt(animalID) # Use animal ID if available
					else:
						title=source+"_"+isoTitle # Else use animal naming convention

					
				# We don't know if the animal is a Ruminant, or what have you, so we just set it as an 
				# instance of whatever kind of animal it is, eg cowC1004 is an instance of cow. We just pray 
				# that that animal has already been set as an instance of whatever family it belongs to 
				# earlier when we handled the animal source triples. If it's a human its just an instance 
				# of Patient.
				rTriple+=ctm.campy.indTriple(title,sClass)
				rTriple+=ctm.campy.propTriple(isoTitle,{"hasSampleSource":title})

	return rTriple