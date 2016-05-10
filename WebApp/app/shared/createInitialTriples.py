from .shared.tripleWriters.createAntigenTriples import getAntigenTriples
from Scripts.endpoint import update
def writeData():
    
    #triple = createGeneTriples(df)

    #AMR
    #triple += createDrugTriples(df)
    triple = getAntigenTriples()
    print(triple)
    #writeToOnt(triple) 

    #writeToBG(triple)
    #for row in range(num_rows):
    #    createTriples(df, row)




# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be
# insterted into blazegraph.
####################################################################################################
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