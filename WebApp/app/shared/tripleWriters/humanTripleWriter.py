from Scripts.tripleWriters.campyTM import CAMPY as ctm
from ..util import popVals as popVals

def humanTripleWriter(data, iso_title):
    triple = []

    h_triple = ""

    c_type = data["clinical_type"]

    # We assume all human samples are clinical for now
    c_type = "clinical" if not c_type else c_type

    h_title = "{} {}".format(iso_title, "patient")

    rlit_props = popVals({"hasPatientID":data["pID"],
                          "hasAge":data["age"],
                          "hasGender":data["gender"],
                          "hasPostalCode":data["postal_code"]})

    props = popVals({"traveledTo":data["travel"]})

    # All human source are assumed to be patients
    triple.append(ctm.indTriple(h_title, "Patient"))
    triple.append(ctm.propTriple(h_title, {"hasName":"patient"}, True))
    triple.append(ctm.propTriple(iso_title, {"hasHumanSource":h_title}))

    if rlit_props:
        h_triple = ctm.propTriple(h_title, rlit_props, isLiteral=True, rLiteral=True)
        triple.append(h_triple)
    if props:
        h_triple = ctm.propTriple(h_title, props)
        triple.append(h_triple)

    return "".join(triple)
