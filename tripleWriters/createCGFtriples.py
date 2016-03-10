import pandas as pd
import campyTM as ctm
import labTM as ltm
import cleanCSV as cn

######################################################################################################
# Get the CGF ref cluster numbers, make triples.
# Given a ref cluster x_y_z, the cluster follows the nameing convention CGF_N_x_y_x, where N is the 
# threshold. Similarly for ref clusters x and x_y.
######################################################################################################
def createClustTriples(df,row,cgfTest):
	clustTriple=""
	refClust=df["REF CLUSTER 90_95_100"][row]

	if not pd.isnull(refClust) and cn.isGoodVal(refClust):
		clusters=refClust.split("_")
		c90=clusters[0]
		c95=clusters[1]
		c100=clusters[2]

		c90name="CGF_90_"+c90
		c95name="CGF_95_"+c90+"_"+c95
		c100name="CGF_100_"+c90+"_"+c95+"_"+c100

		c90Triple=ltm.lab.indTriple(c90name,"CGFcluster")+\
				  ltm.lab.propTriple(c90name,{"hasThreshold":"90","hasClustNum":c90},"int",True)+\
				  ltm.lab.propTriple(c90name,{"hasSubCluster":c95name},False)
		c95Triple=ltm.lab.indTriple(c95name,"CGFcluster")+\
		          ltm.lab.propTriple(c95name,{"hasThreshold":"95","hasClustNum":c95},"int",True)+\
		          ltm.lab.propTriple(c95name,{"hasSubCluster":c100name},False)
		c100Triple=ltm.lab.indTriple(c100name,"CGFcluster")+\
				   ltm.lab.propTriple(c100name,{"hasThreshold":"100","hasClustNum":c100},"int",True)

		cgfRefTriple=ltm.lab.propTriple(cgfTest,{"hasCluster":[c90name,c95name,c100name]})
		clustTriple=c90Triple+c95Triple+c100Triple+cgfRefTriple
	return clustTriple

######################################################################################################
#
######################################################################################################
def createCGFtriples(df,row,isoTitle):
	# A CGF test will follow the naming convention "CGFisolateName".
	labTriple=""
	cgfTest1="cgf_"+isoTitle
	fingerprint=df["Fingerprint"][row]
	legacyHexNum=df["BIN"][row]
	typingLab=df["TYPING LAB"][row]

	# The file location of the cgf info and the date it was completed are stored in the same cells.
	# The values are of the form DATE FILELOC, or just DATE
	fileLoc=""
	date=""
	date_fileLoc=df["Date CGF completed"][row]

	if not pd.isnull(date_fileLoc) and cn.isGoodVal(date_fileLoc):
		date=date_fileLoc.split(" ")[0]
		date=cn.convertDate(date)

		index=date_fileLoc.find(" ")
		if index!=-1:
			fileLoc=date_fileLoc[index+1:]

	# Every isolate has a cgf test
	cgfTriple=ltm.lab.indTriple(cgfTest1,"CGFtest")

	# Every cgf test in the csv is inVitro
	cgfTriple+=ltm.lab.propTriple(cgfTest1,{"isInVitro":"true"},"bool",True)

	if fileLoc!="":
		cgfTriple+=ltm.lab.propTriple(cgfTest1,{"hasFileLocation":fileLoc},"string",True)
	if date!="":
		cgfTriple+=ltm.lab.propTriple(cgfTest1,{"hasDateCompleted":date},"string",True)

	if not pd.isnull(fingerprint) and cn.isGoodVal(fingerprint):
		fingerprint=fingerprint.replace("fp","")
		cgfTriple+=ltm.lab.propTriple(cgfTest1,{"hasFingerprint":fingerprint},"string",True)

	if not pd.isnull(legacyHexNum) and cn.isGoodVal(legacyHexNum):
		legacyHexNum=legacyHexNum.replace("BIN","")
		cgfTriple+=ltm.lab.propTriple(cgfTest1,{"hasLegacyHexNum":legacyHexNum},"string",True)

	if not pd.isnull(typingLab) and cn.isGoodVal(typingLab):
		# Have to create a typing lab triple and then attach the cgf test to it
		labTriple=ltm.lab.indTriple(typingLab,"TypingLab") # labTitle is an instance of the class TypingLab

		# Right now the URI for hasName is the campy ont. URI. Gonna have to change it to a URI seperate
		# from both campy and labTest URI. WE MUST FIX THIS
		labTriple+=ltm.lab.addUri(cn.cleanString(typingLab))+" "+\
				   ctm.campy.addUri("hasName")+" \"%s\" .\n" % (typingLab)

		# Attach the lab to the cgf test
		cgfTriple+=ltm.lab.propTriple(cgfTest1,{"doneAtLab":typingLab})
		

	clustTriple=createClustTriples(df,row,cgfTest1)
	if clustTriple!="":
		cgfTriple+=clustTriple
	
	# Some triples have more than one URI, so we make our own using TripleMaker's 
	# helper function addUri. WE MUST FIX THIS
	isoTriple=ctm.campy.addUri(cn.cleanString(isoTitle))+" "+ctm.campy.addUri("hasLabTest")+" "+\
		      ltm.lab.addUri(cn.cleanString(cgfTest1))+" .\n"

	return labTriple+cgfTriple+isoTriple