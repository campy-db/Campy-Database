"""
 queries.py

 General SPARQL queries.

"""

import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import CAMPY as ctm
from Scripts.tripleWriters.labTM import LAB as ltm
from .shared import *

####################################################################################################
# FUNCTIONS
####################################################################################################

####################################################################################################
# Returns True if title is an instance of class_
####################################################################################################
def isA(title, class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        {cprefix}
        ask
        where{{
            :{title} a :{class_}
        }}
        """.format(cprefix=CPREFIX, title=title, class_=class_)

    return e.query(q)["boolean"]

####################################################################################################
# Get the lowest level subclasses of class_. IE get all the subclasses of class_ that have
# no subclasses of their own.
####################################################################################################
def getLowestClasses(class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        {cprefix}
        select ?label 
        where 
        {{ 
            ?spec rdfs:subClassOf :{c} .
            ?spec rdfs:label ?label . 
            filter(?spec != :{c}) . 
            filter not exists 
            {{
                ?sub rdfs:subClassOf ?spec . 
                filter(?sub != ?spec) 
            }}
        }}
        """.format(cprefix=CPREFIX, c=class_)

    result = e.query(q)

    return trimResult(result)

####################################################################################################
# Returns all the subclasses of class_ that have a subclass of their own.
####################################################################################################
def getSuperClasses(class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        {cprefix}
        select distinct ?label
        where 
        {{ 
            ?spec rdfs:subClassOf :{c} .
            ?spec rdfs:label ?label .
            ?sub rdfs:subClassOf ?spec .
            filter (?spec != :{c} && ?sub != ?spec)  
        }}
        """.format(cprefix=CPREFIX, c=class_)

    result = e.query(q)

    return trimResult(result)

####################################################################################################
# Get all the subclasses of class_.
####################################################################################################
def getSubClasses(class_):

    class_ = class_[0].upper() + class_[1:]

    q = """
        {cprefix}
        select ?label 
        where 
        {{
            ?sub rdfs:subClassOf :{super} . 
            ?sub rdfs:label ?label . 
            filter(?sub != :{super})
        }}
        """.format(cprefix=CPREFIX, super=class_)

    result = e.query(q)

    return trimResult(result)

####################################################################################################
# MAIN
# Just for testing.
####################################################################################################
def main():
    pass

if __name__ == "__main__":
    main()
    