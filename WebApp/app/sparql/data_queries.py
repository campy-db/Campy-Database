"""
 data_queries.py

 Specific sparql queries

"""

import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import CAMPY as CTM
from Scripts.tripleWriters.labTM import LAB as LTM
from .shared import *
from ..shared.extractValue import getSpecies

####################################################################################################
# Returns a list of isolate names.
####################################################################################################
def getIsoNames(species=None):

    has_species = ""

    if species:
        spec, subspec, un_spec = getSpecies(species)
        if spec:
            for s in spec:
                has_species += "?i :{} :{} .".format("hasSpecies", s)
        if subspec:
            has_species += "?i :{} :{} .".format("hasSubspecies", subspec)
        if un_spec:
            has_species += "?i :{} :{} .".format("hasUncertainSpecies", un_spec)


    q = """
        {cprefix}
        {lprefix}
        select ?v 
        where {{
            ?i :{hasIsoName} ?n .
            {hasSpecies}
            ?n lit:{hasLit} ?v .
        }} order by ?v
        """.format(cprefix=CPREFIX,
                   lprefix=LITPREFIX,
                   hasIsoName="hasIsolateName",
                   hasSpecies=has_species,
                   hasLit=("hasLiteralValue"))

    result = trimResult(e.query(q))

    return result

####################################################################################################
# Returns the single species of an isolate, or if the isolate has a mixed species (recall we had it)
# so ":iso :hasSpecies :jejuni" and ":iso :hasSpecies :coli" if it was mixed coli and jejuni) we
# return the two species with "+" in the middle. EG coli + jejuni gets returned for an isolate with
# a mix of coli and jejuni.
####################################################################################################
def getIsoSpecies(iso):

    q = """
        {cprefix}
        select (group_concat(?sn ; separator=" + ") as ?species)
        where {{
            ?i :{hasSpecies} ?s .
            ?s :{hasName} ?sn .
            filter(?i = :{iso})
        }} group by ?i
        """.format(cprefix=CPREFIX, hasSpecies="hasSpecies", hasName="hasName", iso=iso)

    result = trimResult(e.query(q))

    return "".join(result)

####################################################################################################
# Returns the isolate sample location as "Country, Subnational, City"
####################################################################################################
def getLocation(iso):

    locs = ("Country", "Subnational", "City")

    result = []

    for loc in locs:
        q = """
            {cprefix}
            select ?n
            where {{
               :{iso} :{hasLocation} ?c . 
               ?c a :{loc} . 
               ?c :{hasName} ?n 
            }}""".format(cprefix=CPREFIX,
                         iso=iso,
                         hasLocation="hasSourceLocation",
                         loc=loc,
                         hasName="hasName")

        r = trimResult(e.query(q))

        if r:
            result.append(trimResult(e.query(q)))

    return ", ".join(result)


####################################################################################################
#
####################################################################################################
def getPropVal(subj, prop):

    q = """
        {cprefix}
        {lprefix}
        select ?val
        where {{
            :{subject} :{property} ?o .
            ?o (:{hasName}|lit:{hasLiteralValue}) ?val .
        }}
        """.format(cprefix=CPREFIX,
                   lprefix=LITPREFIX,
                   subject=subj,
                   property=prop,
                   hasName="hasName",
                   hasLiteralValue="hasLiteralValue")

    return trimResult(e.query(q))
