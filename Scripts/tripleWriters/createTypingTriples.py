"""
 createTypingTriples
"""

import pandas as pd
from .. import cleanCSV as cn
from ..TripleMaker import TripleMaker as tm
from .campyTM import CAMPY as ctm
from .labTM import LAB as ltm

def createTypingTriples(df, row, isoTitle):

    triple = ""

    cols = list(df.columns.values) # Get all the column names

    genes = cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract gene names

    mlstGenes = genes[genes.index("Asp"):genes.index("Unc (atpA)")+1]

    cloComp = df["Clonal Complex"][row]

    st = df["ST"][row]

    mTitle = "{}_{}".format("mlst", isoTitle)

    if not pd.isnull(cloComp) and cn.isGoodVal(cloComp):

        # The values ST-403 and ST_403 are in the csv. We'll standardize it to ST_403
        cloComp = cloComp.replace("-", "_")
        triple += ltm.propTriple(mTitle, {"foundClonalComplex":cloComp}, True, True)


    # The value 'new' is in ST. We'll ignore it as well...for....now....
    if not pd.isnull(st) and cn.isGoodVal(st) and "new" not in st:

        st = int(float(st))
        triple += ltm.propTriple(mTitle, {"foundST":st}, True, True)


    if not pd.isnull(st):

        triple += ltm.indTriple(mTitle, "MLST_test")
        triple += tm.multiURI((isoTitle, "hasLabTest", mTitle), (ctm.uri, ctm.uri, ltm.uri))


    def allele_triple(g):

        triple = ""

        alIndex = df[g][row]

        if not pd.isnull(alIndex) and cn.isNumber(alIndex):

            alIndex = int(float(alIndex))

            alTitle = "{}_{}".format(cn.cleanGene(g), alIndex)

            triple = ltm.indTriple(alTitle, "Typing_allele") +\
                     ltm.propTriple(alTitle, {"isOfGene":cn.cleanGene(g)}) +\
                     ltm.propTriple(alTitle, {"hasAlleleIndex":alIndex}, True, True) +\
                     test_triple(g, alTitle)

        return triple


    def test_triple(g, alTitle):

        tClass = "{}_test".format(cn.cleanGene(g))

        tTitle = mTitle if g in mlstGenes else "{}_{}".format(tClass, isoTitle)

        triple = ltm.propTriple(tTitle, {"foundAllele":alTitle})

        if g not in mlstGenes:

            triple += ltm.indTriple(tTitle, tClass) +\
                      ltm.propTriple(tTitle, {"foundAllele":alTitle}) +\
                      tm.multiURI((isoTitle, "hasLabTest", tTitle), (ctm.uri, ctm.uri, ltm.uri))

        return triple



    triples = [allele_triple(g) for g in genes]

    triple += "".join(triples)

    return triple
