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
	# Just create a generic human individual
	humTriple=campy.indTriple(hum,"Human")
	humTriple+=campy.propTriple(hum,{"hasName":"\""+hum+"\""},True)
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
					 campy.propTriple(ccountry,{"hasName":"\""+country+"\""},True)
			# Insert coTriple
			print coTriple
			humTriple+=campy.propTriple(hum,{"traveledTo":ccountry},False)
		if subNational!="":
			cSubNational=c.cleanString(subNational)
			subTriple=campy.indTriple(cSubNational,"SubNational")+\
				      campy.propTriple(cSubNational,{"hasName":"\""+subNational+"\""},True)
			print subTriple
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

	print humTriple
	# Insert humTriple


######################################################################################################
#
######################################################################################################
def createEnviroTriples(cvals,isoName):
	enviroTriple=""
	isoTriple=""
	#sourceSpec=cvals[51]
	enviro=c.remPrefix(cvals[49],2)+isoName

	if enviro!="":
		enviroTriple=campy.indTriple(enviro,"Environment")
		enviroTriple+=campy.propTriple(enviro,{"hasName":"\""+enviro+"\""},True)
		isoTriple=campy.propTriple(isoName,{"hasEnvironment":enviro},False)
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
	family=c.remPrefix(cvals[49],2)
	sourceSpec=cvals[51]
	sampleType=cvals[48]

	if family=="":
		family="Unknown"
		animal="unknown"
	else:
		animal=c.remPrefix(cvals[50],2)+isoName
		if animal!="":
			# Handle the miscDomestic, and miscWild family cases
			if "misc" in family:
				if "wild" in family:
					domestic="false" # Can't just pass in booleans. We could and then convert it 
					                 # to a string, but rdf or whatever's booleans are of the 
					                 # form false instead of False 
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
			# What should we do about these????
		else:
			animal="unknown"

	# animal is an instance of the class family
	animalTriple+=campy.indTriple(animal,family.title())+\
				  campy.propTriple(animal,{"hasName":"\""+animal+"\""},True)
	# Insert animalTriple
	print animalTriple

	isoTriple=campy.propTriple(isoName,{"hasAnimal":animal},False)

	if sampleType!="":
		isoTriple+=campy.propTriple(isoName,{"hasAnimalSampleType":sampleType},False)
		typeTriple=campy.propTriple(sampleType,{"hasName":"\""+sampleType+"\""},True)
		# Insert typeTriple
		print typeTriple

	# Insert isoTriple
	print isoTriple


######################################################################################################
#
######################################################################################################
def createSourceTriples(cvals,dvals,isoName):
	sample=cvals[47] # animal, human or environmental (Reference strain is also found in this column)

	if sample=="animal":
		createAnimalTriples(cvals,isoName)
	elif sample=="environmental":
		createEnviroTriples(cvals,isoName)
	elif sample=="human":
		createHumanTriples(cvals,isoName)
	else: # ReferenceStrain
		pass

######################################################################################################
#
######################################################################################################
def createProjTriples(cvals,dvals,isoName):
	proj=cvals[45]
	subproj=cvals[46]
	projTriple=""
	isoTriple=""
	if proj!="":
		projTriple+=campy.indTriple(proj,"Project")+\
					campy.propTriple(proj,{"hasName":"\""+dvals[45]+"\""},True)

		isoTriple+=campy.propTriple(isoName,{"partOfProject":proj},False)

		if subproj!="" and subproj!=proj:
			for c in " _":
				subproj=subproj.replace(proj+c,"")
				subprojName=dvals[46].replace(proj+c,"")
   			projTriple+=campy.propTriple(subproj,{"hasName":"\""+subprojName+"\""},True)
   			projTriple+=campy.propTriple(proj,{"hasSubproject":subproj},False)

   			isoTriple+=campy.propTriple(isoName,{"partOfSubProject":subproj},False)

   	if isoTriple!="":
   		pass
   		# Insert the isoTriple
   		print isoTriple


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
		print cgfTriple
		# Some triples have more than one URI, so we make our own using TripleMaker's 
		# helper function addUri
		isoTriple=campy.addUri(isoName)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(cgfTest1)+" .\n"
		# Insert isoTriple
		print isoTriple
	

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
			if j<10:
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
	






			

			
	
