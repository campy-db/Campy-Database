import endpoint as e
import TripleMaker as tm

c="https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#"
l="http://www.essepuntato.it/2010/06/literalreification/"
t="https://github.com/samuel-peers/campyOntology/blob/master/LabTests.owl#"
ctm=tm.TripleMaker(c)
ltm=tm.TripleMaker(l)
ttm=tm.TripleMaker(t)

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
	l=[]
	for v in r["results"]["bindings"]:
		l.append(v["v"]["value"])
	return l

######################################################################################################
# getIsoNames
# Returns a list of the isolate names.
######################################################################################################
def getIsoNames():
	q="select ?v where {?i %s ?n . ?n %s ?v .}"\
	   %(ctm.addUri("hasIsolateName"),(ltm.addUri("hasLiteralValue")))

	result=e.query(q)
	return trimResult(result)

######################################################################################################
# insertIso
######################################################################################################
def insertIso(title,props,litType,isRLiteral):
	triple=ctm.indTriple(title,"Isolate")+\
		   ctm.propTriple(title,props,litType,isRLiteral)

	#writeToBG(triple)
	print triple



######################################################################################################
# main
# Just for testing.
######################################################################################################
def main():
	print getIsoNames()

if __name__=="__main__":
	main()
	