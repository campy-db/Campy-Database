"""
 queries.py

 Gernal SPARQL queries.

"""

import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.tripleWriters.labTM import LAB as ltm


####################################################################################################
# Global variables
####################################################################################################
LIT = "http://www.essepuntato.it/2010/06/literalreification/"
LITTM = tm.TripleMaker(LIT)

####################################################################################################
# FUNCTIONS
####################################################################################################

####################################################################################################
# writeToBG
#
# Write a triple to the database running on blazegraph. Blazegraph server must be running for this
# to work.
#
# t - The triple to be inserted.
####################################################################################################
def writeToBG(t):
    q = "insert data{{{}}}".format(t)
    print q

####################################################################################################
# trimResult
#
# The result sent back from the blazegraph server is a messy dictionary with the bindings as a list
# for the key "bindings". URIS have the key "", while literals have the key "v". We return a list of
# the URI, or literal bindings. Returns a list.
#
# r - The result we got from blazegraph
# isLiteral - True if the results are literals
####################################################################################################
def trimResult(result, v):

    l = []
    for b in result["results"]["bindings"]:
        l.append(b[v]["value"])

    return l

####################################################################################################
# isA
#
# returns True if title is an instance of class_
####################################################################################################
def isA(title, class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        ask
        where{{
            {title} a {class_}
        }}
        """.format(title=ctm.addURI(title), class_=ctm.addURI(class_))

    return e.query(q)["boolean"]

####################################################################################################
# getLowestClass
#
# Get the lowest level subclasses of _class. IE get all the subclasses of _class that have
# no subclasses of their own.
####################################################################################################
def getLowestClasses(class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        select ?label 
        where 
        {{ 
            ?spec rdfs:subClassOf {c} .
            ?spec rdfs:label ?label . 
            filter(?spec != {c}) . 
            filter not exists 
            {{
                ?sub rdfs:subClassOf ?spec . 
                filter(?sub != ?spec) 
            }}
        }}
        """.format(c=ctm.addURI(class_))

    result = e.query(q)

    return trimResult(result, "label")

####################################################################################################
# getSuperClasses
#
# Returns all the subclasses of _class that have a subclass of their own.
####################################################################################################
def getSuperClasses(_class):

    _class = _class[0].upper() + _class[1:]

    q = """
        select distinct ?label
        where 
        {{ 
            ?spec rdfs:subClassOf {c} .
            ?spec rdfs:label ?label .
            ?sub rdfs:subClassOf ?spec .
            filter (?spec != {c} && ?sub != ?spec)  
        }}
        """.format(c=ctm.addURI(_class))

    result = e.query(q)

    return trimResult(result, "label")

####################################################################################################
# getSubClasses
# Get all the subclasses of _class.
####################################################################################################
def getSubClasses(_class):

    _class = _class[0].upper() + _class[1:]

    q = """
        select ?label 
        where 
        {{
            ?sub rdfs:subClassOf {super} . 
            ?sub rdfs:label ?label . 
            filter(?sub != {super})
        }}
        """.format(super=ctm.addURI(_class))

    result = e.query(q)

    return trimResult(result, "label")

####################################################################################################
# main
# Just for testing.
####################################################################################################
def main():
    pass

if __name__ == "__main__":
    main()
    