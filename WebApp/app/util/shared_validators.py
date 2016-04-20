"""
 shared_validators

 Validators to be called from flask forms and also whatever ends up being used for batch upload

"""

import re
from .valid_values import SPECIES, ANIMALS, SAMPLE_TYPES, SAMPLE_PROPS, ENVIROS, ENVIRO_PROPS,\
                          PEOPLE, CLINICAL_TYPES
from ..sparql import queries as q

####################################################################################################
#
# Returns true if the string v contains valid mixed campy species, valid species and subspecies,
# valid cf. species, or just a single valid species, where valid means the species actually
# exsists according to the list of campy species on ncbi website. See SPECIES in util/valid_values.
# The species can be a mixed species, defined as "[spec1]+[spec2]", or it could be an uncertain
# (cf.) species, defined as "cf. [spec]", a species and a subspecies, defined as "[main spec]
# [subspec_syn] [sub spec]" (eg "Jejuni spp. Doylei"), or it can just be the single species name.
# Note the word "Campy" or "Campylobacter" is allowed in the input and we remove it here.
#
####################################################################################################
def validSpecies(v):

    good_spec, good_subspec, empty_sub = True, True, False

    # "Subspecies" synonyms
    subspec_syns = ["subspecies", "subspec.", "subspec", "spp.", "subsp.", "subsp"]

	# The user can input campy or campylobacter if they want, the species names in the
	# species dictionary doens't have it though, it's just extraneous is all
    v = re.sub(r"[Cc]ampy(lobacter)?", "", v).lower().strip()

    # Returns the largest string in subspec_syns that is in v. Note we could just sort the list
    # manually, but if we decide to add synonyms to subspec_syns in the future,
    # this would be error prone
    subspec_delim = ""
    for ss in sorted(subspec_syns, key=len, reverse=True):
        if v.find(ss) != -1:
            subspec_delim = ss
            break

    if subspec_delim:
        # make sure they've actually specified a subspecies
        empty_sub = True if v.split(subspec_delim)[1] == "" else False

        specs = [s.strip() for s in v.split(subspec_delim)]

        spec, subspec = specs[0], specs[1]

        good_spec = True if spec in SPECIES.keys() else False

        if good_spec:
            good_subspec = True if subspec in SPECIES[spec] else False

        # Note there are no uncertain or mixed species allowed if a subspecies
        # is specified

    else:
        spec, subspec = v, ""

        if spec.find("cf.") != -1:
            # They can specify ONE uncertain species using "cf."
            spec = v.split("cf.")[1].strip()

        elif spec.find("+") != -1:
            # They can specify mixed species using the plus sign
            spec = [s.strip() for s in spec.split("+")]

        spec = [spec] if not isinstance(spec, list) else spec
        good_spec = all(True if s in SPECIES.keys() else False for s in spec)


    message = "You forgot to add a subspecies" if empty_sub else ""

    message = "Invalid species" if not good_spec else message

    message = "Invalid subspecies" if not good_subspec else message

    valid = good_spec and good_subspec and not empty_sub

    return valid, message


####################################################################################################
# Returns True if the fingerprint contains only 1s and 0s.
####################################################################################################
def validBinaryFP(v):

    valid = True
    message = ""

    for char in v:
        if char != "0" or char != "1":
            valid = False
            message = "Fingerprint must contain only 1s and 0s"
            break

    return valid, message

####################################################################################################
#
# Only handles animal sources right now. Checks if one of the strings in val is in the list ANIMALS
# (created in valid_values.py). If there is more than one string in val, check if it is in the list
# SAMPLE_TYPES. This means that valid animal sources are of the form "chicken breast".
#
# TO DO
# - Handle environment sources (EG dairy lagoon, water, drinking water, sewage, treated sewage)
# - Handle human sources (EG patient blood, patient stool, human blood, human stool)
#
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
#
# Here we check if a value is "general", ie in the list gen_list (we create general value lists in
# valid_values.py). If the value val is general, return a warning message and set valid as False.
#
# NOTE that valid is only set to False if the value is in the general list and does not equal
# last_val. EG if gen_list = ["Avian", "Ruminant"] and val = "Avian", and last_val != "Avian" (if
# you look at validators.py and views.py, last_val is set to None the first time and gets updated
# accordingly (this will be done for the batch uploader as well)), return valid=False. If the user
# then changes the value to "Ruminant", last_val should equal "Avian" and we return valid=False
# again. Say they DON'T change "Ruminant" now and last_val="Ruminant", now we return valid=True
# because a general value is not an incorrect value, we just want the user to know that there are
# better more specific values they should consider, and that's what we return in the message, a list
# of more specific alternatives to val. We also set it to False if it's general and o_err is True,
# because if there are other errors, we should still show the warning message.
#
####################################################################################################
def genValue(val, gen_list, o_err, last_val):

    valid = True
    message = ""
    gen_val = ""

    vals = [v.lower().replace("_", " ") for v in val.split(" ")]

    has_gen = False

    for v in vals:

        if v in gen_list:

            gen_val = v
            has_gen = True

    if has_gen:

        sub_classes = [s.lower() for s in q.getSubClasses(gen_val)]

        sub_class_list = ", ".join(sub_classes)

        if o_err or gen_val != last_val:

            #last_val = gen_val

            valid = False
            message = "Consider these values instead of {}: {}".format(gen_val, sub_class_list)

    return valid, message, gen_val

####################################################################################################
# Raise an error if the source value is not a valid postal code format.
####################################################################################################
def validPostalCode(val):

    valid = True
    message = ""

    if re.search(r"[A-Za-z][0-9][A-Za-z][ ][0-9][A-Za-z][0-9]", val) is None:
        valid = False
        message = "Invalid postal code format."

    return valid, message
