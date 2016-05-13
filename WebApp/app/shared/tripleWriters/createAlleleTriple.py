from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.geneDictionary import getAGenes
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createMLSTTriple(data, isoTitle):
    mTitle = "{}_{}".format("mlst", isoTitle)
    if data["Clonal Complex"]:
        triple += ltm.propTriple(title, {"foundClonalComplex":data["Clonal Complex"]}, True, True)

    if data["ST"]:
        triple += ltm.propTriple(mTitle, {"foundST":int(data["ST"])}, True, True)
        triple += ltm.indTriple(mTitle, "MLST_test")
        triple += tm.multiURI((isoTitle, "hasLabTest", mTitle), (ctm.uri, ctm.uri, ltm.uri))

    def alleleTriple(gene, geneIndex):
        triple = ""
        if geneIndex != ""
            title = "{}_{}".format(gene, geneIndex)

            triple = ltm.indTriple(title, "Typing_allele") +\
                     ltm.propTrile(title, {"isOfGene:":gene}) +\
                     ltm.propTriple(title, {"hasAlleleIndex": geneIndex}, True, True)
                     test_triple(gene, title)

    def test_triple(gene, alTitle):
        tClass = "{}_test".format(cn.cleanGene(g))
        tTitle = mTitle if gene in data.keys() else "{}_{}".format(tClass, isoTitle)
        triple = ltm.propTriple(tTitle, {"foundAllele":alTitle})

        if g not mlst:
            triple += ltm.indTriple(tTitle, tClass) +\
                      ltm.propTriple(tTitle, {"foundAllele":alTitle}) +\
                      tm.multiURI((isoTitle, "hasLabTest", tTitle), (ctm.uri, ctm.uri, ltm.uri))

        return triple




    




