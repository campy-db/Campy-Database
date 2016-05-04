def getBreakpoints(species):
    if (species.lower() == "jejuni"):
        return resistantBreakpointJejuni
    elif (species.lower() == "coli"):
        return resistantBreakpointColi
    else:
        return ""

resistantBreakpointJejuni = {"azm":0.5, "chl":32.0,
                               "cip":1.0, "cli":1.0, 
                               "ery":8.0, "flr":8.0,
                               "gen":4.0, "nal":32.0,
                               "tel":8.0, "tet":2.0}

resistantBreakpointColi = {"azm":0.5, "chl":32.0,
                             "cip":1.0, "cli":1.0, 
                             "ery":8.0, "flr":8.0,
                             "gen":4.0, "nal":32.0,
                             "tel":8.0, "tet":2.0}


