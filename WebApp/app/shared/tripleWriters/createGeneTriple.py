from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createGeneTriple(gene, geneType):
    if geneType == "cgf":
        gType = "CGF_typing_gene"
    elif geneType == "allele":
        gType = "Allelic_typing_gene"

    triple = ltm.indTriple(gene, gType) +\
                 tm.multiURI((gene, "hasName", "\"{}\"".format(gene)), (ltm.uri, ctm.uri), True)
    return triple





