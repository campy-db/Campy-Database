import pandas as pd
import campyTM as ctm
import labTM as ltm
import re
import cleanCSV as cn

######################################################################################################
#
######################################################################################################
def createAMRtriples(df,row,isoTitle):
	aTriple=""
	cols=list(df.columns.values) # Get all the column names
	mic_drugs=cols[cols.index("mic_azm"):cols.index("mic_tet")+1] # Get all the drugs with 'mic_'
	r_drugs=cols[cols.index("razm"):cols.index("rtet")+1] # Get all the drugs with 'r' prefix
	drugs=[d.replace("mic_","") for d in mic_drugs] # Remove the prefix to get drug names
	testTitle="amr_"+isoTitle
	amr=df["AMR"][row] # The column 'AMR' also has some info related to drug resistance

	# Get the mics first
	for m in mic_drugs:
		mic=df[m][row]
		drug=m.replace("mic_","") # Remove the 'mic_' prefix
		if not pd.isnull(mic):
			# Not all of them are floats, and they should be.
			mic=str(float(mic)) if cn.isNumber(mic) else str(mic) 
			dmTitle=mic+"_"+drug
			aTriple+=ltm.lab.indTriple(dmTitle,"DrugMIC")

			# NOTE: All mics are being stored as strings in the ontology as some of the mics have
			# < or > in them. We don't like this.
			aTriple+=ltm.lab.propTriple(dmTitle,{"hasMIC":mic},"string",True)
			aTriple+=ltm.lab.propTriple(dmTitle,{"hasDrug":drug})
			aTriple+=ltm.lab.propTriple(testTitle,{"foundMIC":dmTitle})


	# Handle the random drug resistance in column 'AMR'. The only value 
	# in this column is 'Nal R'
	if not pd.isnull(amr):
		drug=amr.split(" ")[0].lower() # All the other drugs are lower case
		aTriple+=ltm.lab.propTriple(testTitle,{"foundResistanceTo":drug})


	for r in r_drugs:
		res=df[r][row]
		drug=re.sub("^r","",r) # Remove the 'r' prefix
		if not pd.isnull(res):
			res=int(res) # It's stored as a double, we need an int
			if res==1: # The strain is resistant
				aTriple+=ltm.lab.propTriple(testTitle,{"foundResistanceTo":drug})
			else: # The strain is sensitive
				aTriple+=ltm.lab.propTriple(testTitle,{"foundSusceptibilityTo":drug})
	

	if aTriple!="":
		aTriple+=ltm.lab.indTriple(testTitle,"AMRtest")
		aTriple+=ctm.campy.addUri(isoTitle)+" "+ctm.campy.addUri("hasLabTest")+\
			     " "+ltm.lab.addUri(testTitle)+" ."

	return aTriple