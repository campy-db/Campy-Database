from Scripts.tripleWriters.labTM import LAB as ltm
def createSeroTriples(isoTitle, serotype, antigen):
    triple = ""
    title = "sero_{}".format(isoTitle)
    seroTitle = "{}_{}".format(serotype, antigen)
    triple += ltm.indTriple(seroTitle, "Serotype_test")
    triple += ltm.propTriple(seroTitle, {"hasSerotype":"0"}, True, True)
    triple += ltm.propTriple(seroTitle, {"hasAntigen":"O"})
    triple += ltm.propTriple(title, {"foundSerotype":seroTitle})

    return triple

