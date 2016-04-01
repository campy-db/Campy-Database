import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts.TripleMaker import TripleMaker as tm
from Scripts import TripleMaker
from Scripts.tripleWriters.campyTM import campy as ctm
from Scripts.tripleWriters.labTM import lab as ltm
from Scripts import cleanCSV as cn

######################################################################################################
# Global variables
######################################################################################################
campy = "https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#"
lab = "https://github.com/samuel-peers/campyOntology/blob/master/LabTests.owl#"
lit = "http://www.essepuntato.it/2010/06/literalreification/"
litTM = TripleMaker.TripleMaker(lit) 

######################################################################################################
# 
######################################################################################################
def popVals(my_dict):

	for d in my_dict.keys():
		my_dict.pop(d, None) if my_dict[d] == "" else None

	return my_dict

######################################################################################################
# createIsolateTriple
######################################################################################################
def createIsolateTriple(isoTitle):

	return ctm.indTriple(isoTitle,"Isolate")+\
	       ctm.propTriple(isoTitle,{"hasIsolateName":isoTitle},"string",True)

######################################################################################################
# createSourceTriple
######################################################################################################
def createSourceTriple(source, isoTitle):
	return ""

######################################################################################################
# createCGFtriple
######################################################################################################
def createCGFtriple(data, isoTitle):

	title = "cgf_" + isoTitle

	litProps = popVals({ "hasDayCompleted":data["day"], 
                         "hasMonthCompleted":data["month"], 
	                     "hasYearCompleted":data["year"],
                         "foundFingerprint":data["fingerprint"],
	                     "isInSilico":data["silico"] } )

	props = popVals({ "doneAtLab":data["lab"] })

	# If there is actually any CGF data, isInSilico is False by default
	if "isInSilico" not in litProps.keys() and litProps or props:
		litProps["isInSilico"] = False 

	triple = ltm.propTriple(title, litProps, True, True) if litProps else ""

	triple += ltm.propTriple(title, props) if props else ""

	triple += ltm.indTriple(title, "CGF_test") if triple else ""

	triple += tm.multiURI((isoTitle, "hasLabTest", title), (ctm.uri, ctm.uri, ltm.uri))\
	          if triple else "" 

	triple += tm.multiURI((data["lab"], "hasName", "\"{}\"".format(data["lab"])), 
		      (ctm.uri, ctm.uri, ltm.uri)) if data["lab"] else ""

	return triple


######################################################################################################
# createAnimalTriple
######################################################################################################
def createAnimalTriple(data, isoTitle):

    animal = data["animal"]

    locale = data["locale"] 

    title = "{}_{}".format(animal, isoTitle) if animal else ""

    name = "{} {}".format(locale, animal) if locale else animal

    if locale:
        domestic = True if locale in ("domestic", "retail", "abattoir", "farm") else False
    else:
        domestic = ""

    props = popVals({ "hasAnimalID":data["aID"], 
                      "hasName":name, 
                      "hasSex":data["sex"], 
                      "hasAgeRank":data["age"],
                      "isDomestic":domestic })

    triple = ctm.indTriple(title, animal) if animal else ""

    triple += ctm.propTriple(title, props, True, True) if props else ""

    triple += ctm.propTriple(isoTitle, {"hasSampleSource":title}) if title else ""

    triple += ctm.propTriple(isoTitle, {"hasSampleLocale":locale}, True, True) if locale else ""

    return triple