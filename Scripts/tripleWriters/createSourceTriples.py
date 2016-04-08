"""
 createSourceTriples
"""

import re
import datetime
import pycountry as pc
import pandas as pd
from .. import cleanCSV as cn
from .campyTM import CAMPY as ctm

NOW = datetime.datetime.now()
SUBNATS = [x.name for x in list(pc.subdivisions)] # A list of names of subnationals
COUNTRIES = [x.name for x in list(pc.countries)] # A list of names of countries

####################################################################################################
# getAge
# Returns the age and/or birthdate
# Some patients in the csv have ages. The values are found in the 'Patient D.O.B / Age' column.
# The column has birthdates, ages, and age ranges of the form 'a/X-Y years' where X and Y are
# ages and a is some random character. As of right now, we ignore ranges in hopes that Steven can
# get the actual ages.
####################################################################################################
def getAge(df, row):

    birthdate = ""
    yearLen = 4
    ageLen = 2

    age = df["Patient D.O.B / Age"][row]

    yearTaken = df["YEAR"][row]

    if not pd.isnull(age) and cn.isGoodVal(age):

        if len(age) > ageLen: # if a birthday or range

            if "years" in age: # Every range contains the word 'years'.
                # Most ranges are of the form age-age, but some are age+
                age = "" # Ignore ranges for now

            else: # The value is a birth day

                bday = cn.convertDate(age, False) # Will standardize the date to iso and check
                                                  # if it's a valid date.

                if bday != -1:

                    dates = str(bday).split("-")

                    birthdate = [int(float(d)) for d in dates]

                # else: date is invalid

                if not pd.isnull(yearTaken):

                    # yearTaken is stored as a float for w/e reason in the csv
                    age = int(float(yearTaken)) - int(dates[0])

                    # One of the dates the sample was taken is 2011 and the age is 2010
                    age = 0 if age < 0 else age

                else:
                    age = NOW.year - int(bday[:yearLen]) # Use todays year for the age

        # end if len(age) > ageLen

    else:
        age = ""

    return age, birthdate

####################################################################################################
# createTravelTriples
#
# A patient's travel info is in column 'Comments' and is of the form 'Travel: [location]'.
# Sometimes it's just the country, or the province/state, or both. We will store only the lowest
# level. eg from the location value 'Ohia, USA' we will store only Ohio as it is derivable that
# the patient traveled to the states.
####################################################################################################
def createTravelTriples(df, row, hum):

    humTriple = ""

    trTriple = "" # Travel info triple

    travel = df["Comments"][row] # All travel info is in the comments column

    # We will keep the lowest level of ganularity, eg from 'Ohio, USA' we'll keep only Ohio as
    # USA is derivable (consider revising).

    # All travel values are prefixed with 'Travel: '
    if not pd.isnull(travel) and "Travel" in travel:

        travel = travel.replace("Travel:", "").strip() # Remove the 'Travel:' prefix

        # Some values are suffixed with a bunch of meaningless(ful?) stuff
        end = re.search("[;,]", travel)
        travel = travel[:end.span()[0]] if end is not None else travel

        if travel in SUBNATS:
            trTriple = ctm.indTriple(travel, "SubNational")

        if travel in COUNTRIES:
            trTriple = ctm.indTriple(travel, "Country")

        trTriple += ctm.propTriple(travel, {"hasName":travel}, True)
        humTriple = ctm.propTriple(hum, {"traveledTo":travel})

    return trTriple + humTriple

####################################################################################################
# createHumanTriples
#
# Create an individual human for all isolates that have a human as a source. No names are given so
# the unique id for humans is 'patient_[isoTitle]'. Note all humans in the csv are patients so they
# will be instances of the Patient class. Here we will also get the properties postal code if
# available and gender if available. We also get set the clinical sample type here.
####################################################################################################
def createHumanTriples(df, row, isoTitle):

    type_ = ""
    isoTriple = ""
    humTriple = ""

    humTitle = "patient"

    name = "patient"

    gender = df["Gender"][row]

    postalCode = df["Postal code"][row]

    sTypeA = df["Source_Specific_2"][row] # The clinical sample type

    sTypeB = df["Clinical Sample Type"][row] # Also has clinical sample type

    # The age is stored in a column with birthdays and other random crap so we'll
    # handle it separately
    age, birthdate = getAge(df, row)

    # The values 0, m, f, male, female and 'not given' are in the csv. We won't add the
    # prop if it's 'not given'
    if not pd.isnull(gender) and cn.isGoodVal(gender) and gender != 0:

        gender = gender.lower()

        # some of the genders in the csv are 'male' while others are just 'm'.
        # same goes for female
        g = gender[0]

        humTitle = "{} {}".format(humTitle, isoTitle)

        # we don't want the name to be 'f patient', we want 'female patient'
        gender = "female" if g == "f" else "male"

        name = "{} {}".format(gender, name)

    else:
        g = ""

    if not pd.isnull(postalCode):

        p = postalCode

        humTitle = "{} {}".format(p, humTitle)

        # we won't add the postal code to the name

    else:
        p = ""

    humTitle = "{} {}".format(age, humTitle) if age else humTitle

    # If sTypeA is nan, try sTypeB
    typeCol = sTypeA if not pd.isnull(sTypeA) else sTypeB

    if not pd.isnull(typeCol) and cn.isGoodVal(typeCol):

        if re.search("[Ss]tool", typeCol) is not None:
            type_ = "stool"
        if re.search("[Bl]ood", typeCol) is not None:
            type_ = "blood"

     # type could still be "" as not all the values for sTypeA (Source_Specific_2) are
     # clinical sample types, i.e. 'blood' or 'stool'
    if type_:

        isoTriple += ctm.indTriple(humTitle, type_)

        name = "{} {}".format(name, type_)

    if birthdate:

        humTriple += ctm.propTriple(humTitle, {"hasBirthDay":birthdate[2],
                                               "hasBirthMonth":birthdate[1],
                                               "hasBirthYear":birthdate[0]}, True, True)

    humTriple += ctm.indTriple(humTitle, "Patient") # All human samples in the csv are patients

    # Travel info is in the column 'comments' and it's quite messy so we'll
    # handle it separately
    humTriple += createTravelTriples(df, row, humTitle)

    humTriple += ctm.propTriple(humTitle, {"hasAge":int(age)}, True, True) if age else ""

    humTriple += ctm.propTriple(humTitle, {"hasGender":g}, True, True) if g else ""

    humTriple += ctm.propTriple(humTitle, {"hasPostalCode":postalCode}, True, True) if p else ""

    humTriple += ctm.propTriple(humTitle, {"hasName":name}, True, False)

    isoTriple += ctm.propTriple(isoTitle, {"hasSampleSource":humTitle})

    return humTriple + isoTriple

####################################################################################################
# createEnviroTriples
# Creates an instance of Environment for every isolate that has an environmental source type. We
# don't bother uniquely identifying different environment sources; this is just so the user knows
# what type of environment the source came from. We would consider revising this if enviro sources
# had an ID. Though really the enviro's unique ID is the sampling site name or body of water name
# which we fetch in the function createLocation triples.
####################################################################################################
def createEnviroTriples(df, row, isoTitle):

    enviroTriple = ""
    isoTriple = ""

    enviro = cn.remPrefix(df["Source General"][row], 2) # Water, lagoon, sewage, sand, unknown

    enviroSpec = df["Source_Specific_2"][row] # Lagoon:Dairy, Sewage (treated) etc.

    # If enviroSpec (the source specific 2 value) is actually something meaningful, it will be an
    # instance of the class enviro, eg 'Swine' is an instance of the class 'Lagoon', 'Treated'
    # is an instance of 'Sewage'. For other random enviroSpec values, like 'other', 'water' (when
    # we already have water as the enviro value), the instance will just be the name of the class.
    # The enviro value 'sand' is special in that it is not a class in ontology, it will be an
    # instance of the class 'Substrate'. Future soil samples can go in this class too if need be.

    if not pd.isnull(enviro) and cn.isGoodVal(enviro):
        # enviro (Source general) is the class and enviroSpec (source specific 2) is the instance.

        if not pd.isnull(enviroSpec) and cn.isGoodVal(enviroSpec):

            # Have to clean enviroSpec strings a bit
            if re.search("[Tt]reated", enviroSpec) is not None: # For the value 'Sewage (Treated)'

                enviroSpec = "treated" # Don't need redundant info

            if "water" in enviroSpec.lower():

                # EnviroSpec is "drinking water source water","recreational water" or Core water
                # site (ignore Core Water Site)
                if enviroSpec != "Water" and enviroSpec != "Core water site":

                    enviroSpec = enviroSpec.replace(" water", "")
                    enviroSpec = "{} {}".format(enviroSpec, "water")

                else:
                    enviroSpec = enviro # We don't really need this as enviroSpec already
                                        # equals water. But whatever ya know

            # EnviroSpec is "Lagoon: Swine" or "Lagoon:Dairy"
            if re.search("[Ll]agoon", enviroSpec) is not None:

                # Get rid of redundant info
                enviroSpec = "{} lagoon".format(enviroSpec.replace("Lagoon:", ""))

        else: # We know the environment type (enviro) but EnviroSpec is nan or 'Other'
            enviroSpec = enviro

        # Sand is a special case for enviro as sand is not a class but an instance of Substrate
        if re.search("[Ss]and", enviro) is not None:

            enviro = "Substrate"
            enviroSpec = "sand"

    else: # We know it's an environmental source, we don't know the environment type (enviro)
          # or the specific environment source (enviroSpec). Note that source specific 2 is
          # empty if source general is too.

        enviro = "Environment"
        enviroSpec = "unknown environment" # No unique identifier is needed here


    title = enviroSpec.lower()

    enviroTriple = ctm.indTriple(title, enviro) + ctm.propTriple(title, {"hasName":title}, True)

    isoTriple = ctm.propTriple(isoTitle, {"hasSampleSource":title})

    return enviroTriple + isoTriple

####################################################################################################
# isDomestic
#
# Returns True if the given animal is a domestic animal.
####################################################################################################
def isDomestic(sourceSpec, animal, family):

    domestic = None

    if not pd.isnull(sourceSpec):

        sourceSpec = sourceSpec.lower()

        domestic = True if "domestic" in sourceSpec else domestic
        domestic = False if "wild" in sourceSpec else domestic

    # The values miscWild and miscDomestic are in the Source General column (family)
    if family == "MiscWild":
        domestic = False

    if family == "MiscDomestic":
        domestic = True

    if not pd.isnull(animal):

        animal = animal.lower()

        domestic = False if "wild bird" in animal else domestic

        # Handle the domestic type of animal cases
        domestic = True if animal in ("cattle", "chicken", "dog", "sheep", "cat") else domestic

        # Handle the wild type of animal cases
        domestic = False if animal in ("bear", "canada goose") else domestic

    return domestic

####################################################################################################
# createAnimalTriples
#
# Creates instances of the Animal class for every isolate that has an animal as a source.
# Sometimes we know the source is an animal but we don't the family or animal. In this case we say
# the animal type is 'unknown' and it just becomes an instance of the Animal class. Sometimes we
# know the family but not the animal type in which case unknown is an instance of family. When we
# do know the animal type, there are properties attached to animals found all over the csv
# and many nice to work with, totally random cases, we have to handle.
####################################################################################################
def createAnimalTriples(df, row, isoTitle):

    isoTriple = ""
    animalTriple = ""
    taxoGenus = ""
    dairy = None
    beef = None

    sourceSpec = df["Source_Specific_2"][row] # That pesky source specific 2 column

    family = cn.remPrefix(df["Source General"][row], 2) # Avian, Ruminant etc.

    sex = df["Gender"][row]

    id_ = df["Animal ID"][row] # If the animal has an id, this will be its URI

    # The actual animal, eg chicken, racoon etc.
    animal = cn.remPrefix(df["Source_Specific_1"][row], 2)

    ageRank = df["Patient D.O.B / Age"][row] # Juvenile, Adult

    domestic = isDomestic(sourceSpec, animal, family)

    # An animal, say chicken, will become an instance of family (Avian in this case), and Chicken,
    # for example. Then Chicken will become a subclass of Avian. The individuals URI will be
    # animal+isoTitle

    if pd.isnull(family): # We know the source is an Animal but we don't know the family or type
                          # of animal. So it just becomes an instance of the animal class and is
                          # named 'unknown' (unless it has an id)

        animal = "unknown animal"
        family = "Animal"

    else: # We know the family

        if not pd.isnull(animal):

            animal = animal.lower()

            family = family.lower()

            animal = "cattle" if animal == "cow" else animal

            # Handle the MiscDomestic, and MiscWild family cases
            if "misc" in family:

                birds = ("trumpeter swan", "mute", "bufflehead", "scaup", "canada goose")

                is_bird = any(True if b in animal else False for b in birds)

                # Give families do all the MiscWild and MiscDomestic animals. A lot of
                # random cases here we need to handle.
                if is_bird:
                    family = "Avian"

                elif "small mammal" in animal:
                    animal = "unknown mammal"
                    family = "Animal"

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
                    family = "Animal"
                    animal = "unknown animal"

                else: # racoons, skunks, and llama/alpaca
                    family = "Animal"

            # There are the values Wild Bird, goat/sheep, alpaca/llama in source specific 1
            if "wild bird" in animal:
                animal = "unknown avian" # Wild bird has the family avian
            if "/" in animal:
                animal = animal.split("/")[0]

            # Source Specific 2 has more specific animals sometimes and also domestic/wild info
            if not pd.isnull(sourceSpec):

                sourceSpec = sourceSpec.lower()

                if "heifer" in sourceSpec:
                    animal = "heifer"

                if "dairy" in sourceSpec:
                    dairy = True

                if "beef" in sourceSpec:
                    beef = True

                if "shore bird" in sourceSpec:
                    animal = "shore bird"

        else: # We know the family but not the animal
            animal = "unknown animal"

    if not pd.isnull(id_) and cn.isGoodVal(id_):
        id_ = cn.cleanInt(id_)
    else:
        id_ = ""

    if pd.isnull(sex) or not cn.isGoodVal(sex) or not (sex[0] == "M" or sex[0] == "F"):
        sex = ""

    if pd.isnull(ageRank) or not ("juvenile" in ageRank or "adult" in ageRank):
        ageRank = ""

    ################################################################################################
    # createTypeTriples
    #
    # Here we put animals under different sample type classes. So an animal source will be an
    # instance of whatever kind of animal it is, and whatever sample type it is. EG chicken_1205
    # is an instance of Chicken and could be an instance of Droppings.
    ################################################################################################
    def createTypeTriples(title):

        stTriple, cut, byprod, fae = "", "", "", ""

        seasoned, skinless, is_rinse, is_ground = None, None, None, None

        sampleType = df["Sample Type 2"][row] # Faecel, Abbatoir, Retail, Egg

        sourceSpec = df["Source_Specific_2"][row] # chickenBreast, carcass, rectal swab etc.

        name = animal

        # Insects don't have sample types
        if not pd.isnull(sampleType) and cn.isGoodVal(sampleType) and sampleType != "Insect":

            sampleType = sampleType.lower()

            name = "{} {}".format(sampleType, animal)

            name = "{} {}".format(animal, "feces") if sampleType == "faecal" else name

            if not pd.isnull(sourceSpec):

                sourceSpec = sourceSpec.lower()

                # The source specific 2 for animal sample types is really messy. It's just
                # easier to hard code values in
                cut = "breast" if "breast" in sourceSpec else ""
                cut = "thigh" if "thigh" in sourceSpec else cut
                cut = "ground" if "ground" in sourceSpec else cut
                cut = "loin" if "loin" in sourceSpec else cut

                byprod = "caecum" if "caecum" in sourceSpec else ""
                byprod = "carcass" if "carcass" in sourceSpec else byprod
                byprod = "weep" if "weep" in sourceSpec else byprod

                fae = "droppings" if "field sample" in sourceSpec else ""
                fae = "pit" if "pit" in sourceSpec else fae
                fae = "swab" if "swab" in sourceSpec else fae

                name = "{} {} {}".format(sampleType, animal, cut) if cut else name
                name = "{} {} {}".format(sampleType, animal, byprod) if byprod else name
                name = "{} {}".format(animal, fae) if fae else name

                # sourceSpec has info related to the properties of meat (ie cuts or abattoir caecum)
                if "non-seasoned" in sourceSpec:

                    # The only non-seasoned cut in the csv is pork loin
                    name = "non-seasoned pork loin"

                    seasoned = False

                if "skin" in sourceSpec:

                    if "skinless" in sourceSpec:

                        name = "{} {} {} {}".format(sampleType, "skinless", animal, cut)

                        skinless = True

                    else:

                        name = "{} {} {} {}".format(sampleType, animal, cut, "with skin")

                        skinless = False

                if "rinse" in sourceSpec:

                    name = "{} {} {} {}".format(sampleType, animal, cut, "rinse") if cut else name

                    name = "{} {} {} {}"\
                    .format(sampleType, animal, byprod, "rinse") if byprod else name

                    is_rinse = True

                if "ground" in sourceSpec:

                    a_name = "beef" if animal == "cattle" else animal

                    name = "{} {} {}".format(sampleType, "ground", a_name)

                    is_ground = True

            # endif not pd.isnull(sourceSpec):

            locale = sampleType if sampleType != "faecal" else ""

            if sampleType == "egg":

                locale = "Farm"

                name = "{} {} {}".format("farm", animal, "egg")

                stTriple += ctm.indTriple(title, "Egg")

            stTriple += ctm.indTriple(title, byprod) if byprod else ""

            stTriple += ctm.indTriple(title, cut) if cut else ""

            # All retail samples are assumed to be cuts, unless the byprod is specified
            stTriple += ctm.indTriple(title, "Cut")\
                        if not cut and not byprod and sampleType == "retail" else ""

            stTriple += ctm.indTriple(title, fae) if fae else ""

            stTriple += ctm.propTriple(title, {"hasSampleLocale":locale.lower()}, True, True)\
                        if locale else ""

            #stTriple += ctm.indTriple(animalTitle, stClass)

        # endif not pd.isnull(sampleType) and cn.isGoodVal(sampleType) and sampleType != "Insect"

        stTriple += \
        ctm.propTriple(title, {"isGround":is_ground}, True, True) if is_ground is not None else ""

        stTriple += \
        ctm.propTriple(title, {"isRinse":True}, True, True) if is_rinse is not None else ""

        stTriple += \
        ctm.propTriple(title, {"isSeasoned":seasoned}, True, True) if seasoned is not None else ""

        stTriple += \
        ctm.propTriple(title, {"isSkinless":skinless}, True, True) if skinless is not None else ""

        stTriple += ctm.propTriple(title, {"hasName":name}, True)

        return stTriple


    title = "{}_{}".format(animal, isoTitle)

    animalTriple += createTypeTriples(title)

    # animal becomes an instance of animal
    animalTriple += \
    ctm.indTriple(title, animal) if "unknown" not in animal else ""

    animalTriple += \
    ctm.propTriple(title, {"isDomestic":domestic}) if domestic is not None else ""

    animalTriple += \
    ctm.propTriple(title, {"hasTaxoGenus":taxoGenus}, True, True) if taxoGenus else ""

    animalTriple += \
    ctm.propTriple(title, {"hasAgeRank":ageRank}, True, True) if ageRank else ""

    animalTriple += \
    ctm.propTriple(title, {"hasSex":sex}, True, True) if sex else ""

    animalTriple += \
    ctm.propTriple(title, {"isBeefCattle":True}, True, True) if beef else ""

    animalTriple += \
    ctm.propTriple(title, {"isDairyCattle":True}, True, True) if dairy else ""

    animalTriple += \
    ctm.propTriple(title, {"hasAnimalID":id_}, True, True) if id_ else ""

    animalTriple += ctm.indTriple(title, family)

    isoTriple += ctm.propTriple(isoTitle, {"hasSampleSource":title})

    return animalTriple + isoTriple


####################################################################################################
# createSourceTriples
#
# Here we call functions to create all triples associated with the source of the isolate
####################################################################################################
def createSourceTriples(df, row, isoTitle):

    resultTriple = ""

    sample = df["Sample Type"][row] # animal, human or environmental (and Reference Strain but
                                    # that's handled when we to the project triples as every
                                    # reference strain is mentioned in that column but sometimes
                                    # not this one (SampleType)).

    if sample == "Animal":

        resultTriple += createAnimalTriples(df, row, isoTitle)

    if sample == "Environmental":

        resultTriple += createEnviroTriples(df, row, isoTitle)

    if sample == "Human":

        resultTriple += createHumanTriples(df, row, isoTitle)

    return resultTriple
