import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import cleanCSV as cn
from Scripts.TripleMaker import TripleMaker as tm
import pandas as pd
from campyTM import campy as ctm
from labTM import lab as ltm

######################################################################################################
# Get the CGF ref cluster numbers, make triples.
# Given a ref cluster x_y_z, the cluster follows the nameing convention CGF_N_x_y_x, where N is the 
# threshold. Similarly for ref clusters x and x_y.
######################################################################################################
def createClustTriples(df, row, cgfTest):

	clustTriple = ""
	refClust = df["REF CLUSTER 90_95_100"][row]

	if not pd.isnull(refClust) and cn.isGoodVal(refClust):

		clusters = refClust.split("_")
		c90 = int(clusters[0])
		c95 = int(clusters[1])
		c100 = int(clusters[2])

		c90name = "{}_{}_{}".format("CGF", 90, c90)
		c95name = "{}_{}_{}_{}".format("CGF", 95, c90, c95)
		c100name = "{}_{}_{}_{}_{}".format("CGF", 100, c90, c95, c100)

		c90Triple = ltm.indTriple(c90name,"CGFcluster")+\
				  ltm.propTriple(c90name, {"hasThreshold":90, "hasClustNum":c90}, True, True)+\
				  ltm.propTriple(c90name, {"hasSubCluster":c95name})

		c95Triple = ltm.indTriple(c95name, "CGFcluster")+\
		          ltm.propTriple(c95name, {"hasThreshold":95,"hasClustNum":c95}, True, True)+\
		          ltm.propTriple(c95name, {"hasSubCluster":c100name})

		c100Triple = ltm.indTriple(c100name,"CGFcluster")+\
				   ltm.propTriple(c100name, {"hasThreshold":100,"hasClustNum":c100}, True, True)

		cgfRefTriple = ltm.propTriple(cgfTest,{"hasCluster":[c90name, c95name, c100name]})
		clustTriple = c90Triple+c95Triple+c100Triple+cgfRefTriple

	return clustTriple

######################################################################################################
#
######################################################################################################
def createCGFtriples(df, row, isoTitle):

	# A CGF test will follow the naming convention "CGFisolateName".
	labTriple = ""
	cgfTest = "cgf_" + isoTitle
	fingerprint = df["Fingerprint"][row]
	legacyHexNum = df["BIN"][row]
	typingLab = df["TYPING LAB"][row]

	# The file location of the cgf info and the date it was completed are stored in the same cells.
	# The values are of the form DATE FILELOC, or just DATE
	fileLoc = ""
	date = ""
	date_fileLoc = df["Date CGF completed"][row]

	if not pd.isnull(date_fileLoc) and cn.isGoodVal(date_fileLoc):

		date = date_fileLoc.split(" ")[0]
		date = cn.convertDate(date, False)

		index = date_fileLoc.find(" ")

		if index != -1:
			fileLoc = date_fileLoc[index+1:]

	# Every isolate has a cgf test
	cgfTriple = ltm.indTriple(cgfTest, "CGF_test")

	# Every cgf test in the csv is in Vitro
	cgfTriple += ltm.propTriple(cgfTest,{"isInSilico":False}, True, True)

	if fileLoc:
		cgfTriple += ltm.propTriple(cgfTest,{"hasFileLocation":fileLoc}, True, True)  

	if date and date != -1:

		dates = date.split("-")

		dates = [int(float(d)) for d in dates]

		cgfTriple += ltm.propTriple(cgfTest, {"hasDayCompleted":dates[2], 
		             			              "hasMonthCompleted":dates[1],
		                                      "hasYearCompleted":dates[0]}, True, True)

	if not pd.isnull(fingerprint) and cn.isGoodVal(fingerprint):
		fingerprint = str(fingerprint.replace("fp","")) # long type maybe? Leading zeroes? What do??
		cgfTriple += ltm.propTriple(cgfTest, {"foundFingerprint":fingerprint}, True, True)

	if not pd.isnull(legacyHexNum) and cn.isGoodVal(legacyHexNum):
		legacyHexNum = str(legacyHexNum.replace("BIN",""))
		cgfTriple += ltm.propTriple(cgfTest, {"foundLegacyHexNum":legacyHexNum}, True, True)


	if not pd.isnull(typingLab) and cn.isGoodVal(typingLab):

		# Have to create a typing lab triple and then attach the cgf test to it
		labTriple = ltm.indTriple(typingLab,"TypingLab") # labTitle is an instance of the class TypingLab

		labTriple += tm.multiURI(( typingLab, "hasName", "\"{}\"".format(typingLab)),\
			         (ltm.uri, ctm.uri), True )

		# Attach the lab to the cgf test
		cgfTriple += ltm.propTriple(cgfTest,{"doneAtLab":typingLab})
		
	clustTriple = createClustTriples(df,row,cgfTest)

	if clustTriple:
		cgfTriple += clustTriple
	

	isoTriple = tm.multiURI( (isoTitle, "hasLabTest", cgfTest), (ctm.uri, ctm.uri, ltm.uri) )

	return labTriple+cgfTriple+isoTriple
