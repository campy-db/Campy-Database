from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.geneDictionary import getAGenes, getMLSTGenes
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createTypingTriple(data, isoTitle):
    triple = ""
    mTitle = "{}_{}".format("mlst", isoTitle)
    if data["Clonal Complex"]:
        triple += ltm.propTriple(mTitle, {"foundClonalComplex":data["Clonal Complex"]}, True, True)

    if data["ST"]:
        triple += ltm.propTriple(mTitle, {"foundST":int(data["ST"])}, True, True)
        triple +=  ltm.indTriple(mTitle, "MLST_test")
        triple += tm.multiURI((isoTitle, "hasLabTest", mTitle), (ctm.uri, ctm.uri, ltm.uri))


    def alleleTriple(gene, data):
        triple = ""
        print (">>>>>>>>>>>>>>>" + str(data))
        geneIndex = int(data[gene])
        if geneIndex:
            alTitle = "{}_{}".format(gene, geneIndex)
            tClass = "{}_test".format(gene)
            tTitle =  mTitle if gene in data.keys() else "{}_{}".format(tClass, isoTitle)
            triple += ltm.propTriple(tTitle, {"foundAllele":alTitle})

            triple += ltm.indTriple(alTitle, "Typing_allele") +\
                     ltm.propTriple(alTitle, {"isOfGene:":gene}) +\
                     ltm.propTriple(alTitle, {"hasAlleleIndex": geneIndex}, True, True)
                     
            triple += ltm.indTriple(tTitle, tClass) +\
                      ltm.propTriple(tTitle, {"foundAllele":alTitle}) +\
                      tm.multiURI((isoTitle, "hasLabTest", tTitle), (ctm.uri, ctm.uri, ltm.uri))
        return triple

    def alleleTripleMLST(gene, data):
        triple = ""
        geneIndex = int(data[gene])
        if geneIndex:
            alTitle = "{}_{}".format(gene, geneIndex)
            tClass = "{}_test".format(gene)
            tTitle =  mTitle if gene in data.keys() else "{}_{}".format(tClass, isoTitle)
            triple += ltm.propTriple(tTitle, {"foundAllele":alTitle})

            triple += ltm.indTriple(alTitle, "Typing_allele") +\
                      ltm.propTriple(alTitle, {"isOfGene:":gene}) +\
                      ltm.propTriple(alTitle, {"hasAlleleIndex": int(geneIndex)}, True, True)
        return triple

    triplesAGenes = [alleleTriple(g, data["aGenes"]) for g in getAGenes()]
    triplesMLSTGenes = [alleleTripleMLST(g, data["mlstGenes"]) for g in getMLSTGenes()]

    triples = "".join(triplesAGenes) + "".join(triplesMLSTGenes)
    triple += "".join(triples)

    return triple



    




