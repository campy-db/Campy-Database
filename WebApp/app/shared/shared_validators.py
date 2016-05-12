"""
 shared_validators

 Validators to be called from flask forms and also whatever ends up being used for batch upload

"""

import re
from .valid_values import SPECIES, ANIMALS, SAMPLE_TYPES, SAMPLE_PROPS, ENVIROS, ENVIRO_PROPS,\
                          PEOPLE, CLINICAL_TYPES, GEN_ANIMALS, GEN_SAMPLE_TYPES, ANTIGENS
from ..sparql import queries as q

from .tripleWriters.dictionary.resistanceDictionary import getBreakpoints as getResistanceBP
from .tripleWriters.dictionary.susceptibleDictionary import getBreakpoints as getSusceptibleBP

####################################################################################################
# Returns true if the string v contains valid mixed campy species, valid species and subspecies,
# valid cf. species, or just a single valid species, where valid means the species actually
# exsists according to the list of campy species on ncbi website. See SPECIES in util/valid_values.
# The species can be a mixed species, defined as "[spec1]+[spec2]", or it could be an uncertain
# (cf.) species, defined as "cf. [spec]", a species and a subspecies, defined as "[main spec]
# [subspec_syn] [sub spec]" (eg "Jejuni spp. Doylei"), or it can just be the single species name.
# Note the word "Campy" or "Campylobacter" is allowed in the input and we remove it here.
####################################################################################################
def validSpecies(spec, subspec, un_spec):

    good_spec, good_subspec, good_un_spec = True, True, True

    if spec:
        good_spec = all(True if s in SPECIES.keys() else False for s in spec)

    if subspec and good_spec:
        if len(spec) == 1:
            spec = "".join(spec)
            good_subspec = True if subspec in SPECIES[spec] else False

    if un_spec:
        good_un_spec = True if un_spec in SPECIES.keys() else False

    message = ""

    message = "Invalid species" if (not good_spec or not good_un_spec) else message

    message = "Invalid subspecies" if not good_subspec else message

    valid = good_spec and good_subspec and good_un_spec

    return valid, message

####################################################################################################
# Returns True if the fingerprint contains only 1s and 0s.
####################################################################################################
def validBinaryFP(v):

    valid = True
    message = ""

    for char in v:
        if char != "0" and char != "1":
            valid = False
            message = "Fingerprint must contain only 1s and 0s"
            break

    return valid, message

####################################################################################################
# Only handles animal sources right now. Checks if one of the strings in val is in the list ANIMALS
# (created in valid_values.py). If there is more than one string in val, check if it is in the list
# SAMPLE_TYPES. This means that valid animal sources are of the form "chicken breast".
####################################################################################################
def validSource(val):

    has_sample, has_sample_prop, has_enviro_prop, has_human_type = None, None, None, None
    valid = True
    message = ""

    vals = [v.lower().replace("_", " ") for v in val.split(" ")]

    has_animal = any([True if v in ANIMALS else False for v in vals])

    has_enviro = any([True if v in ENVIROS else False for v in vals])

    has_human = any([True if v in PEOPLE else False for v in vals])

    # True if any of the values in vals is a sample type. False otherwise.
    if len(vals) > 1:
        has_human_type = any([True if v in CLINICAL_TYPES else False for v in vals])
        has_enviro_prop = any([True if v in ENVIRO_PROPS else False for v in vals])
        has_sample = any([True if v in SAMPLE_TYPES else False for v in vals])

    # If there are more than 2 values, then one must be an animal, the other a sample type, and the
    # the last a sample type property (rinse, with skin, skinless, seasoned)
    if len(vals) > 2:
        has_sample_prop = any([True if v in SAMPLE_PROPS else False for v in vals])

    if not any([has_animal, has_enviro, has_human]):

        message = "Invalid source"
        valid = False

    if has_animal:

        if has_sample is False:

            message = "Invalid sample type"
            valid = False

        if has_sample_prop is False:

            message = "Invalid sample type property"
            valid = False

    if has_enviro:

        if has_enviro_prop is False:

            message = "Invalid environment property"
            valid = False

    if has_human:

        if has_human_type is False:

            message = "Invalid human sample type"
            valid = False

    return valid, message

####################################################################################################
# Interface functions for genValue
####################################################################################################
def checkGenAnimal(val, last_val, o_err):
    return genValue(val, GEN_ANIMALS, last_val, o_err)

def checkGenType(val, last_val, o_err):
    return genValue(val, GEN_SAMPLE_TYPES, last_val, o_err)

####################################################################################################
# Here we check if a value is "general", ie in the list gen_list (we create general value lists in
# valid_values.py). If the value val is general, return a warning message and set valid as False.
#
# NOTE that valid is only set to False if the value is in the general list and does not equal
# last_val. EG if gen_list = ["Avian", "Ruminant"] and val = "Avian", and last_val != "Avian" (if
# you look at validators.py and views.py, last_val is set to None the first time and gets updated
# accordingly (this will be done for the batch uploader as well)), return valid=False. If the user
# then changes the value to "Ruminant", last_val should equal "Avian" and we return valid=False
# again.
#
# Say they DON'T change "Ruminant" now and last_val="Ruminant", now we return valid=True
# because a general value is not an incorrect value, we just want the user to know that there are
# better more specific values they should consider, and that's what we return in the message, a list
# of more specific alternatives to val.
#
# We also set it to False if it's general and o_err is True, ie there are other errors in the form,
# because if there are other errors, we should still show the warning message.
####################################################################################################
def genValue(val, gen_list, last_val, o_err):


    valid = True
    message = ""

    has_gen = False

    if val in gen_list:
        has_gen = True

    if has_gen:

        sub_classes = [s.lower() for s in q.getSubClasses(val)]

        sub_class_list = ", ".join(sub_classes)

        if o_err or val != last_val:

            #last_val = gen_val

            valid = False
            message = "Consider these values instead of {}: {}".format(val, sub_class_list)

    return valid, message

####################################################################################################
# Raise an error if the source value is not a valid postal code format.
####################################################################################################
def validPostalCode(val):

    valid = True
    message = ""

    if re.search(r"[A-Za-z][0-9][A-Za-z][ ][0-9][A-Za-z][0-9]", val) is None:
        valid = False
        message = "Invalid postal code."

    return valid, message

####################################################################################################
# Comments here someday
####################################################################################################
def validMIC(value, drug, species=None):
    message = ""
    valid = True
    isFloat = True
    micValue = value.lstrip(">")
    if species == None:
        message += ""
    try:
        float(micValue)
    except ValueError:
        isFloat = False
        message += "Invalid MIC value for field " + drug + "."
        valid = False
    if isFloat:
        if float(micValue) <= 0:
            message += "MIC values must be greater than 0."
            valid = False
        if species:
            resDict = getResistanceBP(species)
            susDict = getSusceptibleBP(species)
            if float(micValue) > susDict[drug] and float(micValue) < resDict[drug]:
                message += "MIC value for " + drug + " must greater than the resistant breakpoint\
                 or less than the susceptibile breakpoint specified by CIPARS/NARMS."
                valid = False
            if ">" in str(value[0]) and float(micValue) < susDict[drug]:
                message +=  "MIC value for " + drug + " must not have contain a > sign if it falls\
                 below the suceptible breakpoint specified by CIPARS/NARMS"
                valid = False

    return valid, message

def validAntigen(antigen):
    message = ""
    valid = True

    if not antigen in ANTIGENS:
        valid = False
        message = "Antigen is not among list of allowed antigens. Currently allowed antigens are " + str(ANTIGENS) + "."
    return valid, message

def validSero(serotype):
    def isInt(num):
        number = True
        try:
            int(num)
        except ValueError:
            number = False
        return number
    message = ""
    valid = True
    serotype = serotype.split(",")
    for s in serotype:
        if not isInt(s):
            valid = False
            message = "Serotypes must be entered as integers seperated by a comma (no spaces)."
            break
    return valid, message
    
def validDate(value, dateType):
    message = ""
    valid = True
    try:
        int(value)
    except ValueError:
        message += dateType + " must be an integer (whole number) value."
        valid = False

    return valid, message