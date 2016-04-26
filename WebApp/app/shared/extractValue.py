"""
 getSpecies

 Used in clean_triple_writers.py and for the isolate names page.
 Returns a species, subspecies, and an uncertain (cf.) species (if present)

"""

import re
from .valid_values import ANIMALS, ENVIROS, PEOPLE, SAMPLE_TYPES, SAMPLE_PROPS, ENVIRO_PROPS,\
                          CLINICAL_TYPES

####################################################################################################
# Given a string s and a list of values, return the sub_string in s that matches one of the values
# in poss_vals. We standardize the substrings in s first.
####################################################################################################
def getValueIn(s, poss_vals):

    vals = [v.lower().replace("_", " ") for v in s.split(" ")]

    result = ""

    for v in vals:
        result = v if v in poss_vals else result

    return result

####################################################################################################
# Interface functions for retreiving values from lists of valid values we've defined.
####################################################################################################
def getAnimal(s):
    return getValueIn(s, ANIMALS)

def getEnviro(s):
    return getValueIn(s, ENVIROS)

def getPerson(s):
    return getValueIn(s, PEOPLE)

def getType(s):
    return getValueIn(s, SAMPLE_TYPES)

def getTypeProp(s):
    return getValueIn(s, SAMPLE_PROPS)

def getEnviroProp(s):
    return getValueIn(s, ENVIRO_PROPS)

def getClinicalType(s):
    return getValueIn(s, CLINICAL_TYPES)


####################################################################################################
# Given a string spec_str, extract a campy species, subspecies, and uncertain species.
####################################################################################################
def getSpecies(spec_str):

    spec, subspec, uncertain_spec = None, None, None

    subspec_syns = ["subspecies", "subspec.", "subspec", "spp.", "subsp.", "subsp"]

    # Returns the largest string in subspec_syns that is in v. Note we could just sort the list
    # manually, but if we decide to add synonyms to subspec_syns in the future, this approach
    # would be error prone
    subspec_delim = ""
    for ss in sorted(subspec_syns, key=len, reverse=True):
        if spec_str.find(ss) != -1:
            subspec_delim = ss
            break

    # Remove any instances of "Campylobacter", "campylobacter", "Campy", or "campy"
    spec_str = re.sub(r"[Cc]ampy(lobacter)?", "", spec_str).strip().lower()

    # Check if it's an uncertain species
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

    # If it is an uncertain species
    if not is_cf_spec:

        # spec could be a list already (if it's a mixed species). Make it a list if its not
        spec = [spec] if not isinstance(spec, list) else spec

        # For all the species in spec (it could just be one), remove trailing & leading spaces
        spec = [s.strip() for s in spec]

    else:
        spec = None
        uncertain_spec = spec

    if subspec:
        subspec = subspec.strip()

    return spec, subspec, uncertain_spec
