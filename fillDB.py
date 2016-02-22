import TripleMaker as t
import cleanCSV as c
import csv
import pycountry
######################################################################################################
# Takes all the info from the excel campy database (2015-06-11 CGF_DB_20080.csv) 
# and turns it into triples to insert into the triple store running on blazegraph
######################################################################################################

campy=t.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#")
lab=t.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/LabTests.owl#")



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
def createHumanTriples(cvals,isoName):
	hum="human"+isoName
	hClass="Human"
	# Just create a generic human individual
	humTriple=campy.indTriple(hum,hClass)
	humTriple+=campy.hasName(hum,hum)
	gender=cvals[95]
	age=cvals[96] # This column has age and birthday in it. We'll convert the birthday to an age
	              # by taking the year the sample was taken minus the birth year (so we'll have
	              # the age of the patient when the sample was taken). But if the bday is present
				  # and the year the sample was taken is not, we'll do the current year minus the
				  # birth year. Age ranges are also in this column
	travel=cvals[108]
	country=""
	subNational=""
	# ohio__usa, ukraine, new_brunswick, alberta, cuba, and italy are the only travel
	# destinations in the csv
	if "travel" in travel:
		if "ukraine" in travel:
			country="Ukraine"
		elif "usa" in travel:
			country="United States"
			subNational="Ohio"
		elif "cuba" in travel:
			country="Cuba"
		elif "alberta" in travel:
			subNational="Alberta"
		elif "new_brunswick" in travel:
			subNational="New Brunswick"
		else:
			country="Italy"
		
		if country!="":
			ccountry=c.cleanString(country)
			coTriple=campy.indTriple(ccountry,"Country")+\
					 campy.hasName(ccountry,country)
			# Insert coTriple
			# print coTriple
			humTriple+=campy.propTriple(hum,{"traveledTo":ccountry},False)
		if subNational!="":
			cSubNational=c.cleanString(subNational)
			subTriple=campy.indTriple(cSubNational,"SubNational")+\
				      campy.hasName(cSubNational,subNational)
			# print subTriple
		 	# Insert subTriple
			humTriple+=campy.propTriple(hum,{"traveledTo":cSubNational},False)
		
	if age!="missing" and age!="not_given" and age!="": 
		if len(age)<=2: # if not a birthday or range
			pass
		else:
			if "years" in age: # Every range contains the word 'years'.
				# Most ranges are of the form age-age, but some are age++
				pass
			else: # The value is a birth day
				bday=c.convertDate(age)
				yearTaken=cvals[60]

				if yearTaken!="":
					age=int(yearTaken)-int(bday[:4])
					if age<0: # One of the patients was born in 2011,but the sample was taken in 2010
						age=0
				else:
					age=2016-int(bday[:4]) # Use todays year for the age

		humTriple+=campy.propTriple(hum,{"hasAge":str(age)},True,rLiteral=True)

	# The values m, f, and 'not given' are in the csv. We won't add the prop if it's 'not given'
	if gender!="" and gender!="not_given":
		humTriple+=campy.propTriple(hum,{"hasGender":gender},True,rLiteral=True)

	# print humTriple
	# Insert humTriple


######################################################################################################
#
######################################################################################################
def createEnviroTriples(cvals,dvals,isoName):
	enviroTriple=""
	isoTriple=""
	enviro=c.remPrefix(cvals[49],2) # Source general. Water, lagoon, sewage, sand
	enviroSpec=cvals[51] # Source Specific 2. Lagoon:Dairy, Sewage (treated) etc.
	name=dvals[51]

	if enviro!="":
		if enviro in ("lagoon","water","sewage"):
			if enviroSpec!="": 
				# Source general is the class and source specific 2 is the instance.
				# Have to clean enviroSpec strings a bit
				if "treated" in enviroSpec:
					enviroSpec="treated"
					name="Treated"
				if "other" in enviroSpec:
					enviroSpec=enviro
					name=enviro.title()
				if "water" in enviroSpec:
					if enviroSpec!="water": # EnviroSpec=="drinking water source water", "recreational water" or "core water site"
						enviroSpec=enviroSpec.replace("_water","")
						name=name.replace(" water","")
				if "lagoon" in enviroSpec: # EnviroSpec=="lagoon__swine" or "lagoon_dairy"
					enviroSpec=enviroSpec.replace("lagoon__","")
					enviroSpec=enviroSpec.replace("lagoon_","")
					name=name.replace("Lagoon:","").strip()

				title=enviroSpec
			else:
				title=enviro

			eClass=enviro.title()
		else:
			eClass="Environment"
			title=enviro+isoName

		if name=="":
			name=enviro.title()

		enviroTriple=campy.indTriple(title,eClass)+campy.hasName(title,name)
		isoTriple=campy.propTriple(isoName,{"hasEnvironment":title},False)

		# Insert enviroTriple
		# Insert isoTriple
		print enviroTriple
		print isoTriple
		

######################################################################################################
#
######################################################################################################
def createAnimalTriples(cvals,isoName):
	animalTriple=""
	domestic=""
	family=c.remPrefix(cvals[49],2) # Source General
	sourceSpec=cvals[51] # Source specific 2
	sampleType=cvals[48] # Sample Type 2

	if family=="":
		family="Unknown"
		animal="unknown"
	else:
		animal=c.remPrefix(cvals[50],2) # Source Specific 1
		if animal!="":
			# Handle the miscDomestic, and miscWild family cases
			if "misc" in family:
				if "wild" in family:
					domestic="false" # Can't just pass in booleans. We could and then convert it 
					                 # to a string, but rdf or whatever's booleans are of the 
					                 # form 'false' instead of 'False' 
				if "domestic" in family:
					domestic="true"

				family="Misc"

			else:
				# Handle the domestic type of animal cases and Domestic/Wild source_specific_2
				if animal in ("cow","chicken","dog","sheep") or sourceSpec=="domestic":
					domestic="true"
				if sourceSpec=="wild":
					domestic="false"
					
			if domestic!="":
				animalTriple+=campy.propTriple(animal,{"isDomestic":domestic},True,rLiteral=True)

			# There are the values goat/sheep, alpaca/llama, wild bird, small mammal, and peromyscus 
			# in Source Specific 1. What should we do about these????
		else:
			animal="unknown"

	# 'animal' is an instance of the class 'family'
	title=animal+isoName
	aClass=family.title()

	animalTriple+=campy.indTriple(title,aClass)+campy.hasName(title,animal)
	# Insert animalTriple
	# print animalTriple

	isoTriple=campy.propTriple(isoName,{"hasAnimal":title},False)

	if sampleType!="":
		stTriple=""
		stClass=sampleType.title() # Retail, Abbatoir, or Faecel
		stTitle=sourceSpec # chickenBreast, carcass, rectal swab etc.

		if stTitle in ("","dairy_cow","petting_zoo","unknown","other","wild","domestic","shore_bird","long_legged","meat"):
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

		stTriple+=campy.indTriple(stTitle,stClass)+campy.hasName(stTitle,stTitle)
		isoTriple+=campy.propTriple(isoName,{"hasAnimalSampleType":stTitle},False)
		# Insert typeTriple
		# print stTriple

	# Insert isoTriple
	# print isoTriple


######################################################################################################
#
######################################################################################################
def createSourceTriples(cvals,dvals,isoName):
	sample=cvals[47] # animal, human or environmental (Reference strain is also found in this column)

	if sample=="animal":
		createAnimalTriples(cvals,isoName)
	elif sample=="environmental":
		createEnviroTriples(cvals,dvals,isoName)
	elif sample=="human":
		createHumanTriples(cvals,isoName)
	else: # ReferenceStrain
		pass

######################################################################################################
#
######################################################################################################
def createProjTriples(cvals,dvals,isoName):
	proj=cvals[45]
	projName=dvals[45]
	subproj=cvals[46]
	projTriple=""
	isoTriple=""

	if proj!="":
		projTriple+=campy.indTriple(proj,"Project")+campy.hasName(proj,dvals[45])

		isoTriple+=campy.propTriple(isoName,{"partOfProject":proj},False)

		if subproj!="" and subproj!=proj:
			for c in " _":
				subproj=subproj.replace(proj+c,"")
				subprojName=dvals[46].replace(projName+c,"")
   			projTriple+=campy.hasName(subproj,subprojName)
   			projTriple+=campy.propTriple(proj,{"hasSubproject":subproj},False)

   			isoTriple+=campy.propTriple(isoName,{"partOfSubProject":subproj},False)

   	if isoTriple!="":
   		pass
   		# Insert the isoTriple
   		# print isoTriple


######################################################################################################
# Get the CGF ref cluster numbers, make triples.
# Given a ref cluster x_y_z, the cluster follows the nameing convention CGF_N.x.y.x, where N is the 
# threshold. Similarly for ref clusters x and x_y.
######################################################################################################
def createClustTriples(cvals,cgfTest):
	clustTriple=""
	if cvals[43]!="":
		clusters=cvals[43].split("_")
		c90=clusters[0]
		c95=clusters[1]
		c100=clusters[2]

		c90name="CGF_90."+c90
		c95name="CGF_95."+c90+"."+c95
		c100name="CGF_100."+c90+"."+c95+"."+c100

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
def createCgfTriples(cvals,isoName):
	# A CGF test will follow the naming convention "CGFisolateName".
	cgfTest1="CGF"+isoName
	fingerprint="".join(cvals[1:41])
	legacyHexNum=c.remPrefix(cvals[41],3)
	typingLab=cvals[44]
	cgfDate=c.convertDate(cvals[110])

	# Note that hex numbers need to be passed in as strings because there doesn't seem to be a hex number 
	# data type in rdf or whatever. It breaks the ontology if we insert it as is
	cgfTriple=lab.indTriple(cgfTest1,"CGFtest")
	if fingerprint!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasFingerprint":fingerprint},True,rLiteral=True)
	if legacyHexNum!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasLegacyHexNum":"\""+legacyHexNum+"\""},True,rLiteral=True)
	if cgfDate!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasDateCompleted":"\""+cgfDate+"\""},True,rLiteral=True)
	if typingLab!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"doneAtLab":typingLab},False)
		cgfTriple+=lab.addUri(typingLab)+" "+campy.addUri("hasName")+" \""+typingLab+"\" .\n"

	clustTriple=createClustTriples(cvals,cgfTest1)
	if clustTriple!="":
		cgfTriple+=clustTriple

	if cgfTriple!="":
		# Insert cgfTriple
		# print cgfTriple
		# Some triples have more than one URI, so we make our own using TripleMaker's 
		# helper function addUri
		isoTriple=campy.addUri(isoName)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(cgfTest1)+" .\n"
		# Insert isoTriple
		# print isoTriple
	

######################################################################################################
#
######################################################################################################
def createTriples(dvals,cvals):
	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoName=cvals[0].lower()
	isoTriple=campy.indTriple(isoName,"Isolate")+\
		      campy.propTriple(isoName,{"hasIsolateName":"\""+dvals[0]+"\""},True,rLiteral=True)	      
	# Insert isoTriple
	
	createCgfTriples(cvals,isoName)

	createProjTriples(cvals,dvals,isoName)

	createSourceTriples(cvals,dvals,isoName)




######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():
	with open('/home/student/CampyDB/2015-06-11 CGF_DB_20080.csv','r') as r:
		j=0
		for line in r:
				#We'll write only the first isolate for now 
			if j!=-1:
				dirtyVals=line.strip().split(",") 
				#excel read some stuff as \n and screwed things up a bit. so just skip over garbage
				if dirtyVals[0]=='' or dirtyVals[0]=='\n' or dirtyVals[0]=='"': 
					continue

				if j==0:
					#The names of all the CGF genes are in the first row
					cgfGenes=dirtyVals[1:41]
				i=0
				cleanVals=[]	
				for s in dirtyVals:
					# All clean values are to lower case and have all chars that screw things up 
					# changed to the _ character
					cleanVals.append(c.cleanString(dirtyVals[i]))
					i+=1

				if j!=0:
					createTriples(dirtyVals,cleanVals)
			j+=1

######################################################################################################
# Main
######################################################################################################
def main():
	writeData()

	
if __name__=="__main__":
	main()
	






			

			
	
