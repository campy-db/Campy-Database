"""
 data_queries.py

 Specific sparql queries for retrieving a set of data
"""

import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import CAMPY as CTM
from Scripts.tripleWriters.labTM import LAB as LTM


####################################################################################################
# Global variables
#

####################################################################################################
LIT_URI = "http://www.essepuntato.it/2010/06/literalreification/"
LIT = tm.TripleMaker(LIT_URI)


####################################################################################################
# trimResult
#
# Returns a list of lists, where the lists are all the bindings for the vars in the query. EG if we
# do "select ?a ?b ?c ?d ..." then we'll have a list that looks like:
# [[a1, b1, c1, d1], [a2, b2, c2, d2], ..., [ak, bk, ck, dk]], where a# is the binding for ?a, same
# deal for the other letters.
# Returns a list if there is only one var in the query, IE each list in the list has length 1. EG if
# after the for loop, l = [[a], [a1], ..., [ak]], then we return [a, a1, ..., ak].
# Returns a list of values if after the for loop, the outer list contains one list. EG if
# l = [[a, b, c]], then return [a, b, c].
# Returns a single string if the result is one single value in a single inner list. EG if after the
# for loop, l = [["someval"]], we return "someval"
####################################################################################################
def trimResult(r):

    result = []
    vars_ = r["head"]["vars"]
    for b in r["results"]["bindings"]:
        triple = []
        for v in vars_:
            triple.append(b[v]["value"])
        result.append(triple)

    if len(vars_) == 1:
        result = ["".join(v) for v in result]

    if len(result) == 1:
        result = result[0]

    return result

####################################################################################################
# getIsoNames
#
# Returns a list of the isolate names.
####################################################################################################
def getIsoNames():

    q = """
        select ?v 
        where {{
            ?i {hasIsoName} ?n . 
            ?n {hasLit} ?v .
        }}
        """.format(hasIsoName=CTM.addURI("hasIsolateName"),
                   hasLit=(LIT.addURI("hasLiteralValue")))

    result = trimResult(e.query(q))

    return result

####################################################################################################
# getSpecies
#
# Returns the single species of an isolate, or if the isolate has a mixed species (recall we had it)
# so ":iso :hasSpecies :jejuni" and ":iso :hasSpecies :coli" if it was mixed coli and jejuni) we
# return the two species with "+" in the middle. EG coli + jejuni gets returned for an isolate with
# a mix of coli and jejuni.
####################################################################################################
def getSpecies(iso):

    q = """
        select (group_concat(?sn ; separator=" + ") as ?species)
        where {{
            ?i {hasSpecies} ?s .
            ?s {hasName} ?sn .
            filter(?i = {iso})
        }} group by ?i
        """.format(iso=CTM.addURI(iso),
                   hasSpecies=CTM.addURI("hasSpecies"),
                   hasName=CTM.addURI("hasName"))

    result = trimResult(e.query(q))

    return "".join(result)

####################################################################################################
# getLocation
####################################################################################################
def getLocation(iso):

    hsl = CTM.addURI("hasSourceLocation")
    hn = CTM.addURI("hasName")
    iso = CTM.addURI(iso)

    locs = ("Country", "SubNational", "City")

    result = []

    for loc in locs:
        q = """
            select ?n
            where {{
               {iso} {hsl} ?c . 
               ?c a {loc} . 
               ?c {hn} ?n 
            }}""".format(iso=iso, hsl=hsl, loc=CTM.addURI(loc), hn=hn)

        r = trimResult(e.query(q))

        if r:
            result.append(trimResult(e.query(q)))

    return ", ".join(result)


####################################################################################################
# getPropVal
####################################################################################################
def getPropVal(subj, prop):

    q = """
        select ?val
        where {{
            {subject} {property} ?o .
            ?o ({hasName}|{hasLiteralValue}) ?val .
        }}
        """.format(subject=CTM.addURI(subj),
                   property=CTM.addURI(prop),
                   hasName=CTM.addURI("hasName"),
                   hasLiteralValue=LIT.addURI("hasLiteralValue"))

    return trimResult(e.query(q))
