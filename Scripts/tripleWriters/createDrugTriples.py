from labTM import lab as ltm

######################################################################################################
#
######################################################################################################
def createDrugTriples(df):
	dTriple=""
	cols=list(df.columns.values) # Get all the column names
	drugs=cols[cols.index("mic_azm"):cols.index("mic_tet")+1]
	drugs=[d.replace("mic_","") for d in drugs]

	for d in drugs:
		dTriple+=ltm.indTriple(d,"AMRdrug")

	return dTriple