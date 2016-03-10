import pandas as pd
import campyTM as ctm
import cleanCSV as cn

######################################################################################################
#
######################################################################################################
def createSpeciesTriples(df,row,isoTitle):
	isoTriple=""
	specA=""
	specB=""
	lethSpec=df["Campy Species (Leth - 16S, mapA, ceuE)"][row]
	altSpec=df["Alt. Speciation"][row]

	# lethSpec is the default species unless it is empty, equal to 'other campylobacter', or just some
	# invalid value. In this case alt spec becomes the species, granted it has a valid value. 
	# Sometimes the species are mixed (of the form 'Mixed (coli and jejuni)') in which case 
	# specA="coli" and specB="jejuni". But sometimes it will just say 'Mixed' in lethSpec but 'Coli' 
	# in altSpec. In such a case specA="coli" and specB remains empty

	lethIsValid=not pd.isnull(lethSpec) and cn.isGoodVal(lethSpec) and\
			    not cn.compare([lethSpec,"dead"])
	altIsValid=not pd.isnull(altSpec) and cn.isGoodVal(altSpec) and not cn.compare([altSpec,"dead"])

	lethIsOther=cn.compare([lethSpec,"other campylobacter"])
	altIsOther=cn.compare([altSpec,"other campylobacter"])

	isMixed=cn.compare(["mixed (coli and jejuni)",lethSpec]) or\
		    cn.compare(["mixed (coli and jejuni)",altSpec])


	if lethIsValid and not lethIsOther:
		if cn.compare(["no 16s/lari",lethSpec]):
			specs=lethSpec.split("/")
			specA=specs[0]
			specB=specs[1]
		else:
			specA=lethSpec

		# If both are non-empty, we have to check if one is mixed and the other is coli
		if altIsValid and not altIsOther:

			if cn.compare(["mixed",lethSpec]) and cn.compare(["coli",altSpec]):
				specA="coli"
		
	else:
		if altIsValid and not altIsOther:
			specA=altSpec

	if isMixed:
		specA="coli"
		specB="jejuni"

	if specA!="":
		specA=specA.lower() # Some are no_16 and others are No_16
		isoTriple+=ctm.campy.indTriple(specA,"CampySpecies")+\
				   ctm.campy.propTriple(specA,{"hasName":specA},"string")
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasSpecies":specA})

	if specB!="":
		specB=specB.lower() # Ditto
		isoTriple+=ctm.campy.indTriple(specB,"CampySpecies")+\
			       ctm.campy.propTriple(specB,{"hasName":specB},"string")
		isoTriple+=ctm.campy.propTriple(isoTitle,{"hasSpecies":specB})

	return isoTriple