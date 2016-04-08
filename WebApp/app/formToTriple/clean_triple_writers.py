"""
 clean_triple_writers.py

 Takes in values and creates the appropriate triples. All cleaning is done here.
"""

import re
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
def createIsolateTriple(iso_title, spec_str):

    triple = []

    subspec_syns = ["subspecies", "subspec.", "subspec", "spp.", "subsp.", "subsp"]

    if not spec_str:
        return ""

    triple.append(ctm.indTriple(iso_title, "Isolate")+\
                  ctm.propTriple(iso_title, {"hasIsolateName":iso_title}, True, True))

    # Returns the largest string in subspec_syns that is in v. Note we could just sort the list
    # manually, but if we decide to add synonyms to subspec_syns in the future,
    # this would be error prone
    subspec_delim = ""
    for ss in sorted(subspec_syns, key=len, reverse=True):
        if spec_str.find(ss) != -1:
            subspec_delim = ss
            break

    spec_str = re.sub(r"[Cc]ampy(lobacter)?", "", spec_str).strip().lower()

    is_cf_spec = True if spec_str.find("cf.") != -1 else False

    subspec = ""

    if is_cf_spec:

        spec = spec_str.split("cf.")[1]

    elif subspec_delim:

        specs = spec_str.split(subspec_delim)
        spec, subspec = specs[0], specs[1]

    elif spec_str.find("+") != -1:

        spec = spec_str.split("+")

    else:

        spec = spec_str


    if not is_cf_spec:

        spec = [spec] if not isinstance(spec, list) else spec

        for s in spec:

            s = s.strip()
            triple.append(ctm.propTriple(iso_title, {"hasSpecies":s}))

    else:
        triple.append(ctm.propTriple(iso_title, {"hasUncertainSpecies":spec}))

    if subspec:

        subspec = subspec.strip()
        triple.append(ctm.propTriple(iso_title, {"hasSubSpecies":subspec}))

    return "".join(triple)


####################################################################################################
# createCGFtriple
####################################################################################################
def createCGFtriple(data, iso_title):

    triple = []

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

    if litProps:
        triple.append(ltm.propTriple(title, litProps, True, True))

    if props:
        triple.append(ltm.propTriple(title, props))

    if triple:
        triple.append(ltm.indTriple(title, "CGF_test"))

    if triple:
        triple.append(tm.multiURI((iso_title, "hasLABTest", title), (ctm.uri, ctm.uri, ltm.uri)))

    if data["lab"]:
        triple.append(tm.multiURI((data["lab"], "hasName", "\"{}\"".format(data["lab"])),\
                      (ctm.uri, ctm.uri, ltm.uri)))

    return "".join(triple)


####################################################################################################
# createAnimalTriple
####################################################################################################
def createAnimalTriple(data, iso_title):

    triple = []

    animal, locale, type_ = data["animal"], data["locale"], data["type"]

    title = "{}_{}".format(animal, iso_title) if animal else ""

    name = "{} {}".format(locale, animal) if locale else animal

    props = popVals({"hasAnimalID":data["aID"],
                     "hasName":name,
                     "hasSex":data["sex"],
                     "hasAgeRank":data["age"]})

    if title:
        triple.append(ctm.propTriple(iso_title, {"hasSampleSource":title}))

    if animal:
        triple.append(ctm.indTriple(title, animal))

    if type_:
        triple.append(ctm.indTriple(title, type_))

    if props:
        triple.append(ctm.propTriple(title, props, True, True))

    if locale:
        triple.append(ctm.propTriple(iso_title, {"hasSampleLocale":locale}, True, True))

    return "".join(triple)
