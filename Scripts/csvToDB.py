# -*- coding: latin-1 -*-
from tripleWriters.campyTM import campy as ctm
import endpoint as e
import pandas as pd
import re
import tripleWriters as tw

######################################################################################################
# Takes all the info from the excel campy 'database' and turns it into triples to insert into a triple 
# store running on blazegraph.
######################################################################################################

######################################################################################################
# writeToOnt
# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be 
# insterted into blazegraph.
######################################################################################################
def writeToOnt(t):

	with open('/home/student/CampyDB/CampyDatabase/Ontologies/CampyOntology2.0.owl','a') as w:
		w.write(t)

######################################################################################################
# writeToBG
# Later as in right now. Inserts the triples into blazegraph using the endpoint.py program written
# by our good friend Bryce Drew.
######################################################################################################
def writeToBG(t):

	print e.update("insert data{"+t+"}")

######################################################################################################
# createBIOtriples
# Create all the triples related to the bio properties of an isolate.
######################################################################################################
def createBIOtriples(df,row,isoTitle):

	triple=tw.createRefTriples(df,row,isoTitle) # Reference strains

	triple+=tw.createSpeciesTriples(df,row,isoTitle) # Type of species

	triple+=tw.createTypingTriples(df,row,isoTitle) # Triples related to typing tests
	
	triple+=tw.createSMAtriples(df,row,isoTitle) # SMA 1 test triples

	triple+=tw.createSeroTriples(df,row,isoTitle) # Serotype triples
	
	triple+=tw.createAMRtriples(df,row,isoTitle) # Triples for AMR tests

	triple+=tw.createCGFtriples(df,row,isoTitle) # Triples for CGF data

	return triple

######################################################################################################
# createEPItriples
# Create triples for all the epi data for an isolate.
######################################################################################################
def createEPItriples(df,row,isoTitle):

	triple=tw.createDTakenTriples(df,row,isoTitle) # The date the sample was taken

	triple+=tw.createLocTriples(df,row,isoTitle) # The location of where the sample was taken

	triple+=tw.createSourceTriples(df,row,isoTitle) # Triples for The animal, human, or envrio source 

	triple+=tw.createOutbreakTriples(df,row,isoTitle) # Outbreak triples

	return triple

######################################################################################################
# createLIMStriples
# For all the triples related to LIMS data.
######################################################################################################
def createLIMStriples(df,row,isoTitle):

	triple=tw.createDAddedTriples(df,row,isoTitle) # The date the isolate was added to the DB

	triple+=tw.createLabLocTriples(df,row,isoTitle) # The lab location of the isolate

	triple+=tw.createIDtriples(df,row,isoTitle) # For the collection IDs and sample IDs

	triple+=tw.createProjTriples(df,row,isoTitle) # Triples for the project info

	return triple

######################################################################################################
# createTriples
# Makes all the triples for a given isolate.
######################################################################################################
def createTriples(df,row):

	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoTitle=df["Strain Name"][row]

	triple=ctm.indTriple(isoTitle,"Isolate")+\
		   ctm.propTriple(isoTitle,{"hasIsolateName":isoTitle},"string",True)

	triple+=tw.createIsolationTriples(df,row,isoTitle) # For isolation data

	triple+=createBIOtriples(df,row,isoTitle)

	triple+=createEPItriples(df,row,isoTitle)

	triple+=createLIMStriples(df,row,isoTitle)

	#writeToOnt(triple) # Write to the owl file. Just for testing
	#writeToBG(triple) # Write the triples to the blazegraph server
	
######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():

	df=pd.read_csv(r"/home/student/CampyDB/CSVs/2016-02-10 CGF_DB_22011_2.csv")

	# The column names contain a bunch of genes that need to be in the triplestore,
	# so we'll add those first
	triple=tw.createGeneTriples(df)

	# The column names contain the names of the AMR drugs aswell
	triple+=tw.createDrugTriples(df)

	#writeToBG(triple)
	#df["Strain Name"].count()
	for row in range(df["Strain Name"].count()):
		createTriples(df,row)

######################################################################################################
# Main
######################################################################################################
def main():
	writeData()

if __name__=="__main__":
	main()
	