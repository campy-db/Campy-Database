"""
 clean_triple_writers.py

 Called from form_to_triple. Here we recieve a dictionary of data and create triples.
 So the dictionary that is passed in from form_to_triple may have some empty values, so we create
 a "property dictionary" (a dictionary with the property name as the key and the value from the
 data dictionary as the dictionary value) and pop all the keys with empty values. Then create the
 triples using the property dictionary. We don't do this createIsolateTriples because there's only
 one property value passed in.

"""

import re
from Scripts.TripleMaker import TripleMaker as tm
from Scripts import TripleMaker
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.tripleWriters.labTM import LAB as ltm
from .extractValue import getSpecies

####################################################################################################
# GLOBAL VARIABLES
####################################################################################################
CAMPY = "https://github.com/samuel-peers/CAMPYOntology/blob/master/CampyOntology.owl#"
LAB = "https://github.com/samuel-peers/CAMPYOntology/blob/master/LabTests.owl#"
LIT = "http://www.essepuntato.it/2010/06/LITeralreification/"
LITTM = TripleMaker.TripleMaker(LIT)

####################################################################################################
# FUNCTIONS
####################################################################################################

####################################################################################################
# Pop all the empty values from a dictionary
####################################################################################################
def popVals(my_dict):
    return {x:y for x, y in my_dict.iteritems() if y != ""}

####################################################################################################
# Create an isolate instance. spec_str is the species defined by the user. It can be a mixed species
# , defined as "[spec1]+[spec2]", or it could be an uncertain (cf.) species, defined as "cf. [spec]"
# , a species and a subspecies, defined as "[main spec] [subspec_syn] [sub spec]"
# (eg "Jejuni spp. Doylei"), or it can just be the single species name. Note the word "Campy" or
# "Campylobacter" is allowed in the input and we remove it here.
####################################################################################################
def createIsolateTriple(iso_title, spec_str):

    triple = []

    if spec_str:
        spec, subspec, un_spec = getSpecies(spec_str)

        for s in spec:
            triple.append(ctm.propTriple(iso_title, {"hasSpecies":s}))

        if subspec:
            triple.append(ctm.propTriple(iso_title, {"hasSubSpecies":subspec}))

        if un_spec:
            triple.append(ctm.propTriple(iso_title, {"hasUncertainSpecies":un_spec}))

    triple.append(ctm.indTriple(iso_title, "Isolate")+\
                  ctm.propTriple(iso_title, {"hasIsolateName":iso_title}, True, True))

    return "".join(triple)


####################################################################################################
# Create all the cgf triples using a property dictionary. Define a typing lab instance if the user
# has specified one.
####################################################################################################
def createCGFtriple(data, iso_title):

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


####################################################################################################
# Here we create the animal triples, again using a property dictionary.
####################################################################################################
def createAnimalTriple(data, iso_title):

    triple = []

    animal, locale, type_, type_prop = data["animal"],\
                                       data["locale"],\
                                       data["type"],\
                                       data["type_prop"]

    a_title = "{}_{}".format(animal, iso_title) if animal else ""

    name = "{} {}".format(locale, animal) if locale else animal

    rlit_props = popVals({"hasAnimalID":data["aID"],
                          "hasSex":data["sex"],
                          "hasAgeRank":data["age"]})

    if animal:
        triple.append(ctm.indTriple(a_title, animal))
        triple.append(ctm.propTriple(a_title, {"hasName":name}, True))
        triple.append(ctm.propTriple(iso_title, {"hasAnimalSource":a_title}))

    if rlit_props:
        triple.append(ctm.propTriple(a_title, rlit_props, True, True))

    if locale:
        triple.append(ctm.propTriple(iso_title, {"hasSampleLocale":locale}, True, True))

    if type_:

        # Sample type naming convention is "[locale_]type[_prop]"
        s_title = "{} {}".format(locale, type_) if locale else type_
        s_title = "{} {}".format(s_title, type_prop) if type_prop else s_title

        sample_triple = ctm.indTriple(s_title, type_) +\
                        ctm.propTriple(s_title, {"hasName":s_title}, True)

        triple.append(sample_triple)
        triple.append(ctm.propTriple(iso_title, {"hasSampleType":s_title}))

    return "".join(triple)

####################################################################################################
# Here we create the environment triples.
####################################################################################################
def createEnviroTriple(data, iso_title):

    triple = []

    e_prop = data["enviro_prop"]

    enviro = data["enviro"]

    e_title = "{} {}".format(e_prop, enviro) if e_prop else enviro

    triple.append(ctm.indTriple(e_title, enviro))
    triple.append(ctm.propTriple(e_title, {"hasName":e_title}, True))
    triple.append(ctm.propTriple(iso_title, {"hasEnviroSource":e_title}))

    return "".join(triple)

####################################################################################################
# Here we create the animal triples.
####################################################################################################
def createHumanTriple(data, iso_title):

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

