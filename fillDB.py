# -*- coding: latin-1 -*-
from tripleWriters import campyTM as ctm
import endpoint as e
import pandas as pd
import re
import tripleWriters as tw

######################################################################################################
# Takes all the info from the excel campy 'database' and turns it into triples to insert into a triple 
# store running on blazegraph
######################################################################################################

######################################################################################################
# writeToOnt
# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be 
# insterted into blazegraph.
######################################################################################################
def writeToOnt(t):
	with open('/home/student/CampyDB/CampyOnt/CampyOntology2.0.owl','a') as w:
		w.write(t)

######################################################################################################
# writeToBG
# Later as in right now. Inserts the triples into blazegraph using the endpoint.py program written
# by our good friend Bryce Drew.
######################################################################################################
def writeToBG(t):
	print e.update("insert data{"+t+"}")

######################################################################################################
#
######################################################################################################
def createTriples(df,row):
	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoTitle=df["Strain Name"][row]

	triple=ctm.campy.indTriple(isoTitle,"Isolate")+\
		   ctm.campy.propTriple(isoTitle,{"hasIsolateName":isoTitle},"string",True)

	triple+=tw.createLocTriples(df,row,isoTitle)

	triple+=tw.createOutbreakTriples(df,row,isoTitle)

	triple+=tw.createSourceTriples(df,row,isoTitle)

	triple+=tw.createRefTriples(df,row,isoTitle)

	triple+=tw.createProjTriples(df,row,isoTitle)

	triple+=tw.createCGFtriples(df,row,isoTitle)

	triple+=tw.createSpeciesTriples(df,row,isoTitle)

	triple+=tw.createDateTriples(df,row,isoTitle)

	triple+=tw.createLIMStriples(df,row,isoTitle)

	triple+=tw.createIsolationTriples(df,row,isoTitle)

	triple+=tw.createTypingTriples(df,row,isoTitle)
	
	triple+=tw.createSMAtriples(df,row,isoTitle)

	triple+=tw.createSeroTriples(df,row,isoTitle)
	
	triple+=tw.createAMRtriples(df,row,isoTitle)
	
	writeToOnt(triple)
	#writeToBG(triple)
	
######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():
	df=pd.read_csv(r"/home/student/CampyDB/2016-02-10 CGF_DB_22011_2.csv")

	# The column names contain a bunch of genes that need to be in the triplestore,
	# so we'll add those first
	triple=tw.createGeneTriples(df)
	# The column names contain the names of the AMR drugs aswell
	triple+=tw.createDrugTriples(df)

	writeToOnt(triple)

	#createTriples(df,4974)
	#range(df["Strain Name"].count())
	for row in range(df["Strain Name"].count()):
		createTriples(df,row)

######################################################################################################
# Main
######################################################################################################
def main():
	writeData()


if __name__=="__main__":
	main()
	






			

			
	
