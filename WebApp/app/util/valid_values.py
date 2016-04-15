"""
 valid_values.py

 Called by the validators. Used to see which values we consider valid.

"""

import urllib
import re

from ..sparql import queries as q

####################################################################################################
# get_species
#
# Fetches campylobacter species and subspecies from the ncbi website. Creates a dictionary. Adds
# a species as a key and then its value is a list of subspecies.
####################################################################################################
def get_species():

    species = {}

    u = urllib.urlopen("https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=194")
    ustr = u.read()
    content = ustr[ustr.find("content"):]

    # Get all the values between html tags
    content = re.split("<[^><]+>", content)

    for c in content:

        # Only grab the strings that start with "Campy" and have at least 2 words in them
        # (come values are just "Campylobacter" on the website)
        if re.search("^Campy", c) is not None and len(c.split(" ")) >= 2:

            # We take only definitive species, nothing novel
            if c.find(" sp.") == -1:

                # species and subspecies are delimited by "subsp.". Get rid of the word
                # "Campylobacter". We could keep it, but it's extraneous
                specs = [s.replace("Campylobacter ", "").strip().lower() for s in c.split("subsp.")]
                spec = specs[0]
                sub_spec = specs[1] if len(specs) == 2 else ""

                if sub_spec:

                    # A lot of the subspecies are suffixed with reference strain names. We just want
                    # the subspecies name
                    if sub_spec.split(" ")[0] not in species[spec]:
                        species[spec].append(sub_spec)

                else:

                    # We don't want uncertain species
                    uncertain = True if spec.find("cf.") != -1 else False
                    # We don't want campy-like species
                    likeness = True if spec.find("-like") != -1 else False

                    # Species are suffixed with reference strain names. We just want the species
                    # name
                    if spec.split(" ")[0] not in species.keys() and not uncertain and not likeness:
                        species[spec] = []

    return species

####################################################################################################
# A list of values that are fetched from the triples stored on blazegraph. We only consider values
# to be valid if they are already in the database. eg. Only animals that we have already defined
# can placed in the database.
####################################################################################################

ANIMALS = [a.lower() for a in q.getSubClasses("Animal")]

# General animals. eg. cow, avian, duck, companion
GEN_ANIMALS = [a.lower() for a in q.getHighestClasses("Animal")]

# Sample types. eg. swab, droppings, cut, breast
SAMPLE_TYPES = [st.lower() for st in q.getSubClasses("Animal_sample")]

# General sample types. eg. food, faecal
GEN_SAMPLE_TYPES = [st.lower() for st in q.getHighestClasses("Animal_sample")]

#SPECIES = get_species()
SPECIES = {"jejuni":["jejuni", "poylpei"]}