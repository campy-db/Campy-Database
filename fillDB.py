import TripleMaker as tm
import cleanCSV as cn
import pandas as pd
import re
import pycountry as pc
from datetime import date
######################################################################################################
# Takes all the info from the excel campy database and turns it into triples to insert into a triple 
# store running on blazegraph
######################################################################################################

######################################################################################################
# Global variables
######################################################################################################
subNats=[x.name for x in list(pc.subdivisions)] # A list of names of subnationals
countries=[x.name for x in list(pc.countries)] # A list of names of countries

campy=tm.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#")
lab=tm.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/LabTests.owl#")

######################################################################################################
# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be 
# insterted into blazegraph.
######################################################################################################
def putInOnt(t):
	with open('/home/student/CampyDB/CampyOnt/CampyOntology2.0.owl','a') as w:
		w.write(t)

######################################################################################################
# Because of some Excel constraint, the hex number equivalent of the whole binary isn't possible.
# So the hexnumber is the hex of the first 5 digits in the binary concatenated to the hex of 
# the next 5, concatenated to the hex of the next 5 etc. 
# For now we're just reading in the legacy hex from the csv, but I figured we'll need this code in the
# future.
######################################################################################################
def getHex(binary):
	m=0
	hexNum=""
	for b in range(8):
		current=str(hex(int(binary[m:(m+5)],2))).lstrip("0x")
		if len(current)==1:
			current="0"+current
		hexNum+=current
		m+=5
	if hexNum=="":
		hexNum=0
	return hexNum

######################################################################################################
# Gets the genes that were found by a CGF test by using the fingerprint.
# We don't need this for filling the DB, we'll need it in the future for when people want the names
# of the cgf genes or whatever. We'll just keep this here for now though
######################################################################################################
def getGenes(fingerprint,cgfGenes):
	i=0;
	result=[]
	for n in fingerprint:
		if n=='1':
			result.append(c.cleanString(cgfGenes[i]))
		i+=1
	return result

######################################################################################################
#
######################################################################################################
def createAgeTriples(df,row,hum):
	humTriple=""
	yearLen=4
	ageLen=2
	age=df["Patient D.O.B / Age"][row]
	yearTaken=cn.cleanNum(df["YEAR"][row]) # The year values are converted to floats for some reason
										   # in the csv. We convert it to a string
	if not pd.isnull(age) and age!="Missing" and "Given" not in age: 
		if len(age)>ageLen: # if a birthday or range
			if "years" in age: # Every range contains the word 'years'.
				# Most ranges are of the form age-age, but some are age+
				pass
			else: # The value is a birth day
				bday=cn.convertDate(age)
				humTriple+=campy.propTriple(hum,{"hasBirthDate":bday},True,rLiteral=True)
				
				if not pd.isnull(yearTaken):
					age=int(yearTaken)-int(bday[:yearLen]) # bday is in ISO format, so the first 4 chars
													 # is the year of the bday
					if age<0: # One of the patients was born in 2011,but the sample was taken in 2010
						age=0
				else:
					age=date.today().year-int(bday[:yearLen]) # Use todays year for the age

		humTriple+=campy.propTriple(hum,{"hasAge":str(age)},True,rLiteral=True)	
		#print humTriple

	return humTriple


######################################################################################################
#
######################################################################################################
def createTravelTriples(df,row,hum):
	humTriple=""
	trTriple="" # Travel info triple
	travel=df["Comments"][row] # All travel info is in the comments column
	
	# We will keep the lowest level or ganularity, eg from 'Ohio, USA' we'll keep only Ohio as USA
	# is derivable (consider revising).
	# 'Ohio, USA', 'Ukraine', 'New Brunswick', 'Alberta', 'Cuba', and 'Italy' are the only travel
	# destinations in the csv
	if not pd.isnull(travel) and "Travel" in travel: # All travel values are prefixed with 'Travel: '
		travel=travel.replace("Travel:","").strip()

		# Some values are suffixed with a bunch of meaningless(ful?) stuff
		end=re.search("[;,]",travel)
		travel=travel[:end.span()[0]] if end is not None else travel

		if travel in subNats:
			trTriple=campy.indTriple(travel,"SubNational")
		if travel in countries:
			trTriple=campy.indTriple(travel,"Country")

		trTriple+=campy.propTriple(travel,{"hasName":travel},True)
		humTriple=campy.propTriple(hum,{"traveledTo":travel},False)
		#print trTriple+humTriple
	return trTriple+humTriple


######################################################################################################
#
######################################################################################################
def createHumanTriples(df,row,isoTitle):
	hum="patient_"+isoTitle # Need a unique identifier for humans as they have different 
						    # ages, genders, and postal codes I'm told
	gender=df["Gender"][row]
	postalCode=df["Postal code"][row]

	# Just create a generic human individual
	humTriple=campy.indTriple(hum,"Patient") # All human samples in the csv are patients
	humTriple+=campy.propTriple(hum,{"hasName":hum},True)

	# Travel info is in the column 'comments' and it's quite messy so we'll
	# handle it separately 
	humTriple+=createTravelTriples(df,row,hum)

	# The age is stored in a column with birthdays and other random crap so we'll 
	# handle it separately
	humTriple+=createAgeTriples(df,row,hum)

	# The values 0, m, f, male, female and 'not given' are in the csv. We won't add the prop if it's 'not given'
	if not pd.isnull(gender) and gender!="Not Given" and gender!=0:
		humTriple+=campy.propTriple(hum,{"hasGender":gender[0]},True,rLiteral=True)

	if not pd.isnull(postalCode):
		humTriple+=campy.propTriple(hum,{"hasPostalCode":postalCode},True,rLiteral=True)

	isoTriple=campy.propTriple(isoTitle,{"hasHumanSource":hum},False)
	#print cvals[0]
	#print humTriple
	# Insert humTriple
	# Insert isoTriple


######################################################################################################
#
######################################################################################################
def createEnviroTriples(df,row,isoTitle):
	enviroTriple=""
	isoTriple=""
	enviro=cn.remPrefix(df["Source General"][row],2) # Water, lagoon, sewage, sand, unknown
	enviroSpec=df["Source_Specific_2"][row] # Lagoon:Dairy, Sewage (treated) etc.

	# If enviroSpec (the source specific 2 value) is actually something meaningful, it will be an 
	# instance of the class enviro, eg 'Swine' is an instance of the class 'Lagoon', 'Treated' is an 
	# instance of 'Sewage'. For other random enviroSpec values, like 'other', 'water' (when we already 
	# have water as the enviro value), the instance will just be the name of the class. The enviro 
	# value 'sand' is special in that it is not a class in ontology, it will be an instance of the 
	# class 'Substrate'. Future soil samples can go in this class too if need be.

	if not pd.isnull(enviro) and "Unknown" not in enviro:
		# enviro (Source general) is the class and enviroSpec (source specific 2) is the instance.

		if not pd.isnull(enviroSpec) and "Other" not in enviroSpec: 
			# Have to clean enviroSpec strings a bit
			if "treated" in enviroSpec.lower(): # For the value 'Sewage (Treated)'
				enviroSpec="treated" # Don't need redundant info
			if "water" in enviroSpec.lower():
				if enviroSpec!="Water": # EnviroSpec is "drinking water source water", 
										# "recreational water" or "core water site"
					enviroSpec=enviroSpec.replace(" water","") # Get rid of redundant info
				else:
					enviroSpec=enviro # We don't really need this as enviroSpec already
								      # equals water. But whatever ya know
			if "lagoon" in enviroSpec.lower(): # EnviroSpec is "Lagoon: Swine" or "Lagoon:Dairy"
				# Get rid of redundant info
				enviroSpec=enviroSpec.replace("Lagoon: ","") # Note the space in 'Lagoon: Swine'
				enviroSpec=enviroSpec.replace("Lagoon:","")

		else: # We know the environment type (enviro) but EnviroSpec is nan or 'Other'
			enviroSpec=enviro

		# Sand is a special case for enviro as sand is not a class but an instance of Substrate
		if "sand" in enviro.lower():
			enviro="Substrate"
			enviroSpec="sand"

	else: # We know it's an environmental source, we don't know the environment type (enviro) or the specific
		  # environment source though (enviroSpec). Note that source specific 2 is empty if source general is too.
		enviro="Environment"
		enviroSpec="unknown"
	
	title=enviroSpec # Should be unique. If there were an id for enviro sites we'd use it
	enviroTriple=campy.indTriple(title,enviro)+campy.propTriple(title,{"hasName":enviroSpec},True)
	isoTriple=campy.propTriple(isoTitle,{"hasEnvironment":title},False)

	# Insert enviroTriple
	# Insert isoTriple
	# putInOnt(enviroTriple)
	# print isoTriple
		

######################################################################################################
#
######################################################################################################
def createTypeTriples(df,row,isoTitle):
	isoTriple=""
	stTriple=""
	sampleType=df["Sample Type 2"][row]
	sourceSpec=df["Source_Specific_2"][row]

	if not pd.isnull(sampleType):
		stClass=sampleType # Retail, Abbatoir, or Faecel
		stTitle=sourceSpec # chickenBreast, carcass, rectal swab etc.

		# The column source specific 2 has a bunch of rando crap in it so we have to weed some values out
		if stTitle in ("Dairy cow","Petting Zoo","Unknown","Other","Wild","Domestic","Shore Bird","Long Legged","Meat"):
			stTitle="unknown"+stClass 

		if "non_seasoned" in stTitle: # 'seasoned' alone isn't found in the csv
			stTriple+=campy.propTriple(stTitle,{"isSeasoned":"false"},True,rLiteral=True)
		if "skin" in stTitle:
			if "skinless" in stTitle:
				stTitle=stTitle.replace("_skinless","")
				stTriple+=campy.propTriple(stTitle,{"isSkinless":"true"},True,rLiteral=True)
			else:
				stTitle=stTitle.replace("_with_skin","")
				stTriple+=campy.propTriple(stTitle,{"isSkinless":"false"},True,rLiteral=True)
		if "rinse" in stTitle:
			stTitle=stTitle.replace("_rinse","")
			stTriple+=campy.propTriple(stTitle,{"isRinse":"true"},True,rLiteral=True)
		if "chicken" in stTitle:
			if "ground" not in stTitle:
				stTitle=stTitle.replace("chicken_","")

		stTriple+=campy.indTriple(stTitle,stClass)+campy.propTriple(stTitle,{"hasName":stTitle},True)
		# Insert stTriple
		# print stTriple
		isoTriple+=campy.propTriple(isoName,{"hasAnimalSampleType":stTitle},False)
		# Insert isoTriple
		# print isoTriple


######################################################################################################
#
######################################################################################################
def createAnimalTriples(df,row,isoTitle):
	isoTriple=""
	animalTriple=""
	domestic=""
	sourceSpec=df["Source_Specific_2"][row] # That pesky source specific 2 column
	family=cn.remPrefix(df["Source General"][row],2) # Avian, Ruminant etc.
	sex=df["Gender"][row]
	age=df["Patient D.O.B / Age"][row] # 0, , juvenile, and adult
	id=df["Animal ID"][row] # If the animal has an id, this will be its URI
	animal=cn.remPrefix(df["Source_Specific_1"][row],2) # The actual animal, eg chicken, racoon etc.

	# An animal, say chicken, will become an instance of family, and chicken. Its URI will be 
	# animal+isoTitle, unless the id is present, then this will be its URI. The names of animals
	# will be their URI

	if pd.isnull(family): # We know the source is an Animal but we don't know the family or type
						  # of animal. So it just becomes an instance of the animal class and is
						  # named 'unknown' (unless it has an id)
		family="Animal"
		animal="unknown"
	else:
		# We know the family
		if not pd.isnull(animal):
			# Handle the MiscDomestic, and MiscWild family cases
			if "Misc" in family:
				if "Wild" in family:
					domestic="false" # Can't just pass in booleans. We could and then convert it 
					                 # to a string, but rdf or whatever's booleans are of the 
					                 # form 'false' instead of 'False' 
				if "Domestic" in family:
					domestic="true"

				if animal=="Canada Goose" or animal=="Trumpeter Swan" or animal=="Mute Swan" or animal=="Bufflehead":
					family="Avian"
				else:
					family="Animal"
			else:
				# Handle the domestic type of animal cases and Domestic/Wild source_specific_2
				if animal in ("Cow","Chicken","Dog","Sheep") or sourceSpec=="Domestic":
					domestic="true"
				if animal in ("Bear","Canada Goose") or sourceSpec=="Wild":
					domestic="false"

			# There are the values goat/sheep, alpaca/llama, wild bird, small mammal, and peromyscus 
			# in Source Specific 1.
			if "Wild Bird" in animal:
				animal="unknown"
				domestic="false"
			if "/" in animal:
				animal=animal.split("/")[0]
			if "Small Mammal" in animal:
				animal="unknown"
			if "Peromyscus" in animal:
				animal="Deer Mouse"
				family="Rodent"
			if "Rattus" in animal:
				animal="Rat"
				family="Rodent"

		else:
			animal="unknown"


	# If the animal has an id, this becomes its URI
	if not pd.isnull(id):
		title=cn.cleanNum(id)
	else:
		title=animal+"_"+isoTitle

	if domestic!="":
		animalTriple+=campy.propTriple(title,{"isDomestic":domestic},True,rLiteral=True)

	if not pd.isnull(sex) and (sex[0]=="M" or sex[0]=="F"):
		animalTriple+=campy.propTriple(title,{"hasSex":sex[0]},True,rLiteral=True)

	if animal.lower()!="unknown":
		animalTriple+=campy.indTriple(title,animal)+campy.subClass(animal,family)
		
	# Handle animal age

	animalTriple+=campy.indTriple(title,family)+campy.propTriple(title,{"hasName":title},True)
	isoTriple+=campy.propTriple(isoTitle,{"hasAnimal":title},False)

	# Insert animalTriple
	# print animalTriple
	putInOnt(animalTriple)
	# Insert isoTriple
	# print isoTriple


######################################################################################################
#
######################################################################################################
def createSourceTriples(df,row,isoTitle):
	sample=df["Sample Type"][row] # animal, human or environmental (and Reference Strain)

	if sample=="Animal":
		createAnimalTriples(df,row,isoTitle)
		#createTypeTriples(df,row,isoTitle)
	elif sample=="Environmental":
		createEnviroTriples(df,row,isoTitle)
	elif sample=="Human":
		createHumanTriples(df,row,isoTitle)
	else: # ReferenceStrain
		pass

######################################################################################################
#
######################################################################################################
def createProjTriples(df,row,isoTitle):
	projTriple=""
	isoTriple=""
	proj=df["Dataset ID_1"][row]
	subproj=df["Dataset ID_2"][row]

	if not pd.isnull(proj):
		projTriple+=campy.indTriple(proj,"Project")+campy.propTriple(proj,{"hasName":proj},True)

		isoTriple+=campy.propTriple(isoTitle,{"partOfProject":proj},False)

		if not pd.isnull(subproj) and subproj!=proj:
			for c in " _":
				subproj=subproj.replace(proj+c,"") # We want to get rid of the redundant name info, eg
				                                   # we don't need CIPARS_Deckert when we already have
				                                   # CIPARS as the head project. So subproj=Deckert
			projTriple+=campy.indTriple(subproj,"SubProject")
   			projTriple+=campy.propTriple(subproj,{"hasName":subproj},True)
   			projTriple+=campy.propTriple(proj,{"hasSubproject":subproj},False)

   			isoTriple+=campy.propTriple(isoTitle,{"partOfSubProject":subproj},False)
   		# print projTriple
   		# Insert projTriple

   	if isoTriple!="":
   		pass
   		# Insert the isoTriple
   		# print isoTriple


######################################################################################################
# Get the CGF ref cluster numbers, make triples.
# Given a ref cluster x_y_z, the cluster follows the nameing convention CGF_N_x_y_x, where N is the 
# threshold. Similarly for ref clusters x and x_y.
######################################################################################################
def createClustTriples(df,row,cgfTest):
	clustTriple=""
	refClust=df["REF CLUSTER 90_95_100"][row]

	if refClust!="":
		clusters=refClust.split("_")
		c90=clusters[0]
		c95=clusters[1]
		c100=clusters[2]

		c90name="CGF_90_"+c90
		c95name="CGF_95_"+c90+"_"+c95
		c100name="CGF_100_"+c90+"_"+c95+"_"+c100

		c90Triple=lab.indTriple(c90name,"CGFcluster")+\
				  lab.propTriple(c90name,{"hasThreshold":"90","hasClustNum":c90},True,rLiteral=True)+\
				  lab.propTriple(c90name,{"hasSubCluster":c95name},False)
		c95Triple=lab.indTriple(c95name,"CGFcluster")+\
		          lab.propTriple(c95name,{"hasThreshold":"95","hasClustNum":c95},True,rLiteral=True)+\
		          lab.propTriple(c95name,{"hasSubCluster":c100name},False)
		c100Triple=lab.indTriple(c100name,"CGFcluster")+\
				   lab.propTriple(c100name,{"hasThreshold":"100","hasClustNum":c100},True,rLiteral=True)

		cgfRefTriple=lab.propTriple(cgfTest,{"hasCluster":[c90name,c95name,c100name]},False)
		clustTriple=c90Triple+c95Triple+c100Triple+cgfRefTriple
	return clustTriple


######################################################################################################
#
######################################################################################################
def createCgfTriples(df,row,isoTitle):
	# A CGF test will follow the naming convention "CGFisolateName".
	cgfTest1="cgf_"+isoTitle
	fingerprint=cn.remPrefix(df["Fingerprint"][row],2)
	legacyHexNum=cn.remPrefix(df["BIN"][row],3)
	typingLab=df["TYPING LAB"][row]

	# The file location of the cgf info and the date it was completed are stored in the same cells.
	# The values are of the form DATE FILELOC, or just DATE
	fileLoc=""
	date=""
	date_fileLoc=df["Date CGF completed"][row]
	if not pd.isnull(date_fileLoc):
		date=date_fileLoc.split(" ")[0]
		date=cn.convertDate(date)

		index=date_fileLoc.find(" ")
		if index!=-1:
			fileLoc=date_fileLoc[index+1:]

	
	cgfTriple=lab.indTriple(cgfTest1,"CGFtest")

	if fileLoc!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasFileLocation":fileLoc},True,rLiteral=True)
	if date!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasDateCompleted":date},True,rLiteral=True)
	if not pd.isnull(fingerprint):
		cgfTriple+=lab.propTriple(cgfTest1,{"hasFingerprint":fingerprint},True,rLiteral=True)

	# Note that we have hex numbers converted to strings in TripleMaker (just because the isDigit function
	# returns false on hex's (that's what we want)) because there doesn't seem to be a hex number data type 
	# in rdf or whatever. It breaks the ontology if we insert it as is
	if not pd.isnull(legacyHexNum):
		cgfTriple+=lab.propTriple(cgfTest1,{"hasLegacyHexNum":legacyHexNum},True,rLiteral=True)

	if not pd.isnull(typingLab):
		# Have to create a typing lab triple and then attach the cgf test to it
		labTriple=lab.indTriple(typingLab,"TypingLab") # labTitle is an instance of the class TypingLab
		# Right now the URI for hasName is the campy ont. URI. Gonna have to change it to a URI seperate
		# from both campy and labTest URI. WE MUST FIX THIS
		labTriple+=lab.addUri(cn.cleanString(typingLab))+" "+campy.addUri("hasName")+" \""+typingLab+"\""+" .\n"
		# Attach the lab to the cgf test
		cgfTriple+=lab.propTriple(cgfTest1,{"doneAtLab":typingLab},False)
		

	clustTriple=createClustTriples(df,row,cgfTest1)
	if clustTriple!="":
		cgfTriple+=clustTriple
	
	# Insert labTriple
	# Insert cgfTriple
	# print cgfTriple
	# Some triples have more than one URI, so we make our own using TripleMaker's 
	# helper function addUri. WE MUST FIX THIS
	isoTriple=campy.addUri(cn.cleanString(isoTitle))+" "+campy.addUri("hasLabTest")+" "+lab.addUri(cn.cleanString(cgfTest1))+" .\n"
	# Insert isoTriple
	# print isoTriple


######################################################################################################
#
######################################################################################################
def createTriples(df,row):
	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoTitle=df["Strain Name"][row]

	isoTriple=campy.indTriple(isoTitle,"Isolate")+\
		      campy.propTriple(isoTitle,{"hasIsolateName":isoTitle},True,rLiteral=True)	
	
	# print isoTriple      
	# Insert isoTriple
	
	createCgfTriples(df,row,isoTitle)

	createProjTriples(df,row,isoTitle)

	createSourceTriples(df,row,isoTitle)




######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():
	df=pd.read_csv(r"/home/student/CampyDB/2016-02-10 CGF_DB_22011_2.csv")
	#createTriples(df,117)
	
	for row in range(df["Strain Name"].count()):
		createTriples(df,row)
	"""
	with open("/home/student/CampyDB/2016-02-10 CGF_DB_22011_2.csv","r") as r:
		j=0
		for line in r:
				#We'll write only the first isolate for now 
			if j!=-1:
				dirtyVals=line.strip().split(",") 
				#excel read some stuff as \n and screwed things up a bit. so just skip over garbage
				if dirtyVals[0]=="" or dirtyVals[0]=="\n" or dirtyVals[0]=='"': 
					continue

				if j==0:
					#The names of all the CGF genes are in the first row
					cgfGenes=dirtyVals[1:41]
				i=0
				cleanVals=[]	
				for s in dirtyVals:
					# All clean values are to lower case and have all chars that screw things up 
					# changed to an under score
					cleanVals.append(c.cleanString(dirtyVals[i]))
					i+=1

				if j!=0:

					createTriples(dirtyVals,cleanVals)
			j+=1
	"""

######################################################################################################
# Main
######################################################################################################
def main():
	writeData()


if __name__=="__main__":
	main()
	






			

			
	
