from Scripts.tripleWriters.campyTM import CAMPY as ctm

def createDTakenTriples(isoTitle, data):
    triple = ""

    if data["day"]:
        triple = ctm.propTriple(isoTitle, {"hasDaySampleTaken":data["day"]})
    if data["month"]:
        triple += ctm.propTriple(isoTitle, {"hasMonthSampleTaken:":data["month"]})
    if data["year"]:
        triple += ctm.propTriple(isoTitle, {"hasYearSampleTaken:":data["year"]})
    return triple

