import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts.TripleMaker import TripleMaker as tm
from Scripts import cleanCSV as cn
from labTM import lab as ltm
from campyTM import campy as ctm

#####################################################################################################
#
######################################################################################################
def createGeneTriples(df):

	cols = list(df.columns.values) # Get all the column names
	aGenes = cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract allelic typing genes
	cgfGenes = cols[cols.index("cj0008 (486bp)"):cols.index("cj1727c (369bp)")+1] # Extract cgf genes


	def gene_triple(g, gtype):
		triple = ltm.indTriple(g, gtype) +\
				 tm.multiURI((g,"hasName","\"{}\"".format(g)), (ltm.uri,ctm.uri), True)
		return triple

	gene_triples = [gene_triple(cn.cleanGene(g), "AllelicTypingGene") for g in aGenes] +\
	               [gene_triple((g), "CGFtypingGene") for g in cgfGenes]
	               # Note that allelic typing genes in the csv need to be cleaned but
	               # the cgf ones are fine as is
	               
	return "".join(gene_triples)