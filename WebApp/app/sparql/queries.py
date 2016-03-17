import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import endpoint as e
from Scripts import TripleMaker as tm
from Scripts.tripleWriters.campyTM import campy as ctm
from Scripts.tripleWriters.labTM import lab as ltm


######################################################################################################
# Global variables
######################################################################################################
lit = "http://www.essepuntato.it/2010/06/literalreification/"
litTM = tm.TripleMaker(lit)


######################################################################################################
# Functions
######################################################################################################

######################################################################################################
# writeToBG 
# Write a triple to the database running on blazegraph. Blazegraph server must be running for this
# to work.
#
# t - The triple to be inserted.
######################################################################################################
def writeToBG(t):
	print e.update("insert data{"+t+"}")

######################################################################################################
# trimResult
# The result sent back from the blazegraph server is a messy dictionary with the bindings as a list
# for the key "bindings". URIS have the key "", while literals have the key "v". We return a list of
# the URI, or literal bindings. Returns a list.
#
# r - The result we got from blazegraph
# isLiteral - True if the results are literals
######################################################################################################
def trimResult(r):

	l = []
	for v in r["results"]["bindings"]:
		l.append(v["v"]["value"])
	return l

######################################################################################################
# getIsoNames
# Returns a list of the isolate names.
######################################################################################################
def getIsoNames():

	q = "select ?v where {?i %s ?n . ?n %s ?v .}"\
	    %(ctm.addUri("hasIsolateName"),(litTM.addUri("hasLiteralValue")))

	result = e.query(q)
	return trimResult(result)


######################################################################################################
# main
# Just for testing.
######################################################################################################
def main():
	print getIsoNames()

if __name__ == "__main__":
	main()
	