import pandas as pd
import campyTM as ctm
import labTM as ltm

######################################################################################################
#
######################################################################################################
def createSMAtriples(df,row,isoTitle):
	sTriple=""
	pulsovar=df["Pfge Sma I  / Pulsovar"][row]

	if not pd.isnull(pulsovar):
		sTitle="sma1_"+isoTitle
		sTriple+=ltm.lab.indTriple(sTitle,"SMA1")
		sTriple+=ltm.lab.propTriple(sTitle,{"foundPulsovar":pulsovar},"string",True)
		sTriple+=ctm.campy.addUri(isoTitle)+" "+ctm.campy.addUri("hasLabTest")+" "+ltm.lab.addUri(sTitle)+" ."

	return sTriple