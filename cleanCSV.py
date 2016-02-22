from dateutil.parser import parse as dateParse
import datetime
######################################################################################################
# Removes characters that screw things up
######################################################################################################
def cleanString(s):
	s=s.strip().lower()
	for c in ";: -.()+#":
		s=s.replace(c,'_')
	return s

######################################################################################################
# Converts date to a specified format. We'll be using ISO. 
######################################################################################################
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
	print type(datetime.datetime.today())


if __name__=="__main__":
	main()