"""
 createLabLocTriples
"""

import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

def createLabLocTriples(df, row, isoTitle):

    triple = ""
    isoLoc = ""

    isoLocA = df["Isolate Location 1"][row]
    isoLocB = df["Isolate Location 2"][row]

    # There are two columns that contain the lab location of an isolate, but when column has a value
    # the other does not.

    if not pd.isnull(isoLocA) and cn.isGoodVal(isoLocA):
        isoLoc = isoLocA

    if not pd.isnull(isoLocB) and cn.isGoodVal(isoLocB):
        isoLoc = isoLocB

    if isoLoc:
        triple += ctm.indTriple(isoLoc, "Isolate_location")
        triple += ctm.propTriple(isoLoc, {"hasName":isoLoc}, True)
        triple += ctm.propTriple(isoTitle, {"hasIsolateLocation":isoLoc})

    return triple
