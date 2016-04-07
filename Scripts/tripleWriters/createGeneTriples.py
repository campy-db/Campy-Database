"""
 createGeneTriples
"""

from Scripts.TripleMaker import TripleMaker as tm
from .. import cleanCSV as cn
from .labTM import LAB as ltm
from .campyTM import CAMPY as ctm

def createGeneTriples(df):

	# Get all the column names
    cols = list(df.columns.values)

    # Extract allelic typing genes
    aGenes = cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1]

    # Extract cgf genes
    cgfGenes = cols[cols.index("cj0008 (486bp)"):cols.index("cj1727c (369bp)")+1]


    def gene_triple(g, gtype):
        triple = ltm.indTriple(g, gtype) +\
                 tm.multiURI((g, "hasName", "\"{}\"".format(g)), (ltm.uri, ctm.uri), True)
        return triple

    gene_triples = [gene_triple(cn.cleanGene(g), "Allelic_typing_gene") for g in aGenes] +\
                   [gene_triple((g), "CGF_typing_gene") for g in cgfGenes]
                   # Note that allelic typing genes in the csv need to be cleaned but
                   # the cgf ones are fine as is

    return "".join(gene_triples)
