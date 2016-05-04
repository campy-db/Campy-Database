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
from .tripleWriters import *


####################################################################################################
# GLOBAL VARIABLES
####################################################################################################
CAMPY = "https://github.com/samuel-peers/CAMPYOntology/blob/master/CampyOntology.owl#"
LAB = "https://github.com/samuel-peers/CAMPYOntology/blob/master/LabTests.owl#"
LIT = "http://www.essepuntato.it/2010/06/LITeralreification/"
LITTM = TripleMaker.TripleMaker(LIT)

####################################################################################################
# Create an isolate instance. spec_str is the species defined by the user. It can be a mixed species
# , defined as "[spec1]+[spec2]", or it could be an uncertain (cf.) species, defined as "cf. [spec]"
# , a species and a subspecies, defined as "[main spec] [subspec_syn] [sub spec]"
# (eg "Jejuni spp. Doylei"), or it can just be the single species name. Note the word "Campy" or
# "Campylobacter" is allowed in the input and we remove it here.
####################################################################################################
def createDrugResistanceTriple(data, iso_title, spec_str):
    return drugResistanceWriter(data, iso_title, spec_str)

def createIsolateTriple(iso_title, spec_str):	
	return isolateTripleWriter(iso_title, spec_str)
 
####################################################################################################
# Create all the cgf triples using a property dictionary. Define a typing lab instance if the user
# has specified one.
####################################################################################################
def createCGFtriple(data, iso_title):
    return CGFTripleWriter(data, iso_title)


####################################################################################################
# Here we create the animal triples, again using a property dictionary.
####################################################################################################
def createAnimalTriple(data, iso_title):
    return animalTripleWriter(data, iso_title)

####################################################################################################
# Here we create the environment triples.
####################################################################################################
def createEnviroTriple(data, iso_title):
    return enviroTripleWriter(data, iso_title)

####################################################################################################
# Here we create the animal triples.
####################################################################################################
def createHumanTriple(data, iso_title):
    return humanTripleWriter(data, iso_title)

