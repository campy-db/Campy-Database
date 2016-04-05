import sys
sys.path.append("/home/student/Campy/CampyDatabase")

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
def trimResult(r, v):

	l = []
	for b in r["results"]["bindings"]:
		l.append(b[v]["value"])

	return l

######################################################################################################
# getIsoNames
# Returns a list of the isolate names.
######################################################################################################
def getIsoNames():

	q = "select ?v where {{?i {} ?n . ?n {} ?v .}}"\
	    .format(ctm.addURI("hasIsolateName"),(litTM.addURI("hasLiteralValue")))

	result = e.query(q)
	
	return trimResult(result, "v")

######################################################################################################
# getSource
######################################################################################################
def getSources():

	q = "select distinct ?n where {{?s a {SampleSource} . ?s {hasName} ?n . }}"\
	    .format(SampleSource = ctm.addURI("SampleSource"), hasName = ctm.addURI("hasName"))

	result = e.query(q)

	return trimResult(result, "n")

######################################################################################################
# getLowestClass
# Get the lowest level subclasses of _class. IE get all the subclasses of _class that have
# no subclasses of their own. 
######################################################################################################
def getLowestClasses(_class):

	_class = _class[0].upper() + _class[1:]

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
		""".format(c = ctm.addURI(_class))

	result = e.query(q)

	return trimResult(result, "label")

######################################################################################################
# getHighestClasses
# Returns all the subclasses of _class that have a subclass of their own.
######################################################################################################
def getHighestClasses(_class):

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
		""".format(c = ctm.addURI(_class))

	result = e.query(q)

	return trimResult(result, "label")


######################################################################################################
# getSubClasses
# Get all the subclasses of _class.
######################################################################################################
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
		""".format(super = ctm.addURI(_class))

	result = e.query(q)

	return trimResult(result, "label")

######################################################################################################
# main
# Just for testing.
######################################################################################################
def main():
	print getSources()

if __name__ == "__main__":
	main()
	