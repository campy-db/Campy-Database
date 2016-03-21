import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
from campyTM import campy as ctm
import re

######################################################################################################
# createRefTriples
# Handles the reference strains. Most don't have source info,  but some have just a little bit. There
# are only animal and human sources so we just worry about those. THIS COULD CHANGE.
######################################################################################################
def createRefTriples(df, row, isoTitle):
	
	rTriple = ""

	source = df["Source_Specific_2"][row]

	animalID = df["Animal ID"][row]

	ref = df["Dataset ID_1"][row]


	if not pd.isnull(ref):
		
		# Not all strains are reference strains. The column dataset id_1 says whether
		# a strain is a reference strain or not
		if re.search("[Rr]eference[ -_][Ss]train", ref) is not None:

			rTriple = ctm.propTriple(isoTitle, {"isReferenceStrain":True}, True, True)

			if not pd.isnull(source) and cn.isGoodVal(source):
				
				if re.search("[Hh]uman", source) is not None:
					
					# Use the human naming convention
					title = "{}_{}".format("patient", isoTitle) 
					sClass = "Patient"
					
				else: # It's an animal source
				
					source = cn.remPrefix(source, 2)
					sClass = source
					
					if not pd.isnull(animalID):
						title = cn.cleanInt(animalID) # Use animal ID if available
					else:
						# Else use animal naming convention
						title = "{}_{}".format(source, isoTitle) 

					
				# We don't know if the animal is a Ruminant,  or what have you,  so we just set it as an 
				# instance of whatever kind of animal it is,  eg cowC1004 is an instance of cow. We just pray 
				# that that animal has already been set as an instance of whatever family it belongs to 
				# earlier when we handled the animal source triples. If it's a human its just an instance 
				# of Patient.
				rTriple += ctm.indTriple(title, sClass)
				rTriple += ctm.propTriple(isoTitle, {"hasSampleSource":title})

	return rTriple
