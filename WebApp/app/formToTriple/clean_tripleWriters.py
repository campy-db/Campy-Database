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
		my_dict.pop(d, None) if not my_dict[d] else None

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

	litProps = popVals({ "hasDayCompleted":data["day"], "hasMonthCompleted":data["month"], 
	                     "hasYearCompleted":data["year"], "foundFingerprint":data["fingerprint"],
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

    title = "{}_{}".format(data["animal"], isoTitle) if data["animal"] else ""
    title = data["aID"] if data["aID"] else title

    type_class = data["type"] if data["type"] else ""

    name = "{} {}".format(type_class.replace("_type", "").lower(), data["animal"])\
            if type_class else data["animal"]

    props = popVals({ "hasName":name, "hasSex":data["sex"], "hasAgeRank":data["age"] })

    triple = ctm.indTriple(title, data["animal"]) if data["animal"] else ""

    triple += ctm.indTriple(title, type_class) if type_class and title else ""

    triple += ctm.propTriple(title, props, True, True) if title and props else ""

    return triple