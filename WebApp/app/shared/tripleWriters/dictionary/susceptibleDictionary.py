def getBreakpoints(species):
    if (species.lower() == "jejuni"):
        return susceptibleBreakpointJejuni
    elif (species.lower() == "coli"):
        return susceptibleBreakpointColi
    else:
        return ""

susceptibleBreakpointJejuni = {"azm":0.25, "chl":16.0,
                               "cip":0.5, "cli":0.5, 
                               "ery":4.0, "flr":4.0,
                               "gen":2.0, "nal":16.0,
                               "tel":4.0, "tet":1.0}

susceptibleBreakpointColi = {"azm":0.5, "chl":16.0,
                             "cip":0.5, "cli":1.0, 
                             "ery":8.0, "flr":4.0,
                             "gen":2.0, "nal":16.0,
                             "tel":4.0, "tet":2.0}


