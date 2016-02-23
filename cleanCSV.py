from dateutil.parser import parse as dateParse
import datetime

def isNumber(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

######################################################################################################
# Removes characters that screw things up from non-numberic values
######################################################################################################
def cleanString(s):
	if not isNumber(s):
		s=s.strip().lower()
		for c in ";: -.()+#":
			s=s.replace(c,'_')
	return s

######################################################################################################
# Some of the years and dates in the csv are stored as doubles for some reason
######################################################################################################
def cleanDate(s):
	result=""
	if s!="":
		result=str(int(float(s)))
	
	return result

######################################################################################################
# Converts date to a specified format. We'll be using ISO. 
##############################################################################################
def convertDate(d):
	try:
		if d!="":
			df="%Y-%m-%d"
			dt = dateParse(d)
			return (dt.strftime(df))
		else:
			return ""
	except ValueError:
		return ""

######################################################################################################
# Removes a prefix from val of length l
######################################################################################################
def remPrefix(val,l):
	if val!="":
		return val[l:]
	else:
		return ""
	


###################################################################################################
# Main. Just for testing purposes.
###################################################################################################
def main():
	print cleanDate("14.6875678")


if __name__=="__main__":
	main()