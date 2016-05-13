from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createSMATriple(isoTitle, pulsovar):
    triple = ""
    title = "sma1_" + isoTitle
    triple += ltm.indTriple(title, "SMA1_test")
    triple += ltm.propTriple(title, {"foundPulsovar":str(pulsovar)}, True, True)
    triple += tm.multiURI((isoTitle, "hasLabTest", title), (ctm.uri, ctm.uri, ltm.uri))

    return triple








