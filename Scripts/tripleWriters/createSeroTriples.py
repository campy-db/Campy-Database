"""
 createSeroTriples
"""

import pandas as pd
from .. import cleanCSV as cn
from ..TripleMaker import TripleMaker as tm
from .campyTM import CAMPY as ctm
from .labTM import LAB as ltm

def createSeroTriples(df, row, isoTitle):

    triple = ""
    sero = df["Serotype"][row]

    if not pd.isnull(sero) and cn.isGoodVal(sero):

        sTitle = "sero_{}".format(isoTitle)

        triple += ltm.indTriple(sTitle, "Serotype_test")

        triple += ltm.propTriple(sTitle, {"foundSerotype":str(sero)}, True, True)

        triple += tm.multiURI((isoTitle, "hasLabTest", sTitle), (ctm.uri, ctm.uri, ltm.uri))

    return triple
