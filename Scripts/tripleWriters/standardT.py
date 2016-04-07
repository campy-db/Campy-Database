"""
 standardT
"""

from .campyTM import CAMPY as ctm

def addStandardTrips(isoTitle, prop, title, tClass):

    triple = ctm.indTriple(str(title), tClass)
    triple += ctm.propTriple(isoTitle, {prop:title})
    triple += ctm.propTriple(str(title), {"hasName":title}, True)

    return triple
