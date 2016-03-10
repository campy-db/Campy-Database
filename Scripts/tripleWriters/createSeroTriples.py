import pandas as pd
import campyTM as ctm
import labTM as ltm

######################################################################################################
#
######################################################################################################
def createSeroTriples(df,row,isoTitle):
	sTriple=""
	sero=df["Serotype"][row]

	if not pd.isnull(sero):
		sTitle="sero_"+isoTitle
		sTriple+=ltm.lab.indTriple(sTitle,"SerotypeTest")
		sTriple+=ltm.lab.propTriple(sTitle,{"foundSerotype":sero},"string",True)
		sTriple+=ctm.campy.addUri(isoTitle)+" "+ctm.campy.addUri("hasLabTest")+" "+ltm.lab.addUri(sTitle)+" ."

	return sTriple