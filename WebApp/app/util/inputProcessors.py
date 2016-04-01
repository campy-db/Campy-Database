
######################################################################################################
# getSourceSubject
# Takes the value from the source field from the AddForm, and splits it on spaces. Returns the first
# value that is an subj according to our subj list 'valid_vals'. Returns None if no subj is found.
######################################################################################################
def getSourceSubject(source, valid_vals):

	source = source.split(" ")
	
	subj = "".join(source) if len(source) == 1 else None

	if not subj:
		for s in source:
			if not subj:
				s = s.lower()
				subj = s if s in valid_vals else None

	else:
		subj = subj.lower()
		subj = subj if subj in valid_vals else None

	return subj

