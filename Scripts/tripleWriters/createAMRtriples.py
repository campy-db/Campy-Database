import sys
sys.path.append("/home/student/Campy/CampyDatabase")

from Scripts import cleanCSV as cn
from Scripts.TripleMaker import TripleMaker as tm
import pandas as pd
from campyTM import campy as ctm
from labTM import lab as ltm

def createAMRtriples(df, row, isoTitle):
    
    def mic_triple(mic_value, drug, test_title):

        mic = str(float(mic_value)) if cn.isNumber(mic_value) else str(mic_value)
        dm_title = "{}_{}".format(mic, drug)
        
        triple = ltm.indTriple(dm_title, "DrugMIC") + \
                 ltm.propTriple(dm_title, {"hasMIC": mic}, True, True) + \
                 ltm.propTriple(dm_title, {"hasDrug": drug}) + \
                 ltm.propTriple(test_title, {"foundMIC": dm_title})

        return triple
    
    def res_triple(res, drug, test_title):
    	
        if int(res): # if resistant
	    	out = ltm.propTriple(test_title, {"foundResistanceTo": drug})
        else:
            out = ltm.propTriple(test_title, {"foundSusceptibiltyTo": drug})
        return out

    df_row = df.loc[row]
    
    mic_indices = range(df.columns.get_loc("mic_azm"), df.columns.get_loc("mic_tet") + 1)
    
    r_indices = range(df.columns.get_loc("razm"), df.columns.get_loc("rtet") + 1)

    drugs = [df.columns.values[d].replace("mic_", "") for d in mic_indices]

    amr = df_row["AMR"]

    test_title = "amr_" + isoTitle 

    # create MIC triples
    # NOTE: All mics are being stored as strings in the ontology as some of the mics have
    # < or > in them. We don"t like this.
    mic_triples = [mic_triple(df_row[m], drug, test_title)
                   for m, drug in zip(mic_indices, drugs) 
                   if not pd.isnull(df_row[m])]
    
    # create resistance pattern triples
    res_triples = [res_triple(df_row[r], drug, test_title)
                   for r, drug in zip(r_indices, drugs)
                   if not pd.isnull(df_row[r])]

    if not pd.isnull(amr): # secondary source of resistance triples
        res_triples.append(ltm.propTriple(test_title, {"foundResistanceTo": amr.split(" ")[0]})) 
    
    triples = mic_triples + res_triples # merge lists

    if triples: # if data were not empty add URIs, etc
        triples += [ ltm.indTriple(test_title,"AMRtest"), 
                     tm.multiURI((isoTitle,"hasLabTest",test_title),(ctm.uri,ctm.uri,ltm.uri)) ]

    return "".join(triples)
