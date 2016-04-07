"""
 createIDtriples
"""

import re
import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

def createIDtriples(df, row, isoTitle):

    idTriple = ""

    nmlid = df["NML ID#"][row]

    ldmsid = df["LDMS ID"][row]

    origName = df["Mostly Original Sample Names (might have project prefixes!)"][row] # lol

    sidA = df["Alternate Sample ID"][row]  # Sample id

    sidB = df["Alt. Sample ID"][row]

    sidC = df["C-EnterNet Number"][row]

    cidA = df["Sample Collection ID"][row] # Collection id

    cidB = ""

    comment = ""

    # Add the nmlID, ldmsID and original sample name
    if not pd.isnull(nmlid) and cn.isGoodVal(nmlid) and nmlid != "0":
        idTriple += ctm.propTriple(isoTitle, {"hasNMLid":nmlid}, True, True)

    if not pd.isnull(ldmsid) and cn.isGoodVal(ldmsid):
        idTriple += ctm.propTriple(isoTitle, {"hasLDMSid":ldmsid}, True, True)

    if not pd.isnull(origName) and cn.isGoodVal(origName):
        idTriple += ctm.propTriple(isoTitle, {"hasOriginalName":origName}, True, True)


    # Add the isolate's many sample ID's. Don't add the ID if it is the same as the isoTitle
    # or other the other IDs before it
    if not pd.isnull(sidA) and cn.isGoodVal(sidA):

        # Sometimes the Alternate ID is the strain name but with an - instead of _. This causes
        # problems with the reified literals. Note even if it is the same as the strain name as
        # some other strains may have the same sample id
        if cn.compare([isoTitle, sidA]):
            sidA = isoTitle


        sidA = int(float(sidA)) if cn.isNumber(sidA) else sidA # Some ids are ints

        idTriple += ctm.propTriple(isoTitle, {"hasSampleID":sidA}, True, True)


    if not pd.isnull(sidB) and cn.isGoodVal(sidB):

        # The values 'wrong label on tube..' is in this column. We put this in the
        # comments field instead
        if "wrong" in sidB:
            comment = sidB

        else:

            if cn.compare([isoTitle, sidB]):

                sidB = isoTitle # Sometimes it's the same as the isoTitle
                                # but with _ instead of -

            sidB = int(float(sidB)) if cn.isNumber(sidB) else sidB # Some ids are ints
            idTriple += ctm.propTriple(isoTitle, {"hasSampleID":sidB}, True, True)


    if not pd.isnull(sidC) and cn.isGoodVal(sidC):

        if cn.compare([isoTitle, sidC]): # Again this id is sometimes the same as
            sidC = isoTitle             # as isoTitle but with a different character

        sidC = int(float(sidC)) if cn.isNumber(sidC) else sidC # Some ids are ints
        idTriple += ctm.propTriple(isoTitle, {"hasSampleID":sidC}, True, True)


    # Alternate collection id is stored alongside original collection id.
    if not pd.isnull(cidA):

        cidA = int(float(cidA)) if cn.isNumber(cidA) else cidA

        if re.search("[aA]lt", str(cidA)) is not None:

            cids = cidA.split(" ")
            cidA = cids[0]
            cidA = cidA[:len(cidA)-1] # Get rid of the semi colon at the end
            cidB = cids[len(cids)-1] # Get the last item in the cids list

            cidB = int(float(cidB)) if cn.isNumber(cidB) else cidB # Some ids are ints
            idTriple += ctm.propTriple(isoTitle, {"hasCollectionID":cidB}, True, True)


        cidA = int(float(cidA)) if cn.isNumber(cidA) else cidA # Some ids are ints
        idTriple += ctm.propTriple(isoTitle, {"hasCollectionID": cidA}, True, True)


    if comment:
        idTriple += ctm.propTriple(isoTitle, {"hasComment":sidB}, True)

    return idTriple

