from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.resistanceDictionary import getBreakpoints
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm

def createOutbreakTriple(isoTitle, data):
    def createDateTriple(title, predicate, data):
        if data:
            return ctm.propTriple(str(title), {predicate:str(data.data)}, True, True)

    #control needed?
    triple = ctm.propTriple(isoTitle, {"isPartOfOutbreak":True}, True, True)
    outbreakTitle = ""

    if data["name"]:
        outbreakTitle = str(data["name"].data)
        triple += ctm.indTriple(str(outbreakTitle), "Outbreak")
        triple += ctm.propTriple(isoTitle, {"partOfOutbreak":outbreakTitle})
        triple += ctm.propTriple(str(outbreakTitle), {"hasName":"\""+outbreakTitle+"\""}, True)

        if data["upper"]["year"]:
            upperTitle = outbreakTitle +"_"+isoTitle+"upper"
            lowerTitle = outbreakTitle +"_"+isoTitle+"lower"
            print("TITLE: " + upperTitle)
            triple += ctm.propTriple(str(outbreakTitle), {"hasOutbreakDateLowerBound":lowerTitle})
            triple += ctm.propTriple(str(outbreakTitle), {"hasOutbreakDateUpperBound":upperTitle})

            triple += createDateTriple(lowerTitle, "hasOutbreakDayLowerBound", data["lower"]["day"])
            triple += createDateTriple(lowerTitle, "hasOutbreakMonthLowerBound", data["lower"]["month"])
            triple += createDateTriple(lowerTitle, "hasOutbreakYearLowerBound", data["lower"]["year"])

            triple += createDateTriple(upperTitle, "hasOutbreakDayUpperBound", data["upper"]["day"])
            triple += createDateTriple(upperTitle, "hasOutbreakMonthUpperBound", data["upper"]["month"])
            triple += createDateTriple(upperTitle, "hasOutbreakYearUpperBound", data["upper"]["year"])

        elif data["lower"]["year"]:
            singleTitle = outbreakTitle +"_"+isoTitle+"simgle"
            triple += ctm.propTriple((str(outbreakTitle), {"hasOutbreakDate":singleTitle}))
            triple += createDateTriple(singleTitle, "hasOutbreakDay", data["lower"]["day"])
            triple += createDateTriple(singleTitle, "hasOutbreakMonth", data["lower"]["month"])
            triple += createDateTriple(singleTitle, "hasOutbreakYear", data["lower"]["year"])
    return triple


