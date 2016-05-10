"""
createSerotypeTriples
"""
from .dictionary.serotypeDictionary import getSerotypes
from Scripts.tripleWriters.labTM import LAB as ltm

def createSerotypeTriples():
    triple = ""
    drugs = getSerotypes()
    for d in drugs:
        triple + ltm.indTriple(d, "Serotype")
    return triple
