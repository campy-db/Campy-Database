import pandas as pd
import campyTM as ctm
import labTM as ltm
import cleanCSV as cn

def createAMRtriples(df,row,isoTitle):
    
    def mic_triple(mic_value, drug, test_title):

        mic = str(float(mic_value)) if cn.inNumber(mic_value) else str(mic_value)
        dm_title = '{}_{}'.format(mic, drug)
        
        triple = ltm.lab.indTriple(dm_title, 'DrugMIC') + \
                 ltm.lab.propTriple(dm_title, {'hasMIC': mic}, 'string', True) + \
                 ltm.lab.propTriple(dm_title, {'hasDrug': drug}) + \
                 ltm.lab.propTriple(test_title, {'foundMIC': dm_title})

        return triple
    
    def res_triple(res, drug, test_title):

        if int(res.lstrip('r')): # if resistant
	    out = ltm.lab.propTriple(test_title, {'foundResistanceTo': drug})
        else:
            out = ltm.lab.propTriple(test_title, {'foundSusceptibiltyTo': drug})
        return out

    df_row = df.loc[row]
    
    mic_indices = range(df.columns.get_loc('mic_azm', df.columns.get_loc('mic_tet') + 1)
    
    r_indices = range(df.columns.get_loc('razm'), df.columns.get_loc('rtet') + 1)

    drugs = [df.columns.values[d].replace('mic_', '') for d in mic_indices]

    amr = df_row['AMR']

    test_title = 'amr_' + isoTitle 

    # create MIC triples
    # NOTE: All mics are being stored as strings in the ontology as some of the mics have
    # < or > in them. We don't like this.
    mic_triples = [mic_triple(df_row[m], drug, test_title)
                   for m, drug in zip(mic_indices, drugs) 
                   if not pd.isnull(df_row[m])]
    
    # create resistance pattern triples
    res_triples = [res_triple(df_row[r], drug, test_title)
                   for r, drug in zip(r_indices, drugs)
                   if not pd.isnull(df_row[r])]

    if not pd.isnull(amr): # secondary source of resistance triples
        res_triples.append(ltm.lab.propTriple(test_title, {'foundResistanceTo': amr.split(' ')[0]})) 
    
    triples = mic_triples + res_triples # merge lists

    if triples: # if data were not empty add URIs, etc
        triples += [ltm.lab.indTriple(test_title,"AMRtest"),
		    ctm.campy.addUri(isoTitle) + " " + ctm.campy.addUri("hasLabTest") + \
		    " " + ltm.lab.addUri(test_title) + " ."]

    return ''.join(triples)
