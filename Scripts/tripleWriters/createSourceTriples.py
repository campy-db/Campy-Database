import sys
sys.path.append("/home/student/CampyDB/CampyDatabase")

from Scripts import cleanCSV as cn
import pandas as pd
from campyTM import campy as ctm
import re
import pycountry as pc
import datetime

now = datetime.datetime.now()
subNats = [x.name for x in list(pc.subdivisions)] # A list of names of subnationals
countries = [x.name for x in list(pc.countries)] # A list of names of countries

######################################################################################################
# createAgeTriples
# Some patients in the csv have ages. The values are found in the 'Patient D.O.B / Age' column. 
# The column has birthdates,  ages,  and age ranges of the form 'a/X-Y years' where X and Y are ages
# and a is some random character. As of right now,  we ignore ranges in hopes that Steven can get the
# actual ages.
######################################################################################################
def createAgeTriples(df, row, hum):
	
	humTriple = ""
	yearLen = 4
	ageLen = 2
	age = df["Patient D.O.B / Age"][row]
	yearTaken = df["YEAR"][row]
										   
	if not pd.isnull(age) and cn.isGoodVal(age): 

		if len(age) > ageLen: # if a birthday or range

			if "years" in age: # Every range contains the word 'years'.
				# Most ranges are of the form age-age,  but some are age+
				age = "" # Ignore ranges for now

			else: # The value is a birth day

				bday = cn.convertDate(age, False) # Will standardize the date to iso and check
											   # if it's a valid date.

				if bday  !=   -1:

					dates = bday.split("-")

					dates = [cn.cleanInt(d) for d in dates]

					humTriple +=   ctm.propTriple(hum,  {"hasBirthDay":dates[2]
					                                     "hasBirthMonth":dates[1]
					                                     "hasBirthYear":dates[0]},  "int",  True)

				# else: date is invalid

				if not pd.isnull(yearTaken):
	
					# yearTaken is stored as a float for w/e reason in the csv
					age = int(float(yearTaken)) - int(dates[0])
													      
					if age < 0: # One of the patients was born in 2011, but the sample was taken in 2010
						age = 0
				else:
					age = now.year - int(bday[:yearLen]) # Use todays year for the age

		humTriple +=   ctm.propTriple(hum,  {"hasAge":age},  True,  True) if age else ""	

	return humTriple

######################################################################################################
# createTravelTriples
# A patient's travel info is in column 'Comments' and is of the form 'Travel: [location]'. Sometimes
# it's just the country,  or the province/state,  or both. We will store only the lowest level. eg
# from the location value 'Ohia,  USA' we will store only Ohio as it is derivable that the patient
# traveled to the states.
######################################################################################################
def createTravelTriples(df, row, hum):
	
	humTriple = ""
	trTriple = "" # Travel info triple
	travel = df["Comments"][row] # All travel info is in the comments column
	
	# We will keep the lowest level of ganularity,  eg from 'Ohio,  USA' we'll keep only Ohio as USA
	# is derivable (consider revising).

	if not pd.isnull(travel) and "Travel" in travel: # All travel values are prefixed with 'Travel: '
	
		travel = travel.replace("Travel:", "").strip() # Remove the 'Travel:' prefix

		# Some values are suffixed with a bunch of meaningless(ful?) stuff
		end = re.search("[;, ]", travel)
		travel = travel[:end.span()[0]] if end is not None else travel

		if travel in subNats:
			trTriple = ctm.indTriple(travel, "SubNational")
		if travel in countries:
			trTriple = ctm.indTriple(travel, "Country")

		trTriple +=  ctm.propTriple(travel, {"hasName":travel}, True)
		humTriple = ctm.propTriple(hum, {"traveledTo":travel})

	return trTriple+humTriple

######################################################################################################
# createHumanTriples
# Create an individual human for all isolates that have a human as a source. No names are given so
# the unique id for humans is 'patient_[isoTitle]'. Note all humans in the csv are patients so they
# will be instances of the Patient class. Here we will also get the properties postal code if 
# available and gender if available. We also get set the clinical sample type here.
######################################################################################################
def createHumanTriples(df, row, isoTitle):
	
	type = ""
	isoTriple = ""
	hum = "{}_{}".format("patient", isoTitle)
	
	gender = df["Gender"][row]
	postalCode = df["Postal code"][row]
	sTypeA = df["Source_Specific_2"][row] # The clinical sample type
	sTypeB = df["Clinical Sample Type"][row] # Also has clinical sample typ

	# Just create a generic human individual
	humTriple = ctm.indTriple(hum, "Patient") # All human samples in the csv are patients
	humTriple +=  ctm.propTriple(hum, {"hasName":hum}, True)

	# Travel info is in the column 'comments' and it's quite messy so we'll
	# handle it separately 
	humTriple +=  createTravelTriples(df, row, hum)

	# The age is stored in a column with birthdays and other random crap so we'll 
	# handle it separately
	humTriple +=  createAgeTriples(df, row, hum)

	# The values 0,  m,  f,  male,  female and 'not given' are in the csv. We won't add the prop if 
	# it's 'not given'
	if not pd.isnull(gender) and cn.isGoodVal(gender) and gender !=  0:
		humTriple += ctm.propTriple(hum, {"hasGender":gender[0].lower()}, True, True)

	if not pd.isnull(postalCode):
		humTriple += ctm.propTriple(hum, {"hasPostalCode":postalCode}, True, True)

	# If sTypeA is nan,  try sTypeB
	typeCol = sTypeA if not pd.isnull(sTypeA) else sTypeB

	if not pd.isnull(typeCol) and cn.isGoodVal(typeCol):
		
		if re.search("[Ss]tool", typeCol) is not None:
			type = "stool"
		if re.search("[Bl]ood", typeCol) is not None:
			type = "blood"

	 # type could still be "" as not all the values for sTypeA (Source_Specific_2) are 
	 # clinical sample types,  i.e. 'blood' or 'stool'
	if type !=  "":
		isoTriple += ctm.indTriple(type, "ClinicalType")
		isoTriple += ctm.propTriple(type, {"hasName":type}, True)
		isoTriple += ctm.propTriple(isoTitle, {"hasSampleType":type})
		
	isoTriple += ctm.propTriple(isoTitle, {"hasSampleSource":hum})

	return humTriple + isoTriple


######################################################################################################
# createEnviroTriples
# Creates an instance of Environment for every isolate that has an environmental source type. We don't
# bother uniquely identifying different environment sources; this is just so the user knows what type
# of environment the source came from. We would consider revising this if enviro sources had an ID. 
# Though really the enviro's unique ID is the sampling site name or body of water name which we fetch
# in the function createLocation triples.
######################################################################################################
def createEnviroTriples(df, row, isoTitle):
	
	enviroTriple = ""
	isoTriple = ""
	enviro = cn.remPrefix(df["Source General"][row], 2) # Water,  lagoon,  sewage,  sand,  unknown
	enviroSpec = df["Source_Specific_2"][row] # Lagoon:Dairy,  Sewage (treated) etc.

	# If enviroSpec (the source specific 2 value) is actually something meaningful,  it will be an 
	# instance of the class enviro,  eg 'Swine' is an instance of the class 'Lagoon',  'Treated' is an 
	# instance of 'Sewage'. For other random enviroSpec values,  like 'other',  'water' (when we already 
	# have water as the enviro value),  the instance will just be the name of the class. The enviro 
	# value 'sand' is special in that it is not a class in ontology,  it will be an instance of the 
	# class 'Substrate'. Future soil samples can go in this class too if need be.

	if not pd.isnull(enviro) and cn.isGoodVal(enviro):
		# enviro (Source general) is the class and enviroSpec (source specific 2) is the instance.

		if not pd.isnull(enviroSpec) and "Other" not in enviroSpec: 
			
			# Have to clean enviroSpec strings a bit
			if re.search("[Tt]reated", enviroSpec) is not None: # For the value 'Sewage (Treated)'
			
				enviroSpec = "treated" # Don't need redundant info
				
			if "water" in enviroSpec.lower():
				if enviroSpec !=  "Water": # EnviroSpec is "drinking water source water",  
							   # "recreational water" or "core water site"
					enviroSpec = enviroSpec.replace(" water", "") # Get rid of redundant info
					
				else:
					enviroSpec = enviro # We don't really need this as enviroSpec already
							     # equals water. But whatever ya know
			 
			# EnviroSpec is "Lagoon: Swine" or "Lagoon:Dairy"
			if re.search("[Ll]agoon", enviroSpec) is not None:
			
				# Get rid of redundant info
				enviroSpec = enviroSpec.replace("Lagoon:", "")

		else: # We know the environment type (enviro) but EnviroSpec is nan or 'Other'
			enviroSpec = enviro

		# Sand is a special case for enviro as sand is not a class but an instance of Substrate
		if re.search("[Ss]and", enviro) is not None:
			enviro = "Substrate"
			enviroSpec = "sand"

	else: # We know it's an environmental source,  we don't know the environment type (enviro) or the specific
		  # environment source (enviroSpec). Note that source specific 2 is empty if source general is too.
		enviro = "Environment"
		enviroSpec = "unknown_enviro" # No unique identifier is needed here,  but some other things may be
									# named unknown in the future.
	
	title = enviroSpec.lower() # Doesn't need to be unique; there are no props attached to evironments. 
	
	enviroTriple = ctm.indTriple(title, enviro)+ctm.propTriple(title, {"hasName":enviroSpec}, True)
	
	isoTriple = ctm.propTriple(isoTitle, {"hasSampleSource":title})

	return enviroTriple + isoTriple
		

######################################################################################################
# createTypeTriples
# Here we create instances of the AnimalType class. Again we don't use unique identifiers as the user
# probably needs to only know the type of sample. I wish we could just say :isoC1007 :hasSampeType 
# "faecal",  but there are different kinds of faecal samples,  like droppings,  and swab. Also,  some 
# sampletypes have properties attached to them so that further complicates things,  just a bit though.
######################################################################################################
def createTypeTriples(df, row, isoTitle):
	
	isoTriple = ""
	stTriple = ""
	title = ""
	sampleType = df["Sample Type 2"][row] # Faecel,  Abbatoir,  Retail,  Egg
	sourceSpec = df["Source_Specific_2"][row] # chickenBreast,  carcass,  rectal swab etc.

	 # Insects don't have sample types
	if not pd.isnull(sampleType) and cn.isGoodVal(sampleType) and sampleType !=  "Insect":
		
		sampleType = sampleType.lower()

		if not pd.isnull(sourceSpec):
			
			sourceSpec = sourceSpec.lower()

			title = sampleType # The name of the sample type is just the sample type name
						     # unless there is something more specific in source specific 2

			# The source specific 2 for animal sample types is really messy. It's just
			# easier to hard code values in
			title = "breast" if "breast" in sourceSpec else title
			title = "thigh" if "thigh" in sourceSpec else title
			title = "caecum" if "caecum" in sourceSpec else title
			title = "carcass" if "carcass" in sourceSpec else title
			title = "ground" if "ground" in sourceSpec else title
			title = "loin" if "loin" in sourceSpec else title
			title = "droppings" if "field sample" in sourceSpec else title
			title = "pit" if "pit" in sourceSpec else title
			title = "swab" if "swab" in sourceSpec else title
			title = "weep" if "weep" in sourceSpec else title
	
			name = title

			title = "{}_{}".format(sampleType, title) if title !=  sampleType else title

			# sourceSpec has info related to the properties of meat.
			if "seasoned" in sourceSpec:
				
				title = "{}_{}_{}".format(sampleType, "seasoned", name)
				stTriple +=  ctm.propTriple(title, {"isSeasoned":False}, True, True)

			if "skin" in sourceSpec:
				
				if "skinless" in sourceSpec:
					
					title = "{}_{}_{}".format(sampleType, "skinless", name)
					stTriple += ctm.propTriple(title, {"isSkinless":True}, True, True)
				else:
					
					title = "{}_{}_{}".format(sampleType, name, "withskin")
					stTriple += ctm.propTriple(title, {"isSkinless":False}, True, True)
					
			if "rinse" in sourceSpec:
				
				title = "{}_{}_{}".format(sampleType, name, "rinse")
				stTriple += ctm.propTriple(title, {"isRinse":True}, True, True)

			if "breast" in title or "thigh" in title or "ground" in title or "loin" in title:
				stTriple+=  ctm.indTriple(title, "Meat")

			stTriple += ctm.propTriple(title, {"hasName":name}, True)

		else: # sourceSpec is nan
		
			name = sampleType
			title = sampleType # faecal,  abattoir,  retail,  egg

		stClass = "{}{}".format(sampleType, "Type")
		stTriple += ctm.indTriple(title, stClass)

		isoTriple += ctm.propTriple(isoTitle, {"hasSampleType":title})

	return stTriple+isoTriple

######################################################################################################
#
######################################################################################################
def isDomestic(farm, sourceSpec, animal, family):
	
	domestic = None
	
	if not pd.isnull(sourceSpec):
		
		sourceSpec = sourceSpec.lower()
		
		domestic = True if "domestic" in sourceSpec else domestic
		domestic = False if "wild" in sourceSpec else domestic

	# The values miscWild and miscDomestic are in the Source General column (family)
	domestic = False if "wild" in family else domestic
	domestic = True if "domestic" in family else domestic

	# Handle the domestic type of animal cases
	domestic = True if animal in ("cow", "chicken", "dog", "sheep", "cat") else domestic
	
	# Handle the wild type of animal cases
	domestic = False if animal in ("bear", "canada goose") else domestic

	if not pd.isnull(farm):
		farm = farm.lower()
		domestic = True if "farm" in farm else domestic

	domestic = False if "wild bird" in animal else domestic

	return domestic

######################################################################################################
# createAnimalTriples
# Creates instances of the Animal class for every isolate that has an animal as a source. Here we do
# uniquely identify animals as there is an animal id provided in the good 'ole csv. Not all animals
# have an id though so we name those ones [animel]_[isoTitle] where animal is the kind of animal,  eg
# chicken. Note we create new classes here for every type of animal and the new class becomes a
# subclass of its respective family. eg chicken_C1007 is an instance of Chicken,  and Chicken is  
# a sublass of Avian. Sometimes we know the source is an animal but we don't the family or animal. In
# this case we say the animal type is 'unknown' and it just becomes an instance of the Misc class. 
# Sometimes we know the family but not the animal type in which case unknown is an instance of family. 
# When we do know the animal type,  there are properties attached to animals found all over the csv and 
# many nice to work with,  totally random cases,  we have to handle.
######################################################################################################
def createAnimalTriples(df, row, isoTitle):
	
	isoTriple = "" ; animalTriple = "" ; domestic = "" ; taxoGenus = ""
	
	sourceSpec = df["Source_Specific_2"][row] # That pesky source specific 2 column
	
	family = cn.remPrefix(df["Source General"][row], 2) # Avian,  Ruminant etc.
	
	sex = df["Gender"][row]
	
	age = df["Patient D.O.B / Age"][row] # 0,  ,  juvenile,  and adult
	
	id = df["Animal ID"][row] # If the animal has an id,  this will be its URI
	
	animal = cn.remPrefix(df["Source_Specific_1"][row], 2) # The actual animal,  eg chicken,  racoon etc.
	
	ageRank = df["Patient D.O.B / Age"][row] # Juvenile,  Adult
	
	farm = df["Region_L2"][row] # Sometimes region_L2 (the sampling site) is a farm,  
							  # in which case the animal is domestic


	# An animal,  say chicken,  will become an instance of family (Avian in this case),  and Chicken,  
	# for example. Then Chicken will become a subclass of Avian. The individuals URI will be 
	# animal+isoTitle,  unless the id is present,  then this will be its URI. 


	if pd.isnull(family): # We know the source is an Animal but we don't know the family or type
						  # of animal. So it just becomes an instance of the animal class and is
						  # named 'unknown' (unless it has an id)
		animal = "unknown"
		family = "Misc"
		
	else: # We know the family
		if not pd.isnull(animal):
			
			animal = animal.lower()
			family = family.lower()

			domestic = isDomestic(farm, sourceSpec, animal, family)

			# Handle the MiscDomestic,  and MiscWild family cases
			if "misc" in family:
				
				# Give families do all the MiscWild and MiscDomestic animals. A lot of 
				# random cases here we need to handle.
				if "canada goose" in animal or "trumpeter swan" in animal or \
				   "mute" in animal or "bufflehead" in animal or "scaup" in animal or\
				   "merganser" in animal:

					family = "Avian"

				elif "small mammal" in animal:
					animal = "unknown"
					family = "Misc"
					
				elif "peromyscus" in animal:
					animal = "deer mouse"
					family = "Rodent"
					taxoGenus = "peromyscus"
					
				elif "rattus" in animal:
					animal = "rat"
					family = "Rodent"
					taxoGenus = "Rattus"
					
				elif "marmot" in animal:
					family = "Rodent"
					
				elif "unknown" in animal:
					family = "Misc"
					animal = "unknown"
					
				else: # racoons,  skunks,  and llama/alpaca
					family = "Misc"

			# There are the values Wild Bird,  goat/sheep,  alpaca/llama in source specific 1
			if "wild bird" in animal:
				animal = "unknown" # Wild bird has the family avian
			if "/" in animal:
				animal = animal.split("/")[0]

			# Source Specific 2 has more specific animals sometimes and also domestic/wild info
			if not pd.isnull(sourceSpec):
				
				sourceSpec = sourceSpec.lower()

				# The value Heifer is in source specific 2 for values of cow in source specific 1.
				# This is more specific than cow so Heifer will become a subclass of Cow
				if "heifer" in sourceSpec:
					
					animal = "heifer"
					family = "Cow"
					animalTriple += ctm.subClass(family, "Ruminant") # Cow is subclass of Ruminant

				# Dairy cow is more specific than just a cow so Dairy Cow becomes a subclass
				# of cow. DAIRY,  Dairy Cow,  and Dairy Manure are found in source specific 2
				if "dairy" in sourceSpec:
					
					animal = "dairy cow"
					family = "Cow"
					animalTriple += ctm.subClass(family, "Ruminant") # Cow is subclass of Ruminant

				if "shore bird" in sourceSpec:
					animal = "shore bird"

		else: # We know the family but not the animal
			animal = "unknown"

	# Note that even unknown animals need a unique identifier as they have properties attached to them
	# and can be part of different families

	# If the animal has an id,  this becomes its URI
	if not pd.isnull(id) and cn.isGoodVal(id):
		title = cn.cleanInt(id)
	else:
		title = "{}_{}".format(animal, isoTitle)


	if not pd.isnull(sex) and cn.isGoodVal(sex) and (sex[0] =  = "M" or sex[0] =  = "F"):
		animalTriple += ctm.propTriple(title, {"hasSex":sex[0].lower()}, True, True)

	if not pd.isnull(ageRank) and ("juvenile" in ageRank or "adult" in ageRank):
		animalTriple+=  ctm.propTriple(title, {"hasAgeRank":ageRank}, True, True)		
		
	if domestic:
		animalTriple += ctm.propTriple(title, {"isDomestic":domestic}, True, True)

	if animal !=  "unknown":
		# animal becomes an instance of animal,  and animal becomes a subclass of family
		animalTriple += ctm.indTriple(title, animal) + ctm.subClass(animal, family)

	if taxoGenus:
		animalTriple += ctm.propTriple(title, {"hasTaxoGenus":taxoGenus}, True, True)


	animalTriple += ctm.indTriple(title, family)

	isoTriple += ctm.propTriple(isoTitle, {"hasSampleSource":title})


	return animalTriple + isoTriple


######################################################################################################
# createSourceTriples
# Here we call functions to create all triples associated with the source of the isolate
######################################################################################################
def createSourceTriples(df, row, isoTitle):
	
	resultTriple = ""
	
	sample = df["Sample Type"][row] # animal,  human or environmental (and Reference Strain but that's
								  # handled when we to the project triples as every reference strain
								  # is mentioned in that column but sometimes not this one (Sample
								  # Type)).

	if sample == "Animal":
		
		resultTriple += createAnimalTriples(df, row, isoTitle)
		resultTriple += createTypeTriples(df, row, isoTitle)
		
	if sample == "Environmental":
		
		resultTriple += createEnviroTriples(df, row, isoTitle)
		
	if sample == "Human":
		
		resultTriple += createHumanTriples(df, row, isoTitle)

	return resultTriple
