"""
createSerotypeTriples
"""
from .dictionary.antigenDictionary import getAntigens
from Scripts.tripleWriters.labTM import LAB as ltm


def createAntigenTriple():
    triple = ""
    antigens = getAntigens()
    for a in antigens:
        triple += ltm.indTriple(a, "Antigen")
    return triple
