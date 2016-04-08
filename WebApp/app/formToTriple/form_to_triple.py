"""
 form_to_triple.py
"""

from ..util.valid_values import ANIMALS, SAMPLE_TYPES
from . import clean_triple_writers as ctw

def formToTriple(form):

    triple = []

    iso_title = str(form.name.data)

    specs = str(form.spec.data).split("subspecies") if form.spec.data else ""

    spec = specs[0] if specs else ""
    subspec = specs[1] if specs and len(specs) > 1 else ""

    triple.append(ctw.createIsolateTriple(iso_title, spec, subspec))


    def formCGF():

        fp = str(form.fp.data) if form.fp.data else ""
        dcy = int(form.dcy.data) if form.dcy.data else ""
        dcm = int(form.dcm.data) if form.dcm.data else ""
        dcd = int(form.dcd.data) if form.dcd.data else ""
        lab = str(form.lab.data) if form.lab.data else ""
        silico = bool(form.silico.data) if form.silico.data else ""

        cgf_data =\
        {"fingerprint":fp, "year":dcy, "month":dcm, "day":dcd, "lab":lab, "silico":silico}

        return ctw.createCGFtriple(cgf_data, iso_title)

    def formAnimalSource():

        aID = str(form.aID.data) if form.aID.data else ""
        animal = getAnimal(str(form.source.data)) if form.source else ""
        type_ = getType(str(form.source.data)) if form.source else ""
        locale = str(form.sourceLocale.data) if form.sourceLocale.data else ""
        sex = str(form.sex.data) if form.sex.data else ""
        aage = str(form.aage.data) if form.aage.data else ""

        animal_data =\
        {"animal":animal, "type":type_, "aID":aID, "locale":locale, "sex":sex, "age":aage}

        return ctw.createAnimalTriple(animal_data, iso_title)

    triple.append(" ".join([formCGF(), formAnimalSource()]))

    return "".join(triple)


def getAnimal(a):

    vals = [v.lower().replace("_", " ") for v in a.split(" ")]

    animal = ""

    for v in vals:
        animal = v if v in ANIMALS else animal

    return animal

def getType(s):

    vals = [v.lower().replace("_", " ") for v in s.split(" ")]

    type_ = ""

    for v in vals:
        type_ = v if v in SAMPLE_TYPES else type_

    return type_

