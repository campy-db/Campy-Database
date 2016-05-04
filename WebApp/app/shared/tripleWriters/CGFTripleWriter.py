from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm
from ..util import popVals as popVals

def CGFTripleWriter(data, iso_title):

    triple = []

    title = "cgf_{}".format(iso_title)

    litProps = popVals({"hasDayCompleted":data["day"], \
                        "hasMonthCompleted":data["month"], \
                        "hasYearCompleted":data["year"], \
                        "foundFingerprint":data["fingerprint"], \
                        "isInSilico":data["silico"]})

    typing_lab = data["lab"]

    # If there is actually any CGF data, isInSilico is False by default
    if "isInSilico" not in litProps.keys() and litProps or typing_lab:
        litProps["isInSilico"] = False

    if litProps:
        triple.append(ltm.propTriple(title, litProps, True, True))

    if triple:
        triple.append(ltm.indTriple(title, "CGF_test"))

    if triple:
        triple.append(tm.multiURI((iso_title, "hasLABTest", title), (ctm.uri, ctm.uri, ltm.uri)))

    if typing_lab:

        triple.append(ltm.propTriple(title, {"doneAtLab":typing_lab}))

        triple.append(tm.multiURI((typing_lab, "hasName", "\"{}\"".format(typing_lab)),\
                      (ctm.uri, ctm.uri, ltm.uri), isLiteral=True))

    return "".join(triple)