from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.resistanceDictionary import getBreakpoints
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createDrugResistanceTriple(data, isoTitle, species):

    def micTriple(mic_value, drug, test_title):
        dm_title = "{}_{}".format(mic_value, drug);
        triple = ltm.indTriple(dm_title, "DrugMIC") + \
        ltm.propTriple(dm_title, {"hasMIC": mic_value}, True, True) + \
        ltm.propTriple(dm_title, {"hasDrug": drug}) + \
        ltm.propTriple(test_title, {"foundMIC": dm_title})
        return triple

    def resTriple(data, drug, testTitle):
        if isResistant(drug, data, species): 
            triple = ltm.propTriple(testTitle, {"foundResistanceTo": drug})
        else:
            triple = ltm.propTriple(testTitle, {"foundSusceptibiltyTo": drug})
        return triple

    def isResistant(drug, data, species):
        resDict = getBreakpoints(species)
        if(float(data[drug].lstrip(">")) >= float(resDict[drug])):
            return True
        else:
            return False
    
    testTitle = "amr_" + isoTitle


    micTriples = [micTriple(data[drug], drug, testTitle)
                 for drug in data
                 if not data[drug] == ""]
    if species:
        resTriples = [resTriple(data, drug, testTitle)
                     for drug in data
                     if not data[drug] == ""]

        triples = micTriples + resTriples 
        if triples: 
            triples += [ltm.indTriple(testTitle, "AMR_test"),
                tm.multiURI((isoTitle, "hasLabTest", testTitle), (ctm.uri, ctm.uri, ltm.uri))]
        return "".join(triples)
    else:
        if micTriples:
            micTriples += [ltm.indTriple(testTitle, "AMR_test"),
                tm.multiURI((isoTitle, "hasLabTest", testTitle), (ctm.uri, ctm.uri, ltm.uri))]
        return "".join(micTriples)









