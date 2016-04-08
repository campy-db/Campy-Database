"""
 csvToDB
 Takes all the info from the excel campy 'database' and turns it into triples to insert into a
 triepl-store running on blazegraph.
"""

import pandas as pd

from .tripleWriters import *
from .endpoint import update
from .tripleWriters.campyTM import CAMPY as ctm


####################################################################################################
# writeToOnt
# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be
# insterted into blazegraph.
####################################################################################################
def writeToOnt(t):

    with open("/home/student/Campy/CampyDatabase/Ontologies/CampyOntology2.0.owl", "a") as w:
        w.write(t)

####################################################################################################
# writeToBG
# Later as in right now. Inserts the triples into blazegraph using the endpoint.py program written
# by our good friend Bryce Drew.
####################################################################################################
def writeToBG(t):
    print update("insert data{"+t+"}")

####################################################################################################
# createBIOtriples
# Create all the triples related to the bio properties of an isolate.
####################################################################################################
def createBIOtriples(df, row, isoTitle):

    triple = createRefTriples(df, row, isoTitle) # Reference strains

    triple += createSpeciesTriples(df, row, isoTitle) # Type of species

    triple += createTypingTriples(df, row, isoTitle) # Triples related to typing tests

    triple += createSMAtriples(df, row, isoTitle) # SMA 1 test triples

    triple += createSeroTriples(df, row, isoTitle) # Serotype triples

    triple += createAMRtriples(df, row, isoTitle) # Triples for AMR tests

    triple += createCGFtriples(df, row, isoTitle) # Triples for CGF data

    return triple

####################################################################################################
# createEPItriples
# Create triples for all the epi data for an isolate.
####################################################################################################
def createEPItriples(df, row, isoTitle):

    triple = createDTakenTriples(df, row, isoTitle) # The date the sample was taken

    triple += createLocTriples(df, row, isoTitle) # The location of where the sample was taken

    triple += createSourceTriples(df, row, isoTitle) # Triples for the isolate source

    triple += createOutbreakTriples(df, row, isoTitle) # Outbreak triples

    return triple

####################################################################################################
# createLIMStriples
# For all the triples related to LIMS data.
####################################################################################################
def createLIMStriples(df, row, isoTitle):

    triple = createDAddedTriples(df, row, isoTitle) # The date the isolate was added to the DB

    triple += createLabLocTriples(df, row, isoTitle) # The lab location of the isolate

    triple += createIDtriples(df, row, isoTitle) # For the collection IDs and sample IDs

    triple += createProjTriples(df, row, isoTitle) # Triples for the project info

    return triple

####################################################################################################
# createTriples
# Makes all the triples for a given isolate.
####################################################################################################
def createTriples(df, row):

    # Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the
    # original csv name aswell. Same goes for everything else with a name
    isoTitle = df["Strain Name"][row]

    triple = ctm.indTriple(isoTitle, "Isolate")+\
             ctm.propTriple(isoTitle, {"hasIsolateName":isoTitle}, True, True)

    triple += createIsolationTriples(df, row, isoTitle) # For isolation data

    triple += createBIOtriples(df, row, isoTitle)

    triple += createEPItriples(df, row, isoTitle)

    triple += createLIMStriples(df, row, isoTitle)

    #writeToOnt(triple) # Write to the owl file. Just for testing
    writeToBG(triple) # Write the triples to the blazegraph server

####################################################################################################
# Reads in data from the spreadsheet and writes triples
####################################################################################################
def writeData():

    df = pd.read_csv(r"/home/student/Campy/CSVs/2016-02-10 CGF_DB_22011_2.csv")

    # The column names contain a bunch of genes that need to be in the triplestore,
    # so we'll add those first
    triple = createGeneTriples(df)

    # The column names contain the names of the AMR drugs aswell
    triple += createDrugTriples(df)

    #writeToOnt(triple)

    writeToBG(triple)
    #df["Strain Name"].count()
    for row in range(df["Strain Name"].count()):
        if row > 20000:
            createTriples(df, row)

####################################################################################################
# Main
####################################################################################################
def main():
    writeData()

if __name__ == "__main__":
    main()
    