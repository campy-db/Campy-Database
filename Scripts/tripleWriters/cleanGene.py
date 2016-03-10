def cleanGene(g):
	g=g.replace("Oxford","")
	g=g.replace("MOMP peptide","MOMP")
	g=g.replace("fla peptide","flaPeptide")
	g=g.replace(" ","")

	return g	