from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.resistanceDictionary import getBreakpoints
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm
from ..util import cleanInt, remPrefix
import re

def createRefTriple(data, isoTitle):

    rTriple = ""
    # source = df["Source_Specific_2"][row]

    # animalID = df["Animal ID"][row]

    # ref = df["Dataset ID_1"][row]

    if data["Reference Strain"] == "yes":
        rTriple = ctm.propTriple(isoTitle, {"isReferenceStrain":True}, True, True)

        if data["Reference Source"]:

            if re.search("[Hh]uman", data["Reference Source"]) is not None:

                # Use the human naming convention
                title = "{}_{}".format("patient", isoTitle)
                sClass = "Patient"

            else: # It's an animal source

                source = remPrefix(data["Reference Source", 2])
                sClass = source

                if data["Animal ID"]:

                    # Use animal ID if available
                    title = cleanInt(data["Animal ID"])

                else:

                    # Else use animal naming convention
                    title = "{}_{}".format(source, isoTitle)




            rTriple += ctm.indTriple(title, sClass)
            rTriple += ctm.propTriple(isoTitle, {"hasSampleSource":title})

    return rTriple

