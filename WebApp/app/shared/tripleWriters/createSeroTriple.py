from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm
def createSeroTriple(isoTitle, serotype, antigen):
    triple = ""
    title = "sero_{}".format(isoTitle)
    seroTitle = "{}_{}".format(serotype, antigen)
    if serotype and antigen:
        triple += ltm.indTriple(seroTitle, "Serotype_test")
        triple += ltm.propTriple(seroTitle, {"hasSerotype":"0"}, True, True)
        triple += ltm.propTriple(seroTitle, {"hasAntigen":"O"})
        triple += ltm.propTriple(title, {"foundSerotype":seroTitle})
        triple += tm.multiURI((isoTitle, "hasLabTest", title), (ctm.uri, ctm.uri, ltm.uri))

    return triple

