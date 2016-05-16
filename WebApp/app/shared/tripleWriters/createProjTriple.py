# -*- coding: latin-1 -*-
from Scripts.tripleWriters.labTM import LAB as ltm
from .dictionary.resistanceDictionary import getBreakpoints
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.TripleMaker import TripleMaker as tm
from ..util import cleanInt, isNumber

import re

def createProjTriple(data, isoTitle):

    resultTriple = ""

    projTriple = ""

    isoTriple = ""

    proj = data["Project Name"]

    subproj = data["Subproject Name"]

    # Whether an isolate is a reference strain or not is stored in the 'Dataset ID_1' column
    # (proj variable), and usually in subsequent columns, but not always.


    if proj:

        projTriple += ctm.indTriple(proj, "Project") +\
                      ctm.propTriple(proj, {"hasName":proj}, True)

        isoTriple += ctm.propTriple(isoTitle, {"partOfProject":proj})

        if subproj:

            for c in " _":

                # Split by '-',' ', or '_' if it's preceded by at least 2 characters,
                # we don't want to remove 'C' when the project = C-Enternet for example.
                toRem = re.split("(?<= ..)[- _]", proj)

                for r in toRem:

                    subproj = subproj.replace(r, "")
                    subproj = subproj.strip()

                # Remove all the '-',' ', and '_' if they are NOT preceded by a character
                subproj = re.sub("(?<!.)[- _]", "", subproj)

                # Handle the french characters
                subproj = re.sub("H...pital","Hôpital",subproj)
                subproj = re.sub("^...t... ","Été ",subproj)

          
            # Some of the subprojects are years
            subproj = cleanInt(subproj) if isNumber(subproj) else subproj 

            projTriple += ctm.indTriple(subproj, "Sub_project")
            projTriple += ctm.propTriple(subproj, {"hasName":subproj}, True)
            projTriple += ctm.propTriple(proj, {"hasSubproject":subproj})

            isoTriple += ctm.propTriple(isoTitle, {"partOfSubProject":subproj})

    resultTriple += isoTriple + projTriple

    return resultTriple