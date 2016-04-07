"""
 createIsolationTriples
"""

import re
import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

def createIsolationTriples(df, row, isoTitle):

    isoTriple = ""

    media = df["Media"][row]

    # Don't include colony morph for now.
    # colonyMorph = df["colony morph"][row]
    dilution = df["Dilution"][row]

    glycStock = df["No glycerol stock"][row]

    hipO = df["HipO"][row]

    treatment = df["Treatment"][row]

    technique = df["technique"][row]

    # For whatever reason source specific 2 has media info in
    # it. Just one though: K and Cefex
    sourceSpec = df["Source_Specific_2"][row]

    # For whatever reason there's just a dash as one of the media values. We'll ignore it for now.
    if not pd.isnull(media) and media != "-" and "#N/A" not in media:
        # We'll standardize all media to be uppercase and have no spaces, because
        # there are the values '10% B' and '10%B'.
        media = media.upper().replace(" ", "")
        
        # Grab k and cefex from source specific 2
        if not pd.isnull(sourceSpec) and re.search("[Cc]efex", sourceSpec) is not None:
            media = "K and CEFEX" # SUBJECT TO CHANGE

        isoTriple += ctm.propTriple(isoTitle, {"grownOn":media}, True, True)

    if not pd.isnull(dilution):

        # Again there are some values that have spaces and others that don't.
        # We'll get rid of the spaces. Is this a number value??
        dilution = dilution.replace(" ", "")
        isoTriple += ctm.propTriple(isoTitle, {"hasDilution":dilution}, True, True)

    # The values in the csv are 1 or 0. 1 meaning it is true there is no glyc stock. This
    # is confusing. So in the ontology we have 'hasGlycStock' and we interpret 1 in the csv as false
    if not pd.isnull(glycStock) and cn.isGoodVal(glycStock):

        glycStock = int(float(glycStock)) # Sometimes ints are converted to floats in the csv

        glycStock = False if glycStock == 1 else True

        isoTriple += ctm.propTriple(isoTitle, {"hasGlycStock":glycStock}, True, True)

    if not pd.isnull(hipO) and cn.isGoodVal(hipO):
        hipO = int(float(hipO)) if not isinstance(hipO, str) else hipO

        if hipO == 1:
            hipO = True

        else:
            hipO = "unknown" if hipO == "?" else False

        isoTriple += ctm.propTriple(isoTitle, {"hasHipO":hipO}, True, True)

    # For whatever reason the value 'Treatment' is in the column 'Treatment'. We'll ignore it
    # for now.
    if not pd.isnull(treatment) and "Treatment" not in treatment and cn.isGoodVal(treatment):

        isoTriple += ctm.propTriple(isoTitle, {"hasTreatment":treatment}, True, True)

    # The - also showed up in technique. We'll ignore it.
    if not pd.isnull(technique) and technique != "-":
        # Values enrichment, ENRICH and enrich are found in this col. We'll standardize it to enrich
        if "enrich" in technique.lower():
            technique = "enrich"

        # Some values have spaces and others don't. eg '24AE' and '24 AE'. We'll get rid of
        # spaces.
        technique = technique.replace(" ", "")

        isoTriple += ctm.propTriple(isoTitle, {"hasTechnique":technique}, True, True)
   
    return isoTriple
