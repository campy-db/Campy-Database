"""
 form_to_triple.py

 Here we handle all the fields in the AddForm, and pass it to the clean_triple_writers.
 We cast all fields to their appropriate type and then create a dictionary of all the data,
 whether the field is empty or not.

"""

from .shared.valid_values import ANIMALS, SAMPLE_TYPES, SAMPLE_PROPS, ENVIROS, ENVIRO_PROPS, PEOPLE,\
                                CLINICAL_TYPES
from .shared.tripleWriters import *
from .shared.extractValue import *
from .createInitialTriples import createInitialTriples

####################################################################################################
# formToTriple
#
# Take all the fields from the AddForm and pass it to clean_triple_writers.
####################################################################################################
def formToTriple(form):
    triple = []

    iso_title = str(form.name.data)

    spec_str = str(form.spec.data) if form.spec.data else ""

    triple.append(createIsolateTriple(iso_title, spec_str))
    triple.append(createDTakenTriple(iso_title, form.date.data))
    def formProj():
        data = {"Project Name":str(form.projName.data),
                "Subproject Name":str(form.subprojName.data)}
        return createProjTriple(data, iso_title)


    def formTyping():
        aGenes = {field.description:str(field.data) for field in form.aGenes}
        mlstGenes = {field.description:str(field.data) for field in form.mlstGenes}
        data = {"Clonal Complex":str(form.clonalComplex.data),
                "ST":str(form.st.data),
                "aGenes":aGenes,
                "mlstGenes":mlstGenes}
        return createTypingTriple(data,iso_title)
        #return createMLSTTriple(iso_title, form.mlst.data)
    def formOutbreak():
        data = {"name":form.outbreakName.data,
                "lower":form.outbreakDateLowerBound.data,
                "upper":form.outbreakDateUpperBound.data}
        return createOutbreakTriple(iso_title, data)

    def formSMA1():
        pulsovar = form.sma1.data
        return createSMATriple(iso_title, pulsovar)

    def formSerotype():
        serotype = str(form.serotype.data) if form.serotype.data else ""
        antigen = str(form.antigen.data) if form.antigen.data else ""
        serotypes = serotype.split(",")
        triples = ""
        for s in serotypes:
            print("s value IS " + s)
            triples += createSeroTriple(iso_title, s, antigen)
        return triples

    ################################################################################################
    # Get all the CGF data from the form
    ################################################################################################
    def formCGF():

        fp = str(form.fp.data) if form.fp.data else ""
        dcy = int(form.dcy.data) if form.dcy.data else ""
        dcm = int(form.dcm.data) if form.dcm.data else ""
        dcd = int(form.dcd.data) if form.dcd.data else ""
        lab = str(form.lab.data) if form.lab.data else ""
        silico = bool(form.silico.data) if form.silico.data else ""

        cgf_data =\
        {"fingerprint":fp, "year":dcy, "month":dcm, "day":dcd, "lab":lab, "silico":silico}

        return createCGFTriple(cgf_data, iso_title)

    ################################################################################################
    # Get all the CGF data from the form
    ################################################################################################
    def formDrugResistance():
        azm = str(form.azm.data) if form.azm.data else ""
        chl = str(form.chl.data) if form.chl.data else ""
        cip = str(form.cip.data) if form.cip.data else ""
        cli = str(form.cli.data) if form.cli.data else ""
        ery = str(form.ery.data) if form.ery.data else ""
        flr = str(form.flr.data) if form.flr.data else ""
        gen = str(form.gen.data) if form.gen.data else ""
        nal = str(form.nal.data) if form.nal.data else ""
        tel = str(form.tel.data) if form.tel.data else ""
        tet = str(form.tet.data) if form.tet.data else ""

        drug_data = {"azm":azm, "chl":chl,
                    "cip":cip, "cli":cli, 
                    "ery":ery, "flr":flr,
                    "gen":gen, "nal":nal,
                    "tel":tel, "tet":tet}
        return createDrugResistanceTriple(drug_data, iso_title, spec_str)


    ################################################################################################
    # Get all the source data from the form
    ################################################################################################
    def formSource():

        ############################################################################################
        # Get all the animal source data
        ############################################################################################
        def formAnimalSource(animal, source):

            type_ = getType(source)
            type_prop = getTypeProp(source)

            aID = str(form.aID.data) if form.aID.data else ""
            locale = str(form.sourceLocale.data) if form.sourceLocale.data else ""
            sex = str(form.sex.data) if form.sex.data else ""
            aage = str(form.aage.data) if form.aage.data else ""

            animal_data = {"animal":animal,
                           "type":type_,
                           "type_prop":type_prop,
                           "aID":aID, "locale":locale,
                           "sex":sex, "age":aage}

            return createAnimalTriple(animal_data, iso_title)

        ############################################################################################
        # Get the environment source data
        ############################################################################################
        def formEnviroSource(enviro, source):

            enviro_prop = getEnviroProp(source, )

            enviro_data = {"enviro":enviro, "enviro_prop":enviro_prop}

            return createEnviroTriple(enviro_data, iso_title)

        ############################################################################################
        # Get the human source data
        ############################################################################################
        def formHumanSource(human, source):

            clinical_type = getClinicalType(source)

            age = int(form.hage.data) if form.hage.data else ""
            travel = str(form.travel.data) if form.travel.data else ""
            postal_code = str(form.postal_code.data) if form.postal_code.data else ""
            gender = str(form.hsex.data) if form.hsex.data else ""
            pID = str(form.pID.data) if form.pID.data else ""

            human_data = {"human":human,
                          "clinical_type":clinical_type,
                          "postal_code":postal_code,
                          "travel":travel,
                          "age":age,
                          "gender":gender,
                          "pID":pID}

            return createHumanTriple(human_data, iso_title)


        source = str(form.source.data)

        # Because source can contain an animal, enviro, or human source, we have to determine which
        # one and make the appropriate triples
        if not source:
            return ""
        else:
            animal = getAnimal(source)
            enviro = getEnviro(source)
            human = getPerson(source)

            if animal:
                return formAnimalSource(animal, source)
            if enviro:
                return formEnviroSource(enviro, source)
            if human:
                return formHumanSource(human, source)

    triple.append(" ".join([formCGF(), formDrugResistance(), formSource(), formSerotype(), formOutbreak(), formTyping(), formProj(), createDAddedTriple(iso_title)]))

    return "".join(triple)
