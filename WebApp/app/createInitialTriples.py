#!/usr/bin/env python
from .shared.tripleWriters.createAntigenTriple import createAntigenTriple
from .shared.tripleWriters.createGeneTriple import createGeneTriple
from Scripts.endpoint import update as update
from .shared.tripleWriters.dictionary.antigenDictionary import getAntigens
from .shared.tripleWriters.dictionary.geneDictionary import getGenes
def createInitialTriples():
    triple = ""
    antigens = getAntigens()
    for a in antigens:
        triple += createAntigenTriple(a)

    aGenes, cgfGenes = getGenes()

    for g in aGenes:
        triple += createGeneTriple(g, "allele")
    for g in cgfGenes:
        triple += createGeneTriple(g, "cgf")
    return triple

def writeToOnt(t):
    print ("<<<<<<<<<<<<<<<<<<<<ATTEMPT>")
    with open("/home/student/CampyCopy/CampyDatabase/Ontologies/CampyOntology.owl", "a") as w:
        w.write(t)

def writeToBG(t):
    print update("insert data{"+t+"}")
    #print ("[TEST]: " + t)

def main():
    print("[INFO] Required population of the database has started. Please run this script only once.")
