import sys
sys.path.append("/home/student/CampyDB/CampyDatabase/WebApp/app")

from util.valid_values import animals, sample_types
import clean_tripleWriters as ctw

def formToTriple(form):

    isoTitle = str(form.name.data)
    triple = ctw.createIsolateTriple(isoTitle)

    spec = str(form.spec.data) if form.spec.data else ""

    def formCGF():

        fp = str(form.fp.data) if form.fp.data else ""
        dcy = int(form.dcy.data) if form.dcy.data else ""
        dcm = int(form.dcm.data) if form.dcm.data else ""
        dcd = int(form.dcd.data) if form.dcd.data else ""
        lab = str(form.lab.data) if form.lab.data else ""
        silico = bool(form.silico.data) if form.silico.data else ""

        cgfData = {"fingerprint":fp, "year":dcy, "month":dcm, "day":dcd, "lab":lab, "silico":silico}
        return ctw.createCGFtriple(cgfData, isoTitle)

    def formAnimalSource():

        aID = str(form.aID.data) if form.aID.data else ""
        animal = getAnimal(str(form.source.data)) if form.source else ""
        type = getType(str(form.source.data)) if form.source else ""
        locale = str(form.sourceLocale.data) if form.sourceLocale.data else ""
        sex = str(form.sex.data) if form.sex.data else ""
        aage = str(form.aage.data) if form.aage.data else ""

        animalData = {"animal":animal, "type":type, "aID":aID, "locale":locale, "sex":sex, "age":aage}
        return ctw.createAnimalTriple(animalData, isoTitle)

    triple += formCGF() + formAnimalSource()

    return triple


def getAnimal(a):

    vals = [ v.lower().replace("_", " ") for v in a.split(" ") ]

    animal = ""

    for v in vals:
        animal = v if v in animals else animal
    
    return animal

def getType(st):

    vals = [ v.lower().replace("_", " ") for v in st.split(" ") ]

    type = ""

    for v in vals:
        type = v if v in sample_types else type
    
    return type


    
