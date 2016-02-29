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

	isoTriple=campy.propTriple(isoTitle,{"hasSampleSource":hum},False)


	return humTriple+isoTriple


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
		  # environment source (enviroSpec). Note that source specific 2 is empty if source general is too.
		enviro="Environment"
		enviroSpec="unknown"
	
	title=enviroSpec # Should be unique. If there were an id for enviro sites we'd use it
	enviroTriple=campy.indTriple(title,enviro)+campy.propTriple(title,{"hasName":enviroSpec},True)
	isoTriple=campy.propTriple(isoTitle,{"hasSampleSource":title},False)

	return enviroTriple+isoTriple
		

######################################################################################################
#
######################################################################################################
def createTypeTriples(df,row,isoTitle):
	isoTriple=""
	stTriple=""
	title=""
	sampleType=df["Sample Type 2"][row] # Faecel, Abbatoir, Retail, Egg
	sourceSpec=df["Source_Specific_2"][row] # chickenBreast, carcass, rectal swab etc.

	if not pd.isnull(sampleType) and sampleType!="Insect": # Insects don't have sample types
		sampleType=sampleType.lower()

		if not pd.isnull(sourceSpec):
			sourceSpec=sourceSpec.lower()

			title=sampleType # The name of the sample type is just the sample type name
						     # unless there is something more specific in source specific 2

			title="breast" if "breast" in sourceSpec else title
			title="thigh" if "thigh" in sourceSpec else title
			title="caecum" if "caecum" in sourceSpec else title
			title="carcass" if "carcass" in sourceSpec else title
			title="ground" if "ground" in sourceSpec else title
			title="loin" if "loin" in sourceSpec else title
			title="dropping" if "field sample" in sourceSpec else title
			title="pit" if "pit" in sourceSpec else title
			title="swab" if "swab" in sourceSpec else title
			title="weep" if "weep" in sourceSpec else title

			if title=="breast" or title=="thigh" or title=="ground" or title=="loin":
				stTriple+=campy.indTriple(title+"_"+isoTitle,"Meat")

			title+="_"+isoTitle
			name=title
			stTriple+=campy.propTriple(title,{"hasName":name},True)
	
			# sourceSpec has info related to the properties of meat.
			if "seasoned" in sourceSpec: 
				stTriple+=campy.propTriple(title,{"isSeasoned":"false"},True,rLiteral=True)

			if "skin" in sourceSpec:
				if "skinless" in sourceSpec:
					stTriple+=campy.propTriple(title,{"isSkinless":"true"},True,rLiteral=True)
				else:
					stTriple+=campy.propTriple(title,{"isSkinless":"false"},True,rLiteral=True)
			if "rinse" in sourceSpec:
				stTriple+=campy.propTriple(title,{"isRinse":"true"},True,rLiteral=True)

		else: # sourceSpec is nan
			name=sampleType
			title=sampleType+"_"+isoTitle # faecal, abattoir, retail, egg


		stClass=sampleType+"Type"
		stTriple+=campy.indTriple(title,stClass)

		isoTriple+=campy.propTriple(isoTitle,{"hasSampleType":title},False)

	return stTriple+isoTriple


######################################################################################################
#
######################################################################################################
def createAnimalTriples(df,row,isoTitle):
	isoTriple=""
	animalTriple=""
	domestic=""
	taxoGenus="" # Some of the animals have taxo info (eg peromyscus)
	sourceSpec=df["Source_Specific_2"][row] # That pesky source specific 2 column
	family=cn.remPrefix(df["Source General"][row],2) # Avian, Ruminant etc.
	sex=df["Gender"][row]
	age=df["Patient D.O.B / Age"][row] # 0, , juvenile, and adult
	id=df["Animal ID"][row] # If the animal has an id, this will be its URI
	animal=cn.remPrefix(df["Source_Specific_1"][row],2) # The actual animal, eg chicken, racoon etc.
	ageRank=df["Patient D.O.B / Age"][row] # Juvenile, Adult

	# An animal, say chicken, will become an instance of Family, and Chicken, for example. Then
	# Chicken will become a subclass of Family. The individuals URI will be animal+isoTitle, unless 
	# the id is present, then this will be its URI. 

	if pd.isnull(family): # We know the source is an Animal but we don't know the family or type
						  # of animal. So it just becomes an instance of the animal class and is
						  # named 'unknown' (unless it has an id)
		animal="unknown"
		family="Misc"
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

				# Give families do all the MiscWild and MiscDomestic animals
				if "Canada Goose" in animal or "Trumpeter Swan" in animal or \
				   "Mute" in animal or "Bufflehead" in animal or "Scaup" in animal or\
				   "Merganser" in animal:
					family="Avian"
				elif "Small Mammal" in animal:
					animal="unknown"
					family="Misc"
				elif "Peromyscus" in animal:
					animal="Deer Mouse"
					family="Rodent"
					taxoGenus="peromyscus"
				elif "Rattus" in animal:
					animal="Rat"
					family="Rodent"
					taxoGenus="Rattus"
				elif "Marmot" in animal:
					family="Rodent"
				elif "Unknown" in animal:
					family="Misc"
					animal="unknown"
				else: # racoons, skunks, and llama/alpaca
					family="Misc"
			
			# Handle the domestic type of animal cases
			if animal in ("Cow","Chicken","Dog","Sheep"):
				domestic="true"
			# Handle the wild type of animal cases
			if animal in ("Bear","Canada Goose"): 
				domestic="false"

			# There are the values Wild Bird, goat/sheep, alpaca/llama in source specific 1
			if "Wild Bird" in animal:
				animal="unknown" # Wild bird has the family avian
				domestic="false"
			if "/" in animal:
				animal=animal.split("/")[0]

			# Source Specific 2 has more specific animals sometimes and also domestic/wild info
			if not pd.isnull(sourceSpec):
				sourceSpec=sourceSpec.lower()

				if "domestic" in sourceSpec:
					domestic="true"
				if "wild" in sourceSpec:
					domestic="false"

				# The value Heifer is in source specific 2 for values of cow in source specific 1.
				# This is more specific than cow so Heifer will become a subclass of Cow
				if "heifer" in sourceSpec:
					animal="heifer"
					family="Cow"
					animalTriple+=campy.subClass(family,"Ruminant") # Cow is subclass of Ruminant

				# Dairy cow is more specific than just a cow so Dairy Cow becomes a subclass
				# of cow. DAIRY, Dairy Cow, and Dairy Manure are found in source specific 2
				if "dairy" in sourceSpec:
					animal="dairy cow"
					family="Cow"
					animalTriple+=campy.subClass(family,"Ruminant") # Cow is subclass of Ruminant

				if "shore bird" in sourceSpec:
					animal="shore bird"

		else: # We know the family but not the animal
			animal="unknown"

	# If the animal has an id, this becomes its URI
	if not pd.isnull(id):
		title=cn.cleanNum(id)
	else:
		title=animal+"_"+isoTitle

	if not pd.isnull(sex) and (sex[0]=="M" or sex[0]=="F"):
		animalTriple+=campy.propTriple(title,{"hasSex":sex[0]},True,rLiteral=True)

	# The values 0 and unknown were in the csv for this column
	if not pd.isnull(ageRank) and ("juvenile" in ageRank or "adult" in ageRank):
		animalTriple+=campy.propTriple(title,{"hasAgeRank":ageRank},True,rLiteral=True)		
		
	if domestic!="":
		animalTriple+=campy.propTriple(title,{"isDomestic":domestic},True,rLiteral=True)

	if animal!="unknown":
		# animal becomes an instance of animal, and animal becomes a subclass of family
		animalTriple+=campy.indTriple(title,animal)+campy.subClass(animal,family)

	if taxoGenus!="":
		animalTriple+=campy.propTriple(title,{"hasTaxoGenus":taxoGenus},True,rLiteral=True)


	animalTriple+=campy.indTriple(title,family)

	isoTriple+=campy.propTriple(isoTitle,{"hasSampleSource":title},False)


	return animalTriple+isoTriple

######################################################################################################
#
######################################################################################################
def createLocationTriples(df,row,isoTitle):
	locationTriple=""
	country=df["Country"][row]
	subNat=df["Province/State"][row]
	city=df["City"][row]
	hAuthority=df["Region_L1"][row]
	samplingSite=df["Region_L2"][row]
	samplingSite2=df["Source_Specific_2"][row] # Petting zoo is in this col, and we consider it to be
										       # a sampling site
	c_netSite=df["C-EnterNet Site"][row]
	fncSite=df["FNC Sentinel Site"][row]
	long=df["Longitude"][row]
	lat=df["Latitude"][row]

	# Need this for the body of water location.
	water=df["Sample Type 2"][row]
	if not pd.isnull(water) and "Water" in water:
		bodyOfWater=df["Sample Source"][row]
		if not pd.isnull(bodyOfWater):
			bodyOfWater=cn.remPrefix(bodyOfWater,2)

			if "Oldman River Watershed" in bodyOfWater: # A watershed is a region
				locationTriple+=campy.indTriple(bodyOfWater,"Region")
				locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":bodyOfWater},False)
				locationTriple+=campy.propTriple(bodyOfWater,{"hasName":bodyOfWater},True)

			# For whatever bloody reason the names of health authorities and cities
			# are in this column for values of water in column sample type 2. The
			# sumas and salmon rivers are the only bodies of water not repeated.
			if "Sumas" in bodyOfWater or "Salmon" in bodyOfWater:
				locationTriple+=campy.indTriple(bodyOfWater,"BodyOfWater")
				locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":bodyOfWater},False)
				locationTriple+=campy.propTriple(bodyOfWater,{"hasName":bodyOfWater},True)



	# SamplingSite is a real mess. Has a lot of redundant information. Also, some of them
	# have city info (Fort Mcleod)
	if not pd.isnull(samplingSite):
		if "Mcleod" in samplingSite or "Macleod" in samplingSite:
			city="Fort Mcleod"
		locationTriple+=campy.indTriple(samplingSite,"SamplingSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":samplingSite},False)
		locationTriple+=campy.propTriple(samplingSite,{"hasName":samplingSite},True)

	if not pd.isnull(country):
		locationTriple+=campy.indTriple(country,"Country")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":country},False)
		locationTriple+=campy.propTriple(country,{"hasName":country},True)

	if not pd.isnull(subNat):
		locationTriple+=campy.indTriple(subNat,"SubNational")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":subNat},False)
		locationTriple+=campy.propTriple(subNat,{"hasName":subNat},True)

	if not pd.isnull(city):
		locationTriple+=campy.indTriple(city,"City")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":city},False)
		locationTriple+=campy.propTriple(city,{"hasName":city},True)

	if not pd.isnull(hAuthority):
		hAuthority=cn.remPrefix(hAuthority,3)
		locationTriple+=campy.indTriple(hAuthority,"HealthAuthority")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":hAuthority},False)
		locationTriple+=campy.propTriple(hAuthority,{"hasName":hAuthority},True)

	if not pd.isnull(samplingSite2) and ("Petting Zoo" in samplingSite2):
		locationTriple+=campy.indTriple(samplingSite2,"SamplingSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":samplingSite2},False)
		locationTriple+=campy.propTriple(samplingSite2,{"hasName":samplingSite2},True)

	if not pd.isnull(c_netSite):
		c_netSite=str(c_netSite) # Some are numbers in the csv
		locationTriple+=campy.indTriple(c_netSite,"C_EnterNetSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":c_netSite},False)
		locationTriple+=campy.propTriple(c_netSite,{"hasName":c_netSite},True)

	if not pd.isnull(fncSite):
		locationTriple+=campy.indTriple(fncSite,"FNCSentinelSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":fncSite},False)
		locationTriple+=campy.propTriple(fncSite,{"hasName":fncSite},True)


	# Have to convert lat and long to signed decimal format
	if not pd.isnull(long) and not pd.isnull(lat): # lat is never nan when long is and vice versa
		 # For some reason the lat and long values in the csv have some newline chars in them
		lat=lat.strip()
		long=long.strip()
		lat=cn.convertGPS(lat)
		long=cn.convertGPS(long)

		locationTriple+=campy.propTriple(isoTitle,{"hasLatitude":lat},True,rLiteral=True)
		locationTriple+=campy.propTriple(isoTitle,{"hasLong":long},True,rLiteral=True)

	putInOnt(locationTriple)
	return locationTriple


######################################################################################################
#
######################################################################################################
def createSourceTriples(df,row,isoTitle):
	result=createLocationTriples(df,row,isoTitle)

	sample=df["Sample Type"][row] # animal, human or environmental (and Reference Strain)

	if sample=="Animal":
		result=createAnimalTriples(df,row,isoTitle)
		result+=createTypeTriples(df,row,isoTitle)
	elif sample=="Environmental":
		result=createEnviroTriples(df,row,isoTitle)
	elif sample=="Human":
		result=createHumanTriples(df,row,isoTitle)
	else: # ReferenceStrain
		pass

	return result

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

   	return isoTriple+projTriple


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
	labTriple=""
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

	# Every isolate has a cgf test
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
	
	# Some triples have more than one URI, so we make our own using TripleMaker's 
	# helper function addUri. WE MUST FIX THIS
	isoTriple=campy.addUri(cn.cleanString(isoTitle))+" "+campy.addUri("hasLabTest")+" "+lab.addUri(cn.cleanString(cgfTest1))+" .\n"

	return labTriple+cgfTriple+isoTriple


######################################################################################################
#
######################################################################################################
def createTriples(df,row):
	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoTitle=df["Strain Name"][row]

	isoTriple=campy.indTriple(isoTitle,"Isolate")+\
		      campy.propTriple(isoTitle,{"hasIsolateName":isoTitle},True,rLiteral=True)		     

	isoTriple+=createCgfTriples(df,row,isoTitle)

	isoTriple+=createProjTriples(df,row,isoTitle)

	isoTriple+=createSourceTriples(df,row,isoTitle)

	#insert isoTriple


######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():
	df=pd.read_csv(r"/home/student/CampyDB/2016-02-10 CGF_DB_22011_2.csv")
	#createTriples(df,16598)
	#range(df["Strain Name"].count())
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
	






			

			
	
