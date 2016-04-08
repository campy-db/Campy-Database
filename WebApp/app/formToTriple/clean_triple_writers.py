"""
 clean_triple_writers.py
"""

from Scripts.TripleMaker import TripleMaker as tm
from Scripts import TripleMaker
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.tripleWriters.labTM import LAB as ltm
from Scripts import cleanCSV as cn

####################################################################################################
# GLOBAL VARIABLES
####################################################################################################
CAMPY = "https://github.com/samuel-peers/CAMPYOntology/blob/master/CampyOntology2.0.owl#"
LAB = "https://github.com/samuel-peers/CAMPYOntology/blob/master/LabTests.owl#"
LIT = "http://www.essepuntato.it/2010/06/LITeralreification/"
LITTM = TripleMaker.TripleMaker(LIT)

####################################################################################################
# Pop all the empty values from a dictionary
####################################################################################################
def popVals(my_dict):
    return {x:y for x, y in my_dict.iteritems() if y != ""}

####################################################################################################
# createIsolateTriple
####################################################################################################
def createIsolateTriple(iso_title, species, sub_species):

    triple = ctm.indTriple(iso_title, "Isolate")+\
             ctm.propTriple(iso_title, {"hasIsolateName":iso_title}, True, True)

    triple += ctm.propTriple(iso_title, {"hasSpecies":species}) if species else ""
    triple += ctm.propTriple(iso_title, {"hasSubSpecies":sub_species}) if sub_species else ""

    return triple


####################################################################################################
# createCGFtriple
####################################################################################################
def createCGFtriple(data, iso_title):

    title = "cgf_{}".format(iso_title)

    litProps = popVals({"hasDayCompleted":data["day"], \
                        "hasMonthCompleted":data["month"], \
                        "hasYearCompleted":data["year"], \
                        "foundFingerprint":data["fingerprint"], \
                        "isInSilico":data["silico"]})

    props = popVals({"doneAtLAB":data["lab"]})

    # If there is actually any CGF data, isInSilico is False by default
    if "isInSilico" not in litProps.keys() and litProps or props:
        litProps["isInSilico"] = False

    triple = ltm.propTriple(title, litProps, True, True) if litProps else ""

    triple += ltm.propTriple(title, props) if props else ""

    triple += ltm.indTriple(title, "CGF_test") if triple else ""

    triple += tm.multiURI((iso_title, "hasLABTest", title), (ctm.uri, ctm.uri, ltm.uri))\
              if triple else ""

    triple += tm.multiURI((data["lab"], "hasName", "\"{}\"".format(data["lab"])),\
              (ctm.uri, ctm.uri, ltm.uri)) if data["lab"] else ""

    return triple


####################################################################################################
# createAnimalTriple
####################################################################################################
def createAnimalTriple(data, iso_title):

    animal, locale, type_ = data["animal"], data["locale"], data["type"]

    title = "{}_{}".format(animal, iso_title) if animal else ""

    name = "{} {}".format(locale, animal) if locale else animal

    props = popVals({"hasAnimalID":data["aID"],
                     "hasName":name,
                     "hasSex":data["sex"],
                     "hasAgeRank":data["age"]})

    triple = ctm.indTriple(title, animal) if animal else ""

    triple += ctm.indTriple(title, type_) if type_ else ""

    triple += ctm.propTriple(title, props, True, True) if props else ""

    triple += ctm.propTriple(iso_title, {"hasSampleSource":title}) if title else ""

    triple += ctm.propTriple(iso_title, {"hasSampleLocale":locale}, True, True) if locale else ""

    return triple
