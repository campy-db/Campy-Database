import sys
sys.path.append("/home/student/CampyDB/CampyDatabase/WebApp/app")

from util.validValues import animals as animals
import clean_tripleWriters as ctw

def formToTriple(form):

    isoTitle = str(form.name.data)
    triple = ctw.createIsolateTriple(isoTitle)

    spec = str(form.spec.data) if form.spec.data else ""


    def form_source():

        source = str(form.source.data) if form.source.data else ""

        return ctw.createSourceTriple(source, isoTitle)


    def form_CGF():

        fp = str(form.fp.data) if form.fp.data else ""
        dcy = int(form.dcy.data) if form.dcy.data else ""
        dcm = int(form.dcm.data) if form.dcm.data else ""
        dcd = int(form.dcd.data) if form.dcd.data else ""
        lab = str(form.lab.data) if form.lab.data else ""
        silico = bool(form.silico.data) if form.silico.data else ""

        cgfData = {"fingerprint":fp, "year":dcy, "month":dcm, "day":dcd, "lab":lab, "silico":silico}
        return ctw.createCGFtriple(cgfData, isoTitle)


    def form_AnimalSource():

        aID = str(form.aID.data) if form.aID.data else ""
        animal = get_animal(str(form.source.data)) if form.source else ""
        type = str(form.sourceType.data) if form.sourceType.data else ""
        sex = str(form.sex.data) if form.sex.data else ""
        aage = str(form.aage.data) if form.aage.data else ""

        animalData = {"animal":animal, "aID":aID, "type":type, "sex":sex, "age":aage}
        return ctw.createAnimalTriple(animalData, isoTitle)

    triple += form_CGF() +\
              form_source() +\
              form_AnimalSource()

    return triple


def get_animal(a):

    vals = [ v.lower().replace("_", " ") for v in a.split(" ") ]

    animal = ""

    for v in vals:
        animal = v if v in animals else animal
    
    return animal
    
