from Scripts.tripleWriters.campyTM import CAMPY as ctm
from WebApp.app.shared.extractValue import getSpecies
from .tripleWriters import *

####################################################################################################
# Create an isolate instance. spec_str is the species defined by the user. It can be a mixed species
# , defined as "[spec1]+[spec2]", or it could be an uncertain (cf.) species, defined as "cf. [spec]"
# , a species and a subspecies, defined as "[main spec] [subspec_syn] [sub spec]"
# (eg "Jejuni spp. Doylei"), or it can just be the single species name. Note the word "Campy" or
# "Campylobacter" is allowed in the input and we remove it here.
####################################################################################################
def isolateTripleWriter(iso_title, spec_str):
	
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