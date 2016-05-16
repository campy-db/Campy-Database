#from .extractValue import getSpecies
#from .shared_validators import validSpecies
import pandas as pd
from Scripts.endpoint import update as update

def popVals(my_dict):
    return {x:y for x, y in my_dict.iteritems() if y != ""}

#def isValidSpecies(name):
#    spec, subspec, un_spec= getSpecies(name)
#    valid, message = validSpecies(spec, subspec, un_spec)
#    return valid

def writeToOnt(t):
    print ("<<<<<<<<<<<<<<<<<<<<ATTEMPT>")
    with open("/home/student/CampyCopy/CampyDatabase/Ontologies/CampyOntology.owl", "a") as w:
        w.write(t)

####################################################################################################
# Later as in right now. Inserts the triples into blazegraph using the endpoint.py program written
# by our good friend Bryce Drew.
####################################################################################################
def writeToBG(t):
    print update("insert data{"+t+"}")
    #print ("[TEST]: " + t)

def isGoodVal(v):
    bad_words =\
    ("", "none", "-", "unknown", "n/a", "n\\a", "#n/a",\
     "#n\\a", "missing", "not given", "other", "na")

    v = v.strip().lower() if not isNumber(v) else v

    return v not in bad_words

def isNumber(s):

    try:
        float(s)
        return True
    except ValueError:
        return False

def cleanInt(s):

    if not pd.isnull(s) and isNumber(s):
        s = str(int(float(s)))

    return s

def remPrefix(val, l):

    if val != "" and not pd.isnull(val) and "_" in val:
        val = val[l:]
    return val