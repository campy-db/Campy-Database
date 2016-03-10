import pandas as pd
import campyTM as ctm
import labTM as ltm
import cleanCSV as cn
import cleanGene as cg

######################################################################################################
#
######################################################################################################
def createTypingTriples(df,row,isoTitle):
	testTriple=""
	mTriple=""
	cols=list(df.columns.values) # Get all the column names

	genes=cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract gene names
	# The names of the tests are just the name of the gene they test plus isoTitle, but MLST tests
	# 7 genes, so mlst test name will be 'mlst'+isoTitle
	mlstGenes=genes[genes.index("Asp"):genes.index("Unc (atpA)")+1] 
	cloComp=df["Clonal Complex"][row] # For mlst only
	st=df["ST"][row] # For mlst only
	mTitle="mlst_"+isoTitle

	# The value 'none' is in cloComp right now. Ignore it...for now
	if not pd.isnull(cloComp) and "none" not in cloComp:
		# The values ST-403 and ST_403 are in the csv. We'll standardize it to ST_403
		cloComp=cloComp.replace("-","_")

		mTriple+=ltm.lab.propTriple(mTitle,{"foundClonalComplex":cloComp},"string",True)

	# The value 'new' is in ST. We'll ignore it as well...for....now....
	if not pd.isnull(st) and "new" not in st:
		st=cn.cleanInt(st)
		mTriple+=ltm.lab.propTriple(mTitle,{"foundST":st},"int",True)

	# Go through all the genes, get the allele index, create allele, attach allele to gene,
	# add the allele index to the allele, attach the test to the allele.
	for g in genes:
		alIndex=df[g][row]
		if not pd.isnull(alIndex) and cn.isNumber(alIndex):
			alIndex=cn.cleanInt(alIndex)
			alTitle=cg.cleanGene(g)+"_"+alIndex
			testTriple+=ltm.lab.indTriple(alTitle,"TypingAllele")
			testTriple+=ltm.lab.propTriple(alTitle,{"isOfGene":cg.cleanGene(g)})
			testTriple+=ltm.lab.propTriple(alTitle,{"hasAlleleIndex":alIndex},"int",True)

			if g in mlstGenes:
				mTriple+=ltm.lab.propTriple(mTitle,{"foundAllele":alTitle})
			else:
				testClass=cg.cleanGene(g)+"test"
				testTitle=testClass+"_"+isoTitle
				testTriple+=ltm.lab.indTriple(testTitle,testClass)
				testTriple+=ltm.lab.propTriple(testTitle,{"foundAllele":alTitle})
				testTriple+=ctm.campy.addUri(isoTitle)+" "+ctm.campy.addUri("hasLabTest")+" "\
						    +ltm.lab.addUri(testTitle)+" ."

	if mTriple!="":
		mTriple+=ltm.lab.indTriple(mTitle,"MLSTtest")	
		mTriple+=ctm.campy.addUri(isoTitle)+" "+ctm.campy.addUri("hasLabTest")+\
			   " "+ltm.lab.addUri(mTitle)+" ."

	return mTriple+testTriple