"""
 shared_validators

 Validators to be called from flask forms and also whatever ends up being used for batch upload

"""

import re
from .valid_values import SPECIES

####################################################################################################
# valid_species
#
# Returns true if the string v contains valid mixed campy species, valid species and subspecies,
# valid cf. species, or just a single valid species, where valid means the species actually
# exsists according to the list of campy species on ncbi website. See SPECIES in util/valid_values.
####################################################################################################
def valid_species(v):

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
