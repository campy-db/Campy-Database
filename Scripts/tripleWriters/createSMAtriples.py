"""
 createSMAtriples
"""

import pandas as pd
from .. import cleanCSV as cn
from ..TripleMaker import TripleMaker as tm
from .campyTM import CAMPY as ctm
from .labTM import LAB as ltm

def createSMAtriples(df, row, isoTitle):

    sTriple = ""

    pulsovar = df["Pfge Sma I  / Pulsovar"][row]

    if not pd.isnull(pulsovar) and cn.isGoodVal(pulsovar):

        sTitle = "sma1_"+isoTitle

        sTriple += ltm.indTriple(sTitle, "SMA1_test")

        sTriple += ltm.propTriple(sTitle, {"foundPulsovar":str(pulsovar)}, True, True)

        sTriple += tm.multiURI((isoTitle, "hasLabTest", sTitle), (ctm.uri, ctm.uri, ltm.uri))

    return sTriple
