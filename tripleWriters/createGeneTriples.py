import labTM as ltm
import campyTM as ctm
import cleanGene as cg

#####################################################################################################
#
######################################################################################################
def createGeneTriples(df):
	triple=""
	cols=list(df.columns.values) # Get all the column names
	aGenes=cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract allelic typing genes
	cgfGenes=cols[cols.index("cj0008 (486bp)"):cols.index("cj1727c (369bp)")+1] # Extract cgf genes

	for a in aGenes:
		a=cg.cleanGene(a)

		triple+=ltm.lab.indTriple(a,"AllelicTypingGene")
		# HOW SHOULD WE HANDLE MULTI URI TRIPLES?
		triple+=ltm.lab.addUri(a)+" "+ctm.campy.addUri("hasName")+" \"%s\" ." % (a)

	for c in cgfGenes:
		triple+=ltm.lab.indTriple(c,"CGFtypingGene")
		# ???????????
		triple+=ltm.lab.addUri(c)+" "+ctm.campy.addUri("hasName")+" \"%s\" ." % (c)
		
	return triple