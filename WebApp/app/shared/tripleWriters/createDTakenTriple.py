from Scripts.tripleWriters.campyTM import CAMPY as ctm

def createDTakenTriple(isoTitle, data):
    triple = ""

    if data["day"]:
        triple = ctm.propTriple(isoTitle, {"hasDaySampleTaken":data["day"]}, True, True)
    if data["month"]:
        triple += ctm.propTriple(isoTitle, {"hasMonthSampleTaken:":data["month"]}, True, True)
    if data["year"]:
        triple += ctm.propTriple(isoTitle, {"hasYearSampleTaken:":data["year"]}, True, True)
    return triple

