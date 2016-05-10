#from .extractValue import getSpecies
#from .shared_validators import validSpecies
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

def main():
    print("[INFO] Required population of the database has started. Please run this script only once.")