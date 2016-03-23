import clean_tripleWriters as ctw

def formToTriple(form):

    isoTitle = str(form.name.data)
    triple = ctw.createIsolateTriple(isoTitle)

    spec = str(form.spec.data) if form.spec.data else ""


    def form_source():

        source = str(form.source.data) if form.source.data else ""

        return ctw.createSourceTriple(source, isoTitle)


    def form_CGF():

        fp = long(form.fp.data) if form.fp.data else ""
        dcy = int(form.dcy.data) if form.dcy.data else ""
        dcm = int(form.dcm.data) if form.dcm.data else ""
        dcd = int(form.dcd.data) if form.dcd.data else ""
        lab = str(form.lab.data) if form.lab.data else ""
        vitro = bool(form.vitro.data) if form.vitro.data else ""

        cgfData = {"fingerprint":fp, "year":dcy, "month":dcm, "day":dcd, "lab":lab, "vitro":vitro}
        return ctw.createCGFtriple(cgfData, isoTitle)


    def form_AnimalSource():

        aID = str(form.aID.data) if form.aID.data else ""
        sex = str(form.sex.data) if form.sex.data else ""
        isDom = bool(form.domestic.data).lower() if form.domestic.data else ""
        aage = str(form.aage.data) if form.aage.data else ""

        animalData = {"id":aID, "sex":sex, "domestic":isDom, "age":aage}
        return ctw.createAnimalTriple(animalData, isoTitle)

    triple += form_CGF() +\
              form_source() +\
              form_AnimalSource()

    return triple
    