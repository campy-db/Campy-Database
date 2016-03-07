# -*- coding: latin-1 -*-
import TripleMaker as tm
import endpoint as e
import cleanCSV as cn
import pandas as pd
import re
import pycountry as pc
from datetime import date
######################################################################################################
# Takes all the info from the excel campy 'database' and turns it into triples to insert into a triple 
# store running on blazegraph
######################################################################################################

######################################################################################################
# Global variables
######################################################################################################
subNats=[x.name for x in list(pc.subdivisions)] # A list of names of subnationals
countries=[x.name for x in list(pc.countries)] # A list of names of countries

# Use the campy ontology's URI for some triples
campy=\
tm.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/CampyOntology2.0.owl#")
# The labtests need the lab test URI
lab=tm.TripleMaker("https://github.com/samuel-peers/campyOntology/blob/master/LabTests.owl#")

######################################################################################################
# putInOnt
# Just throws the triples into the owl file. Just for testing purposes. Later the triples will be 
# insterted into blazegraph.
######################################################################################################
def putInOnt(t):
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
# getHex
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
# createAgeTriples
# Some patients in the csv have ages. The values are found in the 'Patient D.O.B / Age' column. 
# The column has birthdates, ages, and age ranges of the form 'a/X-Y years' where X and Y are ages
# and a is some random character. As of right now, we ignore ranges in hopes that Steven can get the
# actual ages.
######################################################################################################
def createAgeTriples(df,row,hum):
	humTriple=""
	yearLen=4
	ageLen=2
	age=df["Patient D.O.B / Age"][row]
	yearTaken=cn.cleanInt(df["YEAR"][row]) # The year values are converted to floats for some reason
										   # in the csv. We convert it to a string
	if not pd.isnull(age) and cn.isGoodVal(age): 
		if len(age)>ageLen: # if a birthday or range
			if "years" in age: # Every range contains the word 'years'.
				# Most ranges are of the form age-age, but some are age+
				age="" # Ignore ranges for now
			else: # The value is a birth day
				bday=cn.convertDate(age)
				humTriple+=campy.propTriple(hum,{"hasBirthDate":bday},True,rLiteral=True)
				
				if not pd.isnull(yearTaken):
					age=int(yearTaken)-int(bday[:yearLen]) # bday is in ISO format, so the first 4
													       # chars is the year of the bday
					if age<0: # One of the patients was born in 2011,but the sample was taken in 2010
						age=0
				else:
					age=date.today().year-int(bday[:yearLen]) # Use todays year for the age

		humTriple+=campy.propTriple(hum,{"hasAge":str(age)},True,rLiteral=True) if age!="" else ""	

	return humTriple

######################################################################################################
# createTravelTriples
# A patient's travel info is in column 'Comments' and is of the form 'Travel: [location]'. Sometimes
# it's just the country, or the province/state, or both. We will store only the lowest level. eg
# from the location value 'Ohia, USA' we will store only Ohio as it is derivable that the patient
# traveled to the states.
######################################################################################################
def createTravelTriples(df,row,hum):
	humTriple=""
	trTriple="" # Travel info triple
	travel=df["Comments"][row] # All travel info is in the comments column
	
	# We will keep the lowest level of ganularity, eg from 'Ohio, USA' we'll keep only Ohio as USA
	# is derivable (consider revising).

	if not pd.isnull(travel) and "Travel" in travel: # All travel values are prefixed with 'Travel: '
		travel=travel.replace("Travel:","").strip() # Remove the 'Travel:' prefix

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
# createHumanTriples
# Create an individual human for all isolates that have a human as a source. No names are given so
# the unique id for humans is 'patient_[isoTitle]'. Note all humans in the csv are patients so they
# will be instances of the Patient class. Here we will also get the properties postal code if 
# available and gender if available. We also get set the clinical sample type here.
######################################################################################################
def createHumanTriples(df,row,isoTitle):
	type=""
	isoTriple=""
	hum="patient_"+isoTitle # Need a unique identifier for humans as they have different 
						    # ages, genders, and postal codes I'm told
	gender=df["Gender"][row]
	postalCode=df["Postal code"][row]
	sTypeA=df["Source_Specific_2"][row] # The clinical sample type
	sTypeB=df["Clinical Sample Type"][row] # Also has clinical sample typ

	# Just create a generic human individual
	humTriple=campy.indTriple(hum,"Patient") # All human samples in the csv are patients
	humTriple+=campy.propTriple(hum,{"hasName":hum},True)

	# Travel info is in the column 'comments' and it's quite messy so we'll
	# handle it separately 
	humTriple+=createTravelTriples(df,row,hum)

	# The age is stored in a column with birthdays and other random crap so we'll 
	# handle it separately
	humTriple+=createAgeTriples(df,row,hum)

	# The values 0, m, f, male, female and 'not given' are in the csv. We won't add the prop if 
	# it's 'not given'
	if not pd.isnull(gender) and cn.isGoodVal(gender) and gender!=0:
		humTriple+=campy.propTriple(hum,{"hasGender":gender[0]},True,rLiteral=True)

	if not pd.isnull(postalCode):
		humTriple+=campy.propTriple(hum,{"hasPostalCode":postalCode},True,rLiteral=True)

	# If sTypeA is nan, try sTypeB
	typeCol=sTypeA if not pd.isnull(sTypeA) else sTypeB

	if not pd.isnull(typeCol) and cn.isGoodVal(typeCol):
		if re.search("[Ss]tool",typeCol) is not None:
			type="stool"
		if re.search("[Bl]ood",typeCol) is not None:
			type="blood"

	 # type could still be "" as not all the values for sTypeA (Source_Specific_2) are 
	 # clinical sample types, i.e. 'blood' or 'stool'
	if type!="":
		isoTriple+=campy.indTriple(type,"ClinicalType")
		isoTriple+=campy.propTriple(type,{"hasName":type},True)
		isoTriple+=campy.propTriple(isoTitle,{"hasSampleType":type},False)
		
	isoTriple+=campy.propTriple(isoTitle,{"hasSampleSource":hum},False)

	return humTriple+isoTriple


######################################################################################################
# createEnviroTriples
# Creates an instance of Environment for every isolate that has an environmental source type. We don't
# bother uniquely identifying different environment sources; this is just so the user knows what type
# of environment the source came from. We would consider revising this if enviro sources had an ID. 
# Though really the enviro's unique ID is the sampling site name or body of water name which we fetch
# in the function createLocation triples.
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

	if not pd.isnull(enviro) and cn.isGoodVal(enviro):
		# enviro (Source general) is the class and enviroSpec (source specific 2) is the instance.

		if not pd.isnull(enviroSpec) and "Other" not in enviroSpec: 
			# Have to clean enviroSpec strings a bit
			if re.search("[Tt]reated",enviroSpec) is not None: # For the value 'Sewage (Treated)'
				enviroSpec="treated" # Don't need redundant info
			if "water" in enviroSpec.lower():
				if enviroSpec!="Water": # EnviroSpec is "drinking water source water", 
										# "recreational water" or "core water site"
					enviroSpec=enviroSpec.replace(" water","") # Get rid of redundant info
				else:
					enviroSpec=enviro # We don't really need this as enviroSpec already
								      # equals water. But whatever ya know
			if re.search("[Ll]agoon",enviroSpec) is not None: # EnviroSpec is "Lagoon: Swine" or "Lagoon:Dairy"
				# Get rid of redundant info
				enviroSpec=enviroSpec.replace("Lagoon:","")

		else: # We know the environment type (enviro) but EnviroSpec is nan or 'Other'
			enviroSpec=enviro

		# Sand is a special case for enviro as sand is not a class but an instance of Substrate
		if re.search("[Ss]and",enviro) is not None:
			enviro="Substrate"
			enviroSpec="sand"

	else: # We know it's an environmental source, we don't know the environment type (enviro) or the specific
		  # environment source (enviroSpec). Note that source specific 2 is empty if source general is too.
		enviro="Environment"
		enviroSpec="unknown"
	
	title=enviroSpec # Doesn't need to be unique; there are no props attached to evironments. 
	enviroTriple=campy.indTriple(title,enviro)+campy.propTriple(title,{"hasName":enviroSpec},True)
	isoTriple=campy.propTriple(isoTitle,{"hasSampleSource":title},False)

	return enviroTriple+isoTriple
		

######################################################################################################
# createTypeTriples
# Here we create instances of the AnimalType class. Again we don't use unique identifiers as the user
# probably needs to only know the type of sample. I wish we could just say :isoC1007 :hasSampeType 
# "faecal", but there are different kinds of faecal samples, like droppings, and swab. Also, some 
# sampletypes have properties attached to them so that further complicates things, just a bit though.
######################################################################################################
def createTypeTriples(df,row,isoTitle):
	isoTriple=""
	stTriple=""
	title=""
	sampleType=df["Sample Type 2"][row] # Faecel, Abbatoir, Retail, Egg
	sourceSpec=df["Source_Specific_2"][row] # chickenBreast, carcass, rectal swab etc.

	 # Insects don't have sample types
	if not pd.isnull(sampleType) and cn.isGoodVal(sampleType) and sampleType!="Insect":
		sampleType=sampleType.lower()

		if not pd.isnull(sourceSpec):
			sourceSpec=sourceSpec.lower()

			title=sampleType # The name of the sample type is just the sample type name
						     # unless there is something more specific in source specific 2

			# The source specific 2 for animal sample types is really messy. It's just
			# easier to hard code values in
			title="breast" if "breast" in sourceSpec else title
			title="thigh" if "thigh" in sourceSpec else title
			title="caecum" if "caecum" in sourceSpec else title
			title="carcass" if "carcass" in sourceSpec else title
			title="ground" if "ground" in sourceSpec else title
			title="loin" if "loin" in sourceSpec else title
			title="droppings" if "field sample" in sourceSpec else title
			title="pit" if "pit" in sourceSpec else title
			title="swab" if "swab" in sourceSpec else title
			title="weep" if "weep" in sourceSpec else title
	
			name=title

			if title!=sampleType:
				title=sampleType+"_"+title

			# sourceSpec has info related to the properties of meat.
			if "seasoned" in sourceSpec:
				title=sampleType+"_seasoned_"+name
				stTriple+=campy.propTriple(title,{"isSeasoned":"false"},True,rLiteral=True)

			if "skin" in sourceSpec:
				if "skinless" in sourceSpec:
					title=sampleType+"_skinless_"+name
					stTriple+=campy.propTriple(title,{"isSkinless":"true"},True,rLiteral=True)
				else:
					title=sampleType+"_"+name+"_withskin"
					stTriple+=campy.propTriple(title,{"isSkinless":"false"},True,rLiteral=True)
			if "rinse" in sourceSpec:
				title=sampleType+"_"+name+"_rinse"
				stTriple+=campy.propTriple(title,{"isRinse":"true"},True,rLiteral=True)


			if "breast" in title or "thigh" in title or "ground" in title or "loin" in title:
				stTriple+=campy.indTriple(title,"Meat")

			stTriple+=campy.propTriple(title,{"hasName":name},True)

		else: # sourceSpec is nan
			name=sampleType
			title=sampleType # faecal, abattoir, retail, egg

		stClass=sampleType+"Type"
		stTriple+=campy.indTriple(title,stClass)

		isoTriple+=campy.propTriple(isoTitle,{"hasSampleType":title},False)

	return stTriple+isoTriple

######################################################################################################
# createAnimalTriples
# Creates instances of the Animal class for every isolate that has an animal as a source. Here we do
# uniquely identify animals as there is an animal id provided in the good 'ole csv. Not all animals
# have an id though so we name those ones [animel]_[isoTitle] where animal is the kind of animal, eg
# chicken. Note we create new classes here for every type of animal and the new class becomes a
# subclass of its respective family. eg chicken_C1007 is an instance of Chicken, and Chicken is set as 
# a sublass of Avian. Sometimes we know the source is an animal but we don't the family or animal. In
# this case we say the animal type is unknown and it just becomes an instance of the Misc class. 
# Sometimes we the family but not the animal type in which case unknown is an instance of family. When
# we do knoe the animal type, there are properties attached to animals found all over the csv and many
# , nice to work with, totally random cases we have to handle.
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
		if not pd.isnull(animal) and cn.isGoodVal(animal):
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
	if not pd.isnull(id) and cn.isGoodVal(id):
		title=cn.cleanInt(id)
	else:
		title=animal+"_"+isoTitle

	if not pd.isnull(sex) and cn.isGoodVal(sex) and (sex[0]=="M" or sex[0]=="F"):
		animalTriple+=campy.propTriple(title,{"hasSex":sex[0]},True,rLiteral=True)

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
# createLocationTriples
# Gets all the info of where we got the isolate sample. 
# NOTE - Right now all values in the column Region_L1 are assumed to be health authorities. This is
#	     incorrect. Some are municipalities. This must be fixed!!!!
# We can find the watershed and the body of water the isolate came from in column Sample Source. The
# only bodies of water are the Sumas and Salmon river.
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
	lng=df["Longitude"][row]
	lat=df["Latitude"][row]

	# Need this for the body of water location and watersheds
	water=df["Sample Type 2"][row]
	if not pd.isnull(water) and "Water" in water:
		bodyOfWater=df["Sample Source"][row]
		if not pd.isnull(bodyOfWater):
			bodyOfWater=cn.remPrefix(bodyOfWater,2)

			if "Watershed" in bodyOfWater:
				locationTriple+=campy.indTriple(bodyOfWater,"Watershed")
				locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":bodyOfWater},False)
				locationTriple+=campy.propTriple(bodyOfWater,{"hasName":bodyOfWater},True)
			else:
				# The word river is also in the watershed values, eg oldman river watershed. So 
				# if the value does not contain watershed but does contain river, it is considered a 
				# body of water.
				#The sumas and salmon rivers are the only bodies of water.
				if re.search("[Rr]iver",bodyOfWater) is not None:
					locationTriple+=campy.indTriple(bodyOfWater,"BodyOfWater")
					locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":bodyOfWater},False)
					locationTriple+=campy.propTriple(bodyOfWater,{"hasName":bodyOfWater},True)

	# SamplingSite is a real mess. Has a lot of redundant information. Also, some of them
	# have city info (Fort Macleod). Note Fort Macleod is also the name of the health authority 
	if not pd.isnull(samplingSite) and cn.isGoodVal(samplingSite):
		if "Mcleod" in samplingSite or "Macleod" in samplingSite:
			city="Fort Macleod"
			samplingSite=samplingSite.replace("Mcleod","Macleod") # It's spelt wrong in the csv
			samplingSite=samplingSite.replace("Ft.","Fort") # It's also abbreviated sometimes

		locationTriple+=campy.indTriple(samplingSite,"SamplingSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":samplingSite},False)
		locationTriple+=campy.propTriple(samplingSite,{"hasName":samplingSite},True)

	if not pd.isnull(country) and cn.isGoodVal(country):
		locationTriple+=campy.indTriple(country,"Country")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":country},False)
		locationTriple+=campy.propTriple(country,{"hasName":country},True)

	if not pd.isnull(subNat) and cn.isGoodVal(subNat):
		locationTriple+=campy.indTriple(subNat,"SubNational")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":subNat},False)
		locationTriple+=campy.propTriple(subNat,{"hasName":subNat},True)

	if not pd.isnull(city) and cn.isGoodVal(city):
		locationTriple+=campy.indTriple(city,"City")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":city},False)
		locationTriple+=campy.propTriple(city,{"hasName":city},True)

	if not pd.isnull(hAuthority) and cn.isGoodVal(hAuthority):
		hAuthority=cn.remPrefix(hAuthority,3)
		# Sometimes watersheds are here. If they are, they are also in the Sample Source
		# column, and we've already handled that. Note that a watershed is not a 
		# health authority
		if re.search("[Ww]atershed",hAuthority) is None: 
			# Montérégie is in the csv and the é is all screwed up
			if re.search("Mont.r.gie",hAuthority) is not None:
				hAuthority=re.sub("Mont.r.gie","Montérégie",hAuthority)

			locationTriple+=campy.indTriple(hAuthority,"HealthAuthority")
			locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":hAuthority},False)
			locationTriple+=campy.propTriple(hAuthority,{"hasName":hAuthority},True)

	if not pd.isnull(samplingSite2) and ("Petting Zoo" in samplingSite2):
		locationTriple+=campy.indTriple(samplingSite2,"SamplingSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":samplingSite2},False)
		locationTriple+=campy.propTriple(samplingSite2,{"hasName":samplingSite2},True)

	if not pd.isnull(c_netSite) and cn.isGoodVal(c_netSite):
		c_netSite=cn.cleanInt(c_netSite)
		locationTriple+=campy.indTriple(c_netSite,"C_EnterNetSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":c_netSite},False)
		locationTriple+=campy.propTriple(c_netSite,{"hasName":c_netSite},True)

	if not pd.isnull(fncSite) and cn.isGoodVal(fncSite):
		locationTriple+=campy.indTriple(fncSite,"FNCSentinelSite")
		locationTriple+=campy.propTriple(isoTitle,{"hasSourceLocation":fncSite},False)
		locationTriple+=campy.propTriple(fncSite,{"hasName":fncSite},True)


	# Have to convert lat and long to signed decimal format
	if not pd.isnull(lng) and cn.isGoodVal(lng):
		if not pd.isnull(lat) and cn.isGoodVal(lat): # lat is never nan when long is and vice versa
			# For some reason the lat and long values in the csv have some newline chars in them
			lat=lat.strip()
			lng=lng.strip()
			lat=cn.convertGPS(lat)
			lng=cn.convertGPS(lng)

			locationTriple+=campy.propTriple(isoTitle,{"hasLatitude":lat},True,rLiteral=True)
			locationTriple+=campy.propTriple(isoTitle,{"hasLongitude":lng},True,rLiteral=True)

	return locationTriple


######################################################################################################
# createSourceTriples
# Here we call functions to create all triples associated with the source of the isolate
######################################################################################################
def createSourceTriples(df,row,isoTitle):

	resultTriple=createLocationTriples(df,row,isoTitle)

	sample=df["Sample Type"][row] # animal, human or environmental (and Reference Strain but that's
								  # handled when we to the project triples as every reference strain
								  # is mentioned in that column but sometimes not this one (Sample
								  # Type)).

	if sample=="Animal":
		resultTriple+=createAnimalTriples(df,row,isoTitle)
		resultTriple+=createTypeTriples(df,row,isoTitle)
	if sample=="Environmental":
		resultTriple+=createEnviroTriples(df,row,isoTitle)
	if sample=="Human":
		resultTriple+=createHumanTriples(df,row,isoTitle)

	return resultTriple

######################################################################################################
# createRefTriples
# Handles the reference strains. Most don't have source info, but some have just a little bit. There
# are only animal and human sources so we just worry about those. THIS COULD CHANGE.
######################################################################################################
def createRefTriples(df,row,isoTitle):
	rTriple=""
	source=df["Source_Specific_2"][row]
	animalID=df["Animal ID"][row]

	rTriple=campy.propTriple(isoTitle,{"isReferenceStrain":"true"},True,rLiteral=True)

	if not pd.isnull(source) and cn.isGoodVal(source):
		if re.search("[Hh]uman",source) is not None:
			title="patient_"+isoTitle # Use the human naming convention
			sClass="Patient"
		else: # It's an animal source
			source=cn.remPrefix(source,2)
			sClass=source
			if not pd.isnull(animalID):
				title=cn.cleanInt(animalID) # Use animal ID if available
			else:
				title=source+"_"+isoTitle # Else use animal naming convention

			
		# We don't know if the animal is a Ruminant, or what have you, so we just set it as an 
		# instance of whatever kind of animal it is, eg cowC1004 is an instance of cow. We just pray 
		# that that animal has already been set as an instance of whatever family it belongs to 
		# earlier when we handled the animal source triples. If it's a human its just an instance 
		# of Patient.
		rTriple+=campy.indTriple(title,sClass)
		rTriple+=campy.propTriple(isoTitle,{"hasSampleSource":title},False)

	return rTriple

######################################################################################################
#
######################################################################################################
def createProjTriples(df,row,isoTitle):
	resultTriple=""
	projTriple=""
	isoTriple=""
	proj=df["Dataset ID_1"][row]
	subproj=df["Dataset ID_2"][row]

	# Whether an isolate is a reference strain or not is stored in the 'Dataset ID_1' column 
	# (proj variable), and usually in subsequent columns, but not always. So if it is, we have 
	# to set some properties, otherwise create the projec triples.
	if re.search("[Rr]eference[ -_][Ss]train",proj) is not None:
		resultTriple=createRefTriples(df,row,isoTitle)
	else:
		if not pd.isnull(proj) and cn.isGoodVal(proj): 
			projTriple+=campy.indTriple(proj,"Project")+campy.propTriple(proj,{"hasName":proj},True)

			isoTriple+=campy.propTriple(isoTitle,{"partOfProject":proj},False)

			if not pd.isnull(subproj) and cn.isGoodVal(proj):
				for c in " _":
					# Split by '-',' ', or '_' if it's preceded by at least 2 characters,
					# we don't want to remove 'C' when the project=C-Enternet for example.
					toRem=re.split("(?<=..)[- _]",proj)
					for r in toRem:
						subproj=subproj.replace(r,"")
						subproj=subproj.strip()

					# Remove all the '-',' ', and '_' if they are NOT preceded by a character
					subproj=re.sub("(?<!.)[- _]","",subproj)

				if subproj!="":
					subproj=cn.cleanInt(subproj) # Some of the subprojects are years
					projTriple+=campy.indTriple(subproj,"SubProject")
		   			projTriple+=campy.propTriple(subproj,{"hasName":subproj},True)
		   			projTriple+=campy.propTriple(proj,{"hasSubproject":subproj},False)

	   				isoTriple+=campy.propTriple(isoTitle,{"partOfSubProject":subproj},False)

	resultTriple+=isoTriple+projTriple
   	return resultTriple

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
	cgfTriple=lab.indTriple(cgfTest1,"CGFtest")

	# Every cgf test in the csv is inVitro
	cgfTriple+=lab.propTriple(cgfTest1,{"isInVitro":"true"},True,rLiteral=True)

	if fileLoc!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasFileLocation":fileLoc},True,rLiteral=True)
	if date!="":
		cgfTriple+=lab.propTriple(cgfTest1,{"hasDateCompleted":date},True,rLiteral=True)

	if not pd.isnull(fingerprint) and cn.isGoodVal(fingerprint):
		fingerprint=fingerprint.replace("fp","")
		cgfTriple+=lab.propTriple(cgfTest1,{"hasFingerprint":fingerprint},True,rLiteral=True)

	# Note that we have hex numbers converted to strings in TripleMaker (just because the isDigit function
	# returns false on hex's (that's what we want)) because there doesn't seem to be a hex number data type 
	# in rdf or whatever. It breaks the ontology if we insert it as is
	if not pd.isnull(legacyHexNum) and cn.isGoodVal(legacyHexNum):
		legacyHexNum=legacyHexNum.replace("BIN","")
		cgfTriple+=lab.propTriple(cgfTest1,{"hasLegacyHexNum":legacyHexNum},True,rLiteral=True)

	if not pd.isnull(typingLab) and cn.isGoodVal(typingLab):
		# Have to create a typing lab triple and then attach the cgf test to it
		labTriple=lab.indTriple(typingLab,"TypingLab") # labTitle is an instance of the class TypingLab
		# Right now the URI for hasName is the campy ont. URI. Gonna have to change it to a URI seperate
		# from both campy and labTest URI. WE MUST FIX THIS
		labTriple+=lab.addUri(cn.cleanString(typingLab))+" "+campy.addUri("hasName")+\
			       " \""+typingLab+"\""+" .\n"
		# Attach the lab to the cgf test
		cgfTriple+=lab.propTriple(cgfTest1,{"doneAtLab":typingLab},False)
		

	clustTriple=createClustTriples(df,row,cgfTest1)
	if clustTriple!="":
		cgfTriple+=clustTriple
	
	# Some triples have more than one URI, so we make our own using TripleMaker's 
	# helper function addUri. WE MUST FIX THIS
	isoTriple=campy.addUri(cn.cleanString(isoTitle))+" "+campy.addUri("hasLabTest")+" "+\
		      lab.addUri(cn.cleanString(cgfTest1))+" .\n"

	return labTriple+cgfTriple+isoTriple

######################################################################################################
#
######################################################################################################
def createSpeciesTriples(df,row,isoTitle):
	isoTriple=""
	lSpec=""
	aSpec=""
	specA=""
	specB=""
	lethSpec=df["Campy Species (Leth - 16S, mapA, ceuE)"][row]
	altSpec=df["Alt. Speciation"][row]

	# If lethSpec isn't null it's the species. If altSpec is not null, it then becomes the species.
	# This is fine as long as they are the same values, or one is empty and the other is not. If 
	# they are not the same values, lethSpec becomes the species, unless lethSpec is unknown or any 
	# of that other crazy crap. Sometimes the species are mixed (of the form 'Mixed (coli and jejuni)') 
	# in which case specA="coli" and specB="jejuni". But sometimes it will just say 'Mixed' in 
	# lethSpec but 'Coli' in altSpec. In such a case specA="coli".

	if not pd.isnull(lethSpec) and cn.isGoodVal(lethSpec):
		lethSpec=lethSpec.lower().strip() # for comparison
		specA=lethSpec if lethSpec!="other campylobacter" else ""

	if not pd.isnull(altSpec) and cn.isGoodVal(altSpec):
		altSpec=altSpec.lower().strip() # ditto
		specA=altSpec if altSpec!="other campylobacter" else ""

	# If both are non empty and don't equal eachother, specA becomes lethSpec, unless lethSpec is 
	# equal to 'other_campylobacter' and altSpec is something more specific
	if not pd.isnull(lethSpec) and not pd.isnull(altSpec):
		if lethSpec!=altSpec and cn.isGoodVal(lethSpec):
			specA=lethSpec if lethSpec!="other campylobacter" else "" 

		# Sometimes lethspec will equal mixed and altspec will equal coli.
		# In this case we take coli to be the correct species
		if "mixed"==lethSpec and "coli"==altSpec:
			specA="coli"

	
	if "mixed (coli and jejuni)"==lethSpec or "mixed (coli and jejuni)"==altSpec:
		specA="coli"
		specB="jejuni"


	if specA!="":
		isoTriple+=campy.indTriple(specA,"CampySpecies")+campy.propTriple(specA,{"hasName":specA},True)
		isoTriple+=campy.propTriple(isoTitle,{"hasSpecies":specA},False)
	if specB!="":
		isoTriple+=campy.indTriple(specB,"CampySpecies")+campy.propTriple(specB,{"hasName":specB},True)
		isoTriple+=campy.propTriple(isoTitle,{"hasSpecies":specB},False)

	putInOnt(isoTriple)
	return isoTriple

######################################################################################################
#
######################################################################################################
def createDateTriples(df,row,isoTitle):
	dateTaken=""
	isoTriple=""
	year=df["YEAR"][row]
	month=df["MONTH"][row]
	day=df["DAY"][row]

	# Sometimes year is empty, but the other fields aren't
	if not pd.isnull(day) and not pd.isnull(month) and not pd.isnull(year):
		dateTaken=cn.cleanInt(year)+"-"+cn.cleanInt(month)+"-"+cn.cleanInt(day)
	
	if not pd.isnull(year) and pd.isnull(month) and pd.isnull(day):
		dateTaken=cn.cleanInt(year)

	if dateTaken!="":
		isoTriple+=campy.propTriple(isoTitle,{"hasDateSampleTaken":dateTaken},True,rLiteral=True)

	return isoTriple

######################################################################################################
#
######################################################################################################
def createLIMStriples(df,row,isoTitle):
	isoTriple=""
	nmlid=df["NML ID#"][row]
	ldmsid=df["LDMS ID"][row]
	origName=df["Mostly Original Sample Names (might have project prefixes!)"][row] # lol
	isoLocA=df["Isolate Location 1"][row]
	isoLocB=df["Isolate Location 2"][row]
	isoLoc=""
	sidA=df["Alternate Sample ID"][row]  # Sample id
	sidB=df["Alt. Sample ID"][row]
	sidC=df["C-EnterNet Number"][row]
	cidA=df["Sample Collection ID"][row] # Collection id
	cidB=""
	dateAdded=df["Date Added to Database"][row]

	if not pd.isnull(nmlid):
		isoTriple+=campy.propTriple(isoTitle,{"hasNMLid":nmlid},True,rLiteral=True)
	if not pd.isnull(ldmsid):
		isoTriple+=campy.propTriple(isoTitle,{"hasLDMSid":ldmsid},True,rLiteral=True)
	if not pd.isnull(origName):
		isoTriple+=campy.propTriple(isoTitle,{"hasOriginalName":origName},True,rLiteral=True)

	if not pd.isnull(isoLocA):
		isoLoc=isoLocA
	if not pd.isnull(isoLocB):
		isoLoc=isoLocB
	if isoLoc!="":
		isoTriple+=campy.indTriple(isoLoc,"IsolateLocation")
		isoTriple+=campy.propTriple(isoLoc,{"hasName":isoLoc},True)
		isoTriple+=campy.propTriple(isoTitle,{"hasIsolateLocation":isoLoc},False)

	if not pd.isnull(sidA) and cn.isGoodVal(sidA):
		isoTriple+=campy.propTriple(isoTitle,{"hasSampleID":sidA},True,rLiteral=True)
	if not pd.isnull(sidB) and cn.isGoodVal(sidB):
		isoTriple+=campy.propTriple(isoTitle,{"hasSampleID":sidB},True,rLiteral=True)
	if not pd.isnull(sidC) and cn.isGoodVal(sidC):
		isoTriple+=campy.propTriple(isoTitle,{"hasSampleID":sidC},True,rLiteral=True)

	# Alternate collection id is stored alongside original collection id.
	if not pd.isnull(cidA):
		cidA=cn.cleanInt(cidA)
		if re.search("[aA]lt",cidA) is not None:
			cids=cidA.split(" ")
			cidA=cids[0]
			cidA=cidA[:len(cidA)-1] # Get rid of the semi colon at the end
			cidB=cids[len(cids)-1] # Get the last item in the cids list

			isoTriple+=campy.propTriple(isoTitle,{"hasCollectionID":cidB},True,rLiteral=True)			

		isoTriple+=campy.propTriple(isoTitle,{"hasCollectionID":cidA},True,rLiteral=True)

	if not pd.isnull(dateAdded):
		dateAdded=cn.convertDate(dateAdded)
		isoTriple+=campy.propTriple(isoTitle,{"hasDateAdded":dateAdded},True,rLiteral=True)

	return isoTriple

######################################################################################################
#
######################################################################################################
def createIsolationTriples(df,row,isoTitle):
	isoTriple=""
	media=df["Media"][row]
	# Don't include colony morph for now.
	# colonyMorph=df["colony morph"][row]
	dilution=df["Dilution"][row]
	glycStock=df["No glycerol stock"][row]
	hipO=df["HipO"][row]
	treatment=df["Treatment"][row]
	technique=df["technique"][row]
	sourceSpec=df["Source_Specific_2"][row] # For whatever reason source specific 2 has media info in
											# it. Just one though: K and Cefex

	# For whatever reason there's just a dash as one of the media values. We'll ignore it for now.
	if not pd.isnull(media) and media!="-" and "#N/A" not in media:
		# We'll standardize all media to be uppercase and some have spaces but others don't. eg
		# there's the value '10% B' and '10%B'. That's no good.
		media=media.upper().replace(" ","")
		
		# Grab k and cefex from source specific 2
		if not pd.isnull(sourceSpec) and re.search("[Cc]efex",sourceSpec) is not None:
			media="K and CEFEX" # SUBJECT TO CHANGE

		isoTriple+=campy.propTriple(isoTitle,{"grownOn":media},True,rLiteral=True)

	if not pd.isnull(dilution):
		# Again there are some values that have spaces and others that don't. 
		# We'll get rid of the spaces 
		dilution=dilution.replace(" ","")
		isoTriple+=campy.propTriple(isoTitle,{"hasDilution":dilution},True,rLiteral=True)

	# The values in the csv are 1 or 0. 1 meaning it is true there is no glyc stock. This
	# is confusing. So in the ontology we have 'hasGlycStock' and we interpret 1 as false
	if not pd.isnull(glycStock) and "NA" not in cn.cleanInt(glycStock):
		glycStock=cn.cleanInt(glycStock) # Sometimes numbers are converted to floats
		glycStock="false" if "1" in glycStock else "true"
		isoTriple+=campy.propTriple(isoTitle,{"hasGlycStock":glycStock},True,rLiteral=True)

	if not pd.isnull(hipO) and "#N/A" not in cn.cleanInt(hipO):
		hipO=cn.cleanInt(hipO)

		if "1" in hipO:
			hipO="true"
		else:
			hipO="unknown" if "?" in hipO else "false"
		isoTriple+=campy.propTriple(isoTitle,{"hasHipO":hipO},True,rLiteral=True)

	# For whatever reason the value 'Treatment' is in the column 'Treatment'. We'll ignore it 
	# for now. 
	if not pd.isnull(treatment) and "Treatment" not in treatment and "#N/A" not in treatment:
		isoTriple+=campy.propTriple(isoTitle,{"hasTreatment":treatment},True,rLiteral=True)

	# The - also showed up in technique. We'll ignore it.
	if not pd.isnull(technique) and technique!="-":
		# Values enrichment and enrich are found in this col. We'll standardize it to 'enrich'
		if re.search("[Ee]nrich",technique) is not None:
			technique="enrich"

		# Some values have spaces and others don't. eg '24AE' and '24 AE'. We'll get rid of
		# spaces.
		technique=technique.replace(" ","")

		isoTriple+=campy.propTriple(isoTitle,{"hasTechnique":technique},True,rLiteral=True)
			
	return isoTriple

######################################################################################################
#
######################################################################################################
def createTypingTriples(df,row,isoTitle):
	testTriple=""
	mTriple=""
	cols=list(df.columns.values) # Get all the column names

	genes=cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract gene names
	# The names of the tests are just the name of the gene they test plus isoTitle, but MLST tests
	# 7 genes, so mlst test name will be 'mlst'+isoTitle
	mlstGenes=genes[genes.index("Asp"):genes.index("Unc (atpA)")+1] 
	cloComp=df["Clonal Complex"][row] # For mlst only
	st=df["ST"][row] # For mlst only
	mTitle="mlst_"+isoTitle

	# The value 'none' is in cloComp right now. Ignore it...for now
	if not pd.isnull(cloComp) and "none" not in cloComp:
		mTriple+=lab.propTriple(mTitle,{"foundClonalComplex":cloComp},True,rLiteral=True)

	if not pd.isnull(st):
		st=cn.cleanInt(st)
		mTriple+=lab.propTriple(mTitle,{"foundST":st},True,rLiteral=True)

	# Go through all the genes, get the allele index, create allele, attach allele to gene,
	# add the allele index to the allele, attach the test to the allele.
	for g in genes:
		alIndex=df[g][row]
		if not pd.isnull(alIndex) and cn.isNumber(alIndex):
			alIndex=cn.cleanInt(alIndex)
			alTitle=g+"_"+alIndex
			testTriple+=lab.indTriple(alTitle,"TypingAllele")
			testTriple+=lab.propTriple(alTitle,{"isOfGene":g},False)
			testTriple+=lab.propTriple(alTitle,{"hasAlleleIndex":alIndex},True,rLiteral=True)

			if g in mlstGenes:
				mTriple+=lab.propTriple(mTitle,{"foundAllele":alTitle},False)
			else:
				# Have to clean up some of the gene names. Don't need 'Oxford' or 'peptide'
				# in 'Oxford MOMP peptide'
				testClass=g.replace("Oxford","")
				testClass=testClass.replace("MOMP peptide","MOMP")
				testClass=testClass.replace("fla peptide","flaPeptide")
				testClass=testClass.replace(" ","")+"test"
				testTitle=testClass+"_"+isoTitle
				testTriple+=lab.indTriple(testTitle,testClass)
				testTriple+=lab.propTriple(testTitle,{"foundAllele":alTitle},False)
				testTriple+=campy.addUri(isoTitle)+" "+campy.addUri("hasLabTest")+" "\
						    +lab.addUri(testTitle)+" ."

	if mTriple!="":
		mTriple+=lab.indTriple(mTitle,"MLSTtest")	
		mTriple+=campy.addUri(isoTitle)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(mTitle)+" ."

	return mTriple+testTriple

######################################################################################################
#
######################################################################################################
def createAMRtriples(df,row,isoTitle):
	aTriple=""
	cols=list(df.columns.values) # Get all the column names
	mic_drugs=cols[cols.index("mic_azm"):cols.index("mic_tet")+1] # Get all the drugs with 'mic_'
	r_drugs=cols[cols.index("razm"):cols.index("rtet")+1] # Get all the drugs with 'r' prefix
	drugs=[d.replace("mic_","") for d in mic_drugs] # Remove the prefix to get drug names
	testTitle="amr_"+isoTitle
	amr=df["AMR"][row] # The column 'AMR' also has some info related to drug resistance for w/e reason

	# Get the mics first
	for m in mic_drugs:
		mic=df[m][row]
		drug=m.replace("mic_","") # Remove the 'mic_' prefix
		if not pd.isnull(mic):
			# Not all of them are floats, and they should be.
			mic=str(float(mic)) if cn.isNumber(mic) else str(mic) 
			dmTitle=mic+"_"+drug
			aTriple+=lab.indTriple(dmTitle,"DrugMIC")
			aTriple+=lab.propTriple(dmTitle,{"hasMIC":mic},True,rLiteral=True)
			aTriple+=lab.propTriple(dmTitle,{"hasDrug":drug},False)
			aTriple+=lab.propTriple(testTitle,{"foundMIC":dmTitle},False)


	# Handle the random drug resistance in column 'AMR'. The only value 
	# in this column is 'Nal R'
	if not pd.isnull(amr):
		drug=amr.split(" ")[0].lower() # All the other drugs are lower case
		aTriple+=lab.propTriple(testTitle,{"foundResistanceTo":drug},False)


	for r in r_drugs:
		res=df[r][row]
		drug=re.sub("^r","",r) # Remove the 'r' prefix
		if not pd.isnull(res):
			res=int(res) # It's stored as a double, we need an int
			if res==1: # The strain is resistant
				aTriple+=lab.propTriple(testTitle,{"foundResistanceTo":drug},False)
			else: # The strain is sensitive
				aTriple+=lab.propTriple(testTitle,{"foundSusceptibilityTo":drug},False)
	

	if aTriple!="":
		aTriple+=lab.indTriple(testTitle,"AMRtest")
		aTriple+=campy.addUri(isoTitle)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(testTitle)+" ."

	return aTriple


######################################################################################################
#
######################################################################################################
def createSeroTriples(df,row,isoTitle):
	sTriple=""
	sero=df["Serotype"][row]

	if not pd.isnull(sero):
		sTitle="sero_"+isoTitle
		sTriple+=lab.indTriple(sTitle,"SerotypeTest")
		sTriple+=lab.propTriple(sTitle,{"foundSerotype":sero},True,True)
		sTriple+=campy.addUri(isoTitle)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(sTitle)+" ."

	return sTriple


######################################################################################################
#
######################################################################################################
def createSMAtriples(df,row,isoTitle):
	sTriple=""
	pulsovar=df["Pfge Sma I  / Pulsovar"][row]

	if not pd.isnull(pulsovar):
		sTitle="sma1_"+isoTitle
		sTriple+=lab.indTriple(sTitle,"SMA1")
		sTriple+=lab.propTriple(sTitle,{"foundPulsovar":pulsovar},True,True)
		sTriple+=campy.addUri(isoTitle)+" "+campy.addUri("hasLabTest")+" "+lab.addUri(sTitle)+" ."

	return sTriple


######################################################################################################
#
######################################################################################################
def createOutbreakTriples(df,row,isoTitle):
	obTriple=""
	obA=df["Outbreak"][row]
	obB=df["Source_Specific_2"][row]

	# Some of the values in comlumn 'Outbreak' are just 'outbreak'. In such a case, we know the 
	# isolate is part of an outbreak, we just don't know the outbreak name
	if not pd.isnull(obA) and re.search("[Oo]utbreak",obA) is not None:
		if obA.strip().lower()=="outbreak":
			obTriple=campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},True,rLiteral=True)
		else:
			obTriple=campy.propTriple(isoTitle,{"partOfOutbreak":obA},False)
			obTriple+=campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},True,rLiteral=True)

	# Source_specific_2 (obB) actually contains the name of the outbreak, maybe
	else:
		if not pd.isnull(obB) and re.search("[Oo]utbreak",obB) is not None:
			obTriple=campy.propTriple(isoTitle,{"isPartOfOutbreak":"true"},True,rLiteral=True)
			obTriple+=campy.propTriple(isoTitle,{"partOfOutbreak":obB},False)

	return obTriple


######################################################################################################
#
######################################################################################################
def createDrugTriples(df):
	dTriple=""
	cols=list(df.columns.values) # Get all the column names
	drugs=cols[cols.index("mic_azm"):cols.index("mic_tet")+1]
	drugs=[d.replace("mic_","") for d in drugs]

	for d in drugs:
		dTriple+=lab.indTriple(d,"AMRdrug")

	return dTriple
	

######################################################################################################
#
######################################################################################################
def createGeneTriples(df):
	triple=""
	cols=list(df.columns.values) # Get all the column names
	aGenes=cols[cols.index("Asp"):cols.index("Oxford MOMP peptide")+1] # Extract allelic typing genes
	cgfGenes=cols[cols.index("cj0008 (486bp)"):cols.index("cj1727c (369bp)")+1] # Extract cgf genes

	for a in aGenes:
		triple+=lab.indTriple(a,"AllelicTypingGene")
		# HOW SHOULD WE HANDLE MULTI URI TRIPLES?
		triple+=lab.addUri(a)+" "+campy.addUri("hasName")+" \""+a+"\" ."

	for c in cgfGenes:
		triple+=lab.indTriple(c,"CGFtypingGene")
		# ???????????
		triple+=lab.addUri(c)+" "+campy.addUri("hasName")+" \""+c+"\" ."
		
	return triple


######################################################################################################
#
######################################################################################################
def createTriples(df,row):
	# Get the isolate name. Note the URI for an isolate needs to be a clean string, but we want the 
	# original csv name aswell. Same goes for everything else with a name
	isoTitle=df["Strain Name"][row]

	triple=campy.indTriple(isoTitle,"Isolate")+\
		   campy.propTriple(isoTitle,{"hasIsolateName":isoTitle},True,rLiteral=True)

	triple+=createSpeciesTriples(df,row,isoTitle)	
	"""
	triple+=createProjTriples(df,row,isoTitle)

	triple+=createSourceTriples(df,row,isoTitle)

	triple+=createOutbreakTriples(df,row,isoTitle)
	
	triple+=createSMAtriples(df,row,isoTitle)

	triple+=createSeroTriples(df,row,isoTitle)
	
	triple+=createAMRtriples(df,row,isoTitle)

	triple+=createTypingTriples(df,row,isoTitle)

	triple+=createIsolationTriples(df,row,isoTitle)
	
	triple+=createDateTriples(df,row,isoTitle)

	triple+=createLIMStriples(df,row,isoTitle)

	triple+=createCgfTriples(df,row,isoTitle)
	"""

	#writeToBG(triple)

######################################################################################################
# Reads in data from the spreadsheet and writes triples
######################################################################################################
def writeData():
	df=pd.read_csv(r"/home/student/CampyDB/2016-02-10 CGF_DB_22011_2.csv")

	# The column names contain a bunch of genes that need to be in the triplestore,
	# so we'll add those first
	triple=createGeneTriples(df)
	# The column names contain the names of the AMR drugs aswll
	triple=createDrugTriples(df)

	#putInOnt(triple)
	# insert Triple

	#createTriples(df,16316)
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
	






			

			
	
