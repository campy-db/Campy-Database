from Scripts.tripleWriters.campyTM import CAMPY as ctm
from WebApp.app.util import *

def animalTripleWriter(data, iso_title):

    triple = []

    animal, locale, type_, type_prop = data["animal"],\
                                       data["locale"],\
                                       data["type"],\
                                       data["type_prop"]

    a_title = "{}_{}".format(animal, iso_title) if animal else ""

    name = "{} {}".format(locale, animal) if locale else animal

    rlit_props = popVals({"hasAnimalID":data["aID"],
                          "hasSex":data["sex"],
                          "hasAgeRank":data["age"]})

    if animal:
        triple.append(ctm.indTriple(a_title, animal))
        triple.append(ctm.propTriple(a_title, {"hasName":name}, True))
        triple.append(ctm.propTriple(iso_title, {"hasAnimalSource":a_title}))

    if rlit_props:
        triple.append(ctm.propTriple(a_title, rlit_props, True, True))

    if locale:
        triple.append(ctm.propTriple(iso_title, {"hasSampleLocale":locale}, True, True))

    if type_:

        # Sample type naming convention is "[locale_]type[_prop]"
        s_title = "{} {}".format(locale, type_) if locale else type_
        s_title = "{} {}".format(s_title, type_prop) if type_prop else s_title

        sample_triple = ctm.indTriple(s_title, type_) +\
                        ctm.propTriple(s_title, {"hasName":s_title}, True)

        triple.append(sample_triple)
        triple.append(ctm.propTriple(iso_title, {"hasSampleType":s_title}))

    return "".join(triple)