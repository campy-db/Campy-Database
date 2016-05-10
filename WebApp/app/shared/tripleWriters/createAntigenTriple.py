"""
createSerotypeTriples
"""
from .dictionary.antigenDictionary import getAntigens
from Scripts.tripleWriters.labTM import LAB as ltm


def createAntigenTriple(antigen):
    triple = ltm.indTriple(antigen, "Antigen")
    return triple
