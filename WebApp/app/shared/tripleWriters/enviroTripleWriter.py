from Scripts.tripleWriters.campyTM import CAMPY as ctm

def enviroTripleWriter(data, iso_title):

    triple = []

    e_prop = data["enviro_prop"]

    enviro = data["enviro"]

    e_title = "{} {}".format(e_prop, enviro) if e_prop else enviro

    triple.append(ctm.indTriple(e_title, enviro))
    triple.append(ctm.propTriple(e_title, {"hasName":e_title}, True))
    triple.append(ctm.propTriple(iso_title, {"hasEnviroSource":e_title}))

    return "".join(triple)